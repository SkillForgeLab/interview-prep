import java.math.BigDecimal;

public class FeeStrategyDemo {
    public static void main(String[] args) {
        Payment payment = new Payment(new BigDecimal("200.00"), true);
        check("1.50", new Processor(new FixedFee()).fee(payment));
        check("2.0000", new Processor(new PercentageFee()).fee(payment));
        System.out.println("PASS: policy varies without changing processor");
    }

    private static void check(String expected, BigDecimal actual) {
        if (new BigDecimal(expected).compareTo(actual) != 0)
            throw new AssertionError("expected " + expected + ", got " + actual);
    }

    interface FeePolicy {
        BigDecimal calculate(Payment p);
    }

    record Payment(BigDecimal amount, boolean international) {
    }

    static final class FixedFee implements FeePolicy {
        public BigDecimal calculate(Payment p) {
            return new BigDecimal("1.50");
        }
    }

    static final class PercentageFee implements FeePolicy {
        public BigDecimal calculate(Payment p) {
            return p.amount().multiply(new BigDecimal("0.01"));
        }
    }

    static final class Processor {
        private final FeePolicy policy;

        Processor(FeePolicy policy) {
            this.policy = policy;
        }

        BigDecimal fee(Payment payment) {
            return policy.calculate(payment);
        }
    }
}
