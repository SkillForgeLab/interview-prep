import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class IdempotencyToyDemo {
    public static void main(String[] args) {
        AcceptanceService svc = new AcceptanceService();
        int first = svc.accept("A", "k1", "amount=100");
        int repeated = svc.accept("A", "k1", "amount=100");
        if (first != repeated) throw new AssertionError("Duplicate created");
        try {
            svc.accept("A", "k1", "amount=200");
            throw new AssertionError("Conflict not detected");
        } catch (IllegalArgumentException expected) { /* correct */ }
        if (svc.accept("B", "k1", "amount=100") == first)
            throw new AssertionError("Tenant key not scoped");
        System.out.println("PASS: same key/payload returns ID; conflict rejected");
    }

    record Key(String tenant, String key) {
    }

    record Entry(String payload, int instructionId) {
    }

    static final class AcceptanceService {
        private final ConcurrentHashMap<Key, Entry> records =
                new ConcurrentHashMap<>();
        private final AtomicInteger nextId = new AtomicInteger();

        int accept(String tenant, String key, String payload) {
            Key scoped = new Key(tenant, key);
            Entry entry = records.compute(scoped, (k, old) -> {
                if (old == null) return new Entry(payload, nextId.incrementAndGet());
                if (!old.payload().equals(payload))
                    throw new IllegalArgumentException("Idempotency conflict");
                return old;
            });
            return entry.instructionId();
        }
    }
}
