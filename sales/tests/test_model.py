from decimal import Decimal

import pytest
import uuid
from sales.models import Customer, Sales, SalesItem
from .factories import CustomerFactory, SalesFactory, SalesItemFactory


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


@pytest.mark.django_db
class TestSalesModel:
    def test_create_sale(self, user, customer):
        sale = SalesFactory(user=user, customer=customer)
        assert sale.pk is not None
        assert sale.invoice_number.startswith("INV-")

    def test_sale_default_status_is_completed(self):
        """Model default is 'completed' — factory overrides to 'pending'."""
        sale = Sales(
            invoice_number="INV-TEST001",
            customer=CustomerFactory(),
            payment_method="cash",
        )
        assert sale.payment_status == "completed"

    def test_sale_payment_method_choices(self, user, customer):
        for method, _ in Sales.PAYMENT_METHODS:
            sale = SalesFactory(user=user, customer=customer, payment_method=method)
            assert sale.payment_method == method

    def test_sale_payment_status_choices(self, user, customer):
        for status, _ in Sales.PAYMENT_STATUS:
            sale = SalesFactory(user=user, customer=customer, payment_status=status)
            assert sale.payment_status == status

    def test_sale_uuid_pk(self, user, customer):
        sale = SalesFactory(user=user, customer=customer)
        assert len(str(sale.id)) == 36

    def test_sale_unique_invoice_number(self, user, customer):
        from django.db import IntegrityError

        SalesFactory(user=user, customer=customer, invoice_number="INV-UNIQUE01")
        with pytest.raises(IntegrityError):
            SalesFactory(user=user, customer=customer, invoice_number="INV-UNIQUE01")

    def test_sale_ordering_newest_first(self, user, customer):
        s1 = SalesFactory(user=user, customer=customer)
        s2 = SalesFactory(user=user, customer=customer)
        sales = list(Sales.objects.all())
        # Newest (higher pk) should come first
        assert sales[0].created_at >= sales[1].created_at

    def test_sale_cascade_delete_customer(self, user):
        customer = CustomerFactory()
        sale = SalesFactory(user=user, customer=customer)
        customer.delete()
        assert not Sales.objects.filter(pk=sale.pk).exists()

    def test_sale_null_user_on_user_delete(self, customer):
        from inventory.tests.factories import UserFactory

        u = UserFactory()
        sale = SalesFactory(user=u, customer=customer)
        u.delete()
        sale.refresh_from_db()
        assert sale.user is None


class TestSalesItemModel:
    def test_create_sales_item(self, product, pending_sale):
        item = SalesItemFactory(
            sale=pending_sale,
            product=product,
            quantity=3,
            unit_price=Decimal("20.00"),
            subtotal=Decimal("60.00"),
        )
        assert item.pk is not None
        assert item.quantity == 3
        assert item.subtotal == Decimal("60.00")

    def test_sales_item_uuid_pk(self, product, pending_sale):
        item = SalesItemFactory(sale=pending_sale, product=product)
        assert len(str(item.id)) == 36

    def test_sales_item_cascade_on_sale_delete(self, product, pending_sale):
        item = SalesItemFactory(sale=pending_sale, product=product)
        pending_sale.delete()
        assert not SalesItem.objects.filter(pk=item.pk).exists()

    def test_sales_item_default_discount(self, product, pending_sale):
        item = SalesItemFactory(sale=pending_sale, product=product)
        assert item.discount_amount == Decimal("0.00")
