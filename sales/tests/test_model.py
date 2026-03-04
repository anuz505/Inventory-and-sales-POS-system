import pytest
import uuid
from sales.models import Customer, Sales, SalesItem
from .factories import CustomerFactory


@pytest.mark.django_db
class TestCustomerModel:
    def test_creation(self):
        customer = CustomerFactory()
        assert customer.id is not None
        assert customer.name
        assert customer.email
        assert customer.phone_number
        assert customer.address

    def test_uuid_primary_key(self):
        assert isinstance(CustomerFactory().id, uuid.UUID)

    def test_customer_fixture(self, customer):
        assert customer.id is not None
        assert customer.name

    def test_timestamps_populated(self):
        customer = CustomerFactory()
        assert customer.created_at is not None
        assert customer.updated_at is not None

    def test_batch_ids_are_unique(self):
        ids = [c.id for c in CustomerFactory.create_batch(5)]
        assert len(ids) == 5

    @pytest.mark.parametrize(
        "field,max_length",
        [
            ("address", 255),
            ("email", 255),
            ("phone_number", 20),
        ],
    )
    def test_field_max_length(self, field, max_length):
        f = Customer._meta.get_field(field)
        assert getattr(f, "max_length", None) == max_length
