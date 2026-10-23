```java
interface PaymentGateway {
    Receipt charge(Payment payment);
}

class BankAGateway implements PaymentGateway {
    private final BankAClient bankAClient;

    BankAGateway(BankAClient bankAClient) {
        this.bankAClient = bankAClient;
    }

    public Receipt charge(Payment payment) {
        BankAResponse response =
                bankAClient.submitCharge(payment.getAmount());

        return new Receipt(response.getReference());
    }
}

// New provider: add this class
class BankBGateway implements PaymentGateway {
    private final BankBClient bankBClient;

    BankAGateway(BankBClient bankBClient) {
        this.bankAClient = bankBClient;
    }

    public Receipt charge(Payment payment) {
        BankBResponse response =
                bankBClient.submitCharge(payment.getAmount());

        return new Receipt(response.getReference());
    }
}

class PaymentService {
    private final PaymentGateway gateway;

    PaymentService(PaymentGateway gateway) {
        this.gateway = gateway;
    }

    Receipt process(Payment payment) {
        return gateway.charge(payment);
    }
}
```

When setting up the application, choose the implementation:

```java
PaymentService service =
        new PaymentService(new BankBGateway());
```

In a real application, the gateway would also receive its API client and configuration. The important point is that
PaymentService.process () does not acquire a new if (provider == BANK_B) branch.

For this to work safely, BankBGateway must honor the same contract as BankAGateway: what counts as a successful charge,
how failures are reported, and how retries or duplicate requests are handled. That is where Liskov connects to this
example.

Here, BankAClient is the type; bankAClient is the object held by the gateway. BankBClient could have different method
names and response fields. Each gateway hides those differences, so PaymentService only needs to know the common
PaymentGateway contract.

