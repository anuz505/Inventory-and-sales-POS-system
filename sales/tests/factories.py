import factory
import factory.fuzzy
from decimal import Decimal
from sales.models import Sales, SalesItem, Customer
from factory.django import DjangoModelFactory


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    name = factory.Faker("name")
    email = factory.Faker("email")
    phone_number = factory.Faker("numerify", text="+1##########")
    address = factory.Faker("address")
