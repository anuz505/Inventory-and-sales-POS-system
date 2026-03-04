from decimal import Decimal

from rest_framework.exceptions import ValidationError
import pytest
from inventory.tests.factories import ProductFactory
from sales.serializers import CustomerSerialzer, SalesItemSerializer, SalesSerializer
from sales.models import Customer, Sales, SalesItem

from .factories import CustomerFactory, SalesFactory, SalesItemFactory


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


class TestSalesItemSerializer:
    def test_serialize_item(self, product, pending_sale):
        item = SalesItemFactory(
            sale=pending_sale,
            product=product,
            quantity=2,
            unit_price=Decimal("50.00"),
            subtotal=Decimal("100.00"),
        )
        serializer = SalesItemSerializer(item)
        data = serializer.data
        assert data["quantity"] == 2
        assert data["product_name"] == product.name
        assert Decimal(data["unit_price"]) == product.selling_price

    def test_product_name_is_read_only(self, product, pending_sale):
        item = SalesItemFactory(sale=pending_sale, product=product)
        serializer = SalesItemSerializer(item)
        assert "product_name" in serializer.data


class TestSalesSerializerCreate:
    def test_create_pending_sale_does_not_deduct_stock(self, user, customer, product):
        initial_stock = product.stock_quantity
        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "0.00",
            "items": [
                {"product": product.id, "quantity": 2, "discount_amount": "0.00"}
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        sale = serializer.save(user=user)
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock  # No deduction for pending

    def test_create_completed_sale_deducts_stock(self, user, customer, product):
        initial_stock = product.stock_quantity
        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "completed",
            "discount_amount": "0.00",
            "items": [
                {"product": product.id, "quantity": 3, "discount_amount": "0.00"}
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        sale = serializer.save(user=user)
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 3

    def test_create_sale_calculates_subtotal_and_total(self, user, customer, product):
        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "10.00",
            "items": [
                {"product": product.id, "quantity": 2, "discount_amount": "0.00"}
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        sale = serializer.save(user=user)
        expected_subtotal = product.selling_price * 2
        assert sale.subtotal == expected_subtotal
        assert sale.total_amount == expected_subtotal - Decimal("10.00")

    def test_create_sale_generates_invoice_number(self, user, customer, product):
        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "0.00",
            "items": [
                {"product": product.id, "quantity": 1, "discount_amount": "0.00"}
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        sale = serializer.save(user=user)
        assert sale.invoice_number.startswith("INV-")
        assert len(sale.invoice_number) == 12  # "INV-" + 8 hex chars

    def test_create_sale_insufficient_stock_raises(
        self, user, customer, out_of_stock_product
    ):
        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "0.00",
            "items": [
                {
                    "product": out_of_stock_product.id,
                    "quantity": 5,
                    "discount_amount": "0.00",
                }
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(ValidationError) as exc:
            serializer.save(user=user)
        assert "Insufficient stock" in str(exc.value)

    def test_create_sale_creates_stock_movement_when_completed(
        self, user, customer, product
    ):
        from inventory.models import StockMovement

        data = {
            "customer": customer.id,
            "payment_method": "cash",
            "payment_status": "completed",
            "discount_amount": "0.00",
            "items": [
                {"product": product.id, "quantity": 2, "discount_amount": "0.00"}
            ],
        }
        serializer = SalesSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        sale = serializer.save(user=user)
        movements = StockMovement.objects.filter(sales=sale, movement_type="OUT")
        assert movements.count() == 1
        assert movements.first().quantity == 2


class TestSalesSerializerUpdate:
    def test_update_pending_to_completed_deducts_stock(
        self, user, sale_with_item, product
    ):
        from inventory.models import StockMovement

        initial_stock = product.stock_quantity
        serializer = SalesSerializer(
            instance=sale_with_item,
            data={"payment_status": "completed"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save(user=user)
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 2
        assert StockMovement.objects.filter(
            sales=sale_with_item, movement_type="OUT"
        ).exists()

    def test_update_completed_to_refunded_restores_stock(self, user, customer, product):
        from inventory.models import StockMovement

        # Build a completed sale with an item
        sale = SalesFactory(
            user=user,
            customer=customer,
            payment_status="completed",
            subtotal=Decimal("100.00"),
            total_amount=Decimal("100.00"),
        )
        SalesItemFactory(
            sale=sale,
            product=product,
            quantity=2,
            unit_price=Decimal("50.00"),
            subtotal=Decimal("100.00"),
        )
        product.stock_quantity = 98  # Simulate stock already deducted
        product.save()

        serializer = SalesSerializer(
            instance=sale, data={"payment_status": "refunded"}, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save(user=user)
        product.refresh_from_db()
        assert product.stock_quantity == 100  # Restored
        assert StockMovement.objects.filter(sales=sale, movement_type="IN").exists()

    def test_update_refunded_sale_raises(self, user, refunded_sale):
        serializer = SalesSerializer(
            instance=refunded_sale,
            data={"notes": "Trying to edit refunded"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(ValidationError) as exc:
            serializer.save(user=user)
        assert "Refunded sales cannot be modified" in str(exc.value)

    def test_update_completed_sale_non_refund_change_raises(self, user, completed_sale):
        serializer = SalesSerializer(
            instance=completed_sale,
            data={"notes": "changing notes on completed"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(ValidationError) as exc:
            serializer.save(user=user)
        assert "Completed sales can only be converted to refunded" in str(exc.value)

    def test_update_pending_sale_items(self, user, sale_with_item, product):
        new_product = ProductFactory(
            stock_quantity=50, selling_price=Decimal("30.00"), low_stock_limit=5
        )
        serializer = SalesSerializer(
            instance=sale_with_item,
            data={
                "payment_status": "pending",
                "items": [
                    {
                        "product": new_product.id,
                        "quantity": 3,
                        "discount_amount": "0.00",
                    }
                ],
            },
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        updated_sale = serializer.save(user=user)
        assert updated_sale.subtotal == Decimal("90.00")  # 3 * 30.00
        assert updated_sale.items.count() == 1
        assert updated_sale.items.first().product == new_product

    def test_update_discount_exceeding_subtotal_raises(self, user, sale_with_item):
        serializer = SalesSerializer(
            instance=sale_with_item,
            data={"discount_amount": "9999.00"},
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        with pytest.raises(ValidationError) as exc:
            serializer.save(user=user)
        assert "Discount" in str(exc.value) and "subtotal" in str(exc.value)
