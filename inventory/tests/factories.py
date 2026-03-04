import factory
import factory.fuzzy
from decimal import Decimal
from factory.django import DjangoModelFactory
from inventory.models import Product, Supplier, Category, StockMovement
from users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = factory.fuzzy.FuzzyChoice(["admin", "staff", "manager"])
    phone_number = factory.Faker("numerify", text="+1##########")


class AdminUserFactory(UserFactory):
    username = factory.Sequence(lambda n: f"admin_{n}")
    is_staff = True
    is_superuser = True


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    description = factory.Faker("sentence")


class SupplierFactory(DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Faker("company")
    email = factory.Faker("company_email")
    phone = factory.fuzzy.FuzzyInteger(1000000000, 9999999999)
    address = factory.Faker("address")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker("catch_phrase")
    sku = factory.Sequence(lambda n: f"SKU-{n:05d}")
    description = factory.Faker("paragraph")
    category = factory.SubFactory(CategoryFactory)
    supplier = factory.SubFactory(SupplierFactory)
    cost_price = factory.fuzzy.FuzzyDecimal(10.00, 500.00, precision=2)
    selling_price = factory.LazyAttribute(
        lambda o: o.cost_price
        + Decimal(str(round(__import__("random").uniform(0, 500), 2)))
    )
    stock_quantity = factory.fuzzy.FuzzyInteger(0, 500)
    low_stock_limit = factory.fuzzy.FuzzyInteger(5, 50)

    class Params:
        low_stock = factory.Trait(stock_quantity=2, low_stock_limit=10)
        out_of_stock = factory.Trait(stock_quantity=0)


class StockMovementFactory(DjangoModelFactory):
    class Meta:
        model = StockMovement

    product = factory.SubFactory(ProductFactory)
    quantity = factory.fuzzy.FuzzyInteger(1, 100)
    movement_type = factory.fuzzy.FuzzyChoice(["IN", "OUT"])
    reason = factory.fuzzy.FuzzyChoice(
        ["SALE", "PURCHASE", "RETURN", "MANUAL", "DAMAGED"]
    )
    user = factory.SubFactory(UserFactory)
    notes = factory.Faker("sentence")

    class Params:
        stock_in = factory.Trait(movement_type="IN", reason="PURCHASE")
        stock_out = factory.Trait(movement_type="OUT", reason="SALE")
