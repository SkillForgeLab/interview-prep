public class PaymentStateDemo {
    public static void main(String[] args) {
        Payment p = new Payment();
        expectFailure(p::settle); // settlement cannot skip authorization
        p.authorize();
        p.settle();
        if (p.status() != Status.SETTLED) throw new AssertionError();
        expectFailure(p::authorize); // cannot move backward
        System.out.println("PASS: valid transitions only");
    }

    private static void expectFailure(Runnable operation) {
        try {
            operation.run();
        } catch (IllegalStateException expected) {
            return;
        }
        throw new AssertionError("Expected invalid transition to fail");
    }

    enum Status {CREATED, AUTHORIZED, SETTLED}

    static final class Payment {
        private Status status = Status.CREATED;

        Status status() {
            return status;
        }

        void authorize() {
            require(Status.CREATED);
            status = Status.AUTHORIZED;
        }

        void settle() {
            require(Status.AUTHORIZED);
            status = Status.SETTLED;
        }

        private void require(Status expected) {
            if (status != expected)
                throw new IllegalStateException("Expected " + expected + ", was " + status);
        }
    }
}
