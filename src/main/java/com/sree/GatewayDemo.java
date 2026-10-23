package com.sree;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 *
 * The flow is PaymentService → PaymentGateway → bank-specific gateway → bank client.
 * PaymentService knows only the common interface.
 * Each gateway translates your application’s Payment into the format its bank client expects.
 * Adding Bank B required a new gateway and client, plus a change to the setup in main;
 * the processing logic stayed the same.
 *
 * Run it with javac GatewayDemo.java and then java GatewayDemo.
 */
public class GatewayDemo {

    static class Payment {
        final BigDecimal amount;

        Payment(String amount) {
            this.amount = new BigDecimal(amount)
                    .setScale(2, RoundingMode.UNNECESSARY);

            if (this.amount.signum() <= 0) {
                throw new IllegalArgumentException("Amount must be positive");
            }
        }
    }

    static class Receipt {
        final String reference;

        Receipt(String reference) {
            this.reference = reference;
        }
    }

    // The contract used by our business code.
    interface PaymentGateway {
        Receipt charge(Payment payment);
    }

    // Bank A's API has its own response type.
    static class BankAResponse {
        final String transactionId;

        BankAResponse(String transactionId) {
            this.transactionId = transactionId;
        }
    }

    static class BankAClient {
        BankAResponse submitPayment(BigDecimal amount) {
            System.out.println("Bank A received $" + amount);
            return new BankAResponse("A-1001");
        }
    }

    // Bank B's API accepts cents and returns a String.
    static class BankBClient {
        String createCharge(long amountInCents) {
            System.out.println("Bank B received " + amountInCents + " cents");
            return "B-2001";
        }
    }

    // Adapter for Bank A.
    static class BankAGateway implements PaymentGateway {
        private final BankAClient client;

        BankAGateway(BankAClient client) {
            this.client = client;
        }

        public Receipt charge(Payment payment) {
            BankAResponse response =
                    client.submitPayment(payment.amount);
            return new Receipt(response.transactionId);
        }
    }

    // New adapter for Bank B.
    static class BankBGateway implements PaymentGateway {
        private final BankBClient client;

        BankBGateway(BankBClient client) {
            this.client = client;
        }

        public Receipt charge(Payment payment) {
            long cents = payment.amount
                    .movePointRight(2)
                    .longValueExact();

            String reference = client.createCharge(cents);
            return new Receipt(reference);
        }
    }

    // This class works with either bank. We do not edit it to add Bank B.
    static class PaymentService {
        private final PaymentGateway gateway;

        PaymentService(PaymentGateway gateway) {
            this.gateway = gateway;
        }

        Receipt process(Payment payment) {
            return gateway.charge(payment);
        }
    }

    public static void main(String[] args) {
        PaymentService bankAService =
                new PaymentService(
                        new BankAGateway(new BankAClient()));

        Receipt first = bankAService.process(new Payment("10.50"));
        System.out.println("Receipt: " + first.reference);

        PaymentService bankBService =
                new PaymentService(
                        new BankBGateway(new BankBClient()));

        Receipt second = bankBService.process(new Payment("7.25"));
        System.out.println("Receipt: " + second.reference);
    }
}