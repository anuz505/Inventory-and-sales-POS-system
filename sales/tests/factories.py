import factory
import factory.fuzzy
from decimal import Decimal

from faker import Faker
from django.utils import timezone
from sales.models import Sales, SalesItem, Customer
from factory.django import DjangoModelFactory

fake = Faker()


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    name = factory.Faker("name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="+1##########")
    address = factory.Faker("address")


class SalesFactory(DjangoModelFactory):
    class Meta:
        model = Sales

    invoice_number = factory.LazyAttribute(
        lambda _: f"INV-{fake.unique.hexify(text='^^^^^^^^').upper()}"
    )
    customer = factory.SubFactory(CustomerFactory)
    user = None  # Set via fixture
    subtotal = factory.LazyAttribute(lambda _: Decimal("100.00"))
    discount_amount = factory.LazyAttribute(lambda _: Decimal("0.00"))
    total_amount = factory.LazyAttribute(lambda _: Decimal("100.00"))
    payment_method = "cash"
    payment_status = "pending"
    notes = factory.LazyAttribute(lambda _: fake.sentence())
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class CompletedSalesFactory(SalesFactory):
    payment_status = "completed"


class RefundedSalesFactory(SalesFactory):
    payment_status = "refunded"


class SalesItemFactory(DjangoModelFactory):
    class Meta:
        model = SalesItem

    sale = factory.SubFactory(SalesFactory)
    product = None  # Set via fixture
    quantity = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=10))
    unit_price = factory.LazyAttribute(
        lambda _: Decimal(str(round(fake.random_number(digits=3) / 10, 2)))
    )
    discount_amount = Decimal("0.00")
    subtotal = factory.LazyAttribute(lambda obj: obj.unit_price * obj.quantity)
    created_at = factory.LazyFunction(timezone.now)
