import pytest
from sales.serializers import CustomerSerialzer, SalesItemSerializer, SalesSerializer
from sales.models import Customer, Sales, SalesItem

from .factories import CustomerFactory


@pytest.mark.django_db
class TestCustomerSerializer:
    def test_serializers_correct_fields(self):
        data = CustomerSerialzer(CustomerFactory()).data
        assert set(data.keys()) == {
            "id",
            "name",
            "email",
            "phone_number",
            "address",
            "created_at",
            "updated_at",
        }

    def test_id_matches_instance(self):
        customer = CustomerFactory()
        assert CustomerSerialzer(customer).data["id"] == str(customer.id)

    @pytest.mark.parametrize(
        "field",
        ["id", "name", "email", "phone_number", "address", "created_at", "updated_at"],
    )
    def test_field_present_in_output(self, field):
        assert field in CustomerSerialzer(CustomerFactory()).data

    def test_read_only_fields_not_writable(self):
        """id, created_at, updated_at should be ignored on input."""
        import uuid
        from datetime import datetime

        payload = {
            "id": str(uuid.uuid4()),
            "name": "Alice",
            "email": "alice@example.com",
            "phone_number": "+1234567890",
            "address": "123 Main St",
            "created_at": "2000-01-01T00:00:00Z",
            "updated_at": "2000-01-01T00:00:00Z",
        }
        s = CustomerSerialzer(data=payload)
        assert s.is_valid(), s.errors
        instance = s.save()
        assert instance.id != uuid.UUID(payload["id"])

    def test_valid_data_saves_customer(self):
        payload = {
            "name": "Bob",
            "email": "bob@example.com",
            "phone_number": "+9876543210",
            "address": "456 Elm St",
        }
        s = CustomerSerialzer(data=payload)
        assert s.is_valid(), s.errors
        instance = s.save()
        assert instance.pk is not None
        assert instance.name == "Bob"

    def test_missing_required_field_is_invalid(self):
        """Omitting 'name' should fail validation."""
        payload = {
            "email": "test@example.com",
            "phone_number": "+1234567890",
            "address": "789 Oak Ave",
        }
        s = CustomerSerialzer(data=payload)
        assert not s.is_valid()
        assert "name" in s.errors

    def test_invalid_email_is_rejected(self):
        payload = {
            "name": "Carol",
            "email": "not-an-email",
            "phone_number": "+1234567890",
            "address": "321 Pine Rd",
        }
        s = CustomerSerialzer(data=payload)
        assert not s.is_valid()
        assert "email" in s.errors

    def test_partial_update(self):
        """PATCH semantics: only provided fields are updated."""
        customer = CustomerFactory()
        original_email = customer.email
        s = CustomerSerialzer(customer, data={"name": "Updated Name"}, partial=True)
        assert s.is_valid(), s.errors
        updated = s.save()
        assert updated.name == "Updated Name"
        assert updated.email == original_email

    def test_id_is_uuid_string_in_output(self):
        import uuid

        customer = CustomerFactory()
        data = CustomerSerialzer(customer).data
        uuid.UUID(data["id"])
