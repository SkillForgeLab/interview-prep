"""M03 L35: deterministic SQLite lab demonstrating a lost update and a version guard.

Educational only. Runs locally using Python's standard library. It does not send
financial instructions, test real parallel load, or prove a production design.

Usage: python M03_lost_update_lab.py
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3


def connect(db_path: Path) -> sqlite3.Connection:
    # Each SQL statement is committed separately to create an explicit interleaving.
    return sqlite3.connect(str(db_path), isolation_level=None, timeout=5)


def read_balance(conn: sqlite3.Connection) -> tuple[int, int]:
    row = conn.execute(
        "SELECT amount_minor, version FROM balances WHERE account_id = ?",
        ("A",),
    ).fetchone()
    assert row is not None
    return int(row[0]), int(row[1])


def reset(conn: sqlite3.Connection) -> None:
    conn.execute("UPDATE balances SET amount_minor = 100, version = 4 WHERE account_id = 'A'")


def guarded_debit(conn: sqlite3.Connection, amount: int, expected_version: int) -> int:
    """Return 1 for successful guarded write; 0 for conflict/invalid condition."""
    return conn.execute(
        """UPDATE balances
           SET amount_minor = amount_minor - ?, version = version + 1
           WHERE account_id = ? AND version = ? AND amount_minor >= ?""",
        (amount, "A", expected_version, amount),
    ).rowcount


def run_lab() -> None:
    with TemporaryDirectory(prefix="m03_lab_") as folder:
        db_path = Path(folder) / "example.sqlite"
        with connect(db_path) as setup:
            setup.execute(
                """CREATE TABLE balances (
                    account_id TEXT PRIMARY KEY,
                    amount_minor INTEGER NOT NULL CHECK (amount_minor >= 0),
                    version INTEGER NOT NULL
                )"""
            )
            setup.execute("INSERT INTO balances VALUES ('A', 100, 4)")

        a = connect(db_path)
        b = connect(db_path)
        try:
            print("PART 1 — Bad read/modify/write based on old values")
            a_value, _ = read_balance(a)
            b_value, _ = read_balance(b)
            print(f"A read {a_value}; B read {b_value}")
            a.execute(
                "UPDATE balances SET amount_minor = ? WHERE account_id = ?",
                (a_value - 10, "A"),
            )
            print("A wrote 90")
            b.execute(
                "UPDATE balances SET amount_minor = ? WHERE account_id = ?",
                (b_value - 20, "A"),
            )
            flawed, _ = read_balance(a)
            print(f"B wrote 80 from stale read. Stored balance: {flawed} (WRONG)")
            assert flawed == 80

            print("\nPART 2 — Guard the write with a database version")
            reset(a)
            a_value, a_version = read_balance(a)
            b_value, b_version = read_balance(b)
            print(f"A read {a_value}/v{a_version}; B read {b_value}/v{b_version}")
            a_rows = guarded_debit(a, 10, a_version)
            b_rows = guarded_debit(b, 20, b_version)
            assert a_rows == 1 and b_rows == 0
            print(f"A affected {a_rows} row; stale B affected {b_rows} rows (CONFLICT)")

            # A real workflow must revalidate full business rules, not just subtract again.
            latest_balance, latest_version = read_balance(b)
            print(f"B rereads {latest_balance}/v{latest_version} and rechecks conditions")
            retry_rows = guarded_debit(b, 20, latest_version)
            final, version = read_balance(a)
            print(f"B guarded retry affected {retry_rows} row. Final: {final}/v{version} (CORRECT)")
            assert retry_rows == 1 and (final, version) == (70, 6)

            print("\nLesson: A stale writer must not silently overwrite another change.")
        finally:
            a.close()
            b.close()


if __name__ == "__main__":
    run_lab()
