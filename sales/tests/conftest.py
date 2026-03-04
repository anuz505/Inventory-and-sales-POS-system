import pytest
from decimal import Decimal
from .factories import (
    CustomerFactory,
    RefundedSalesFactory,
    SalesFactory,
    SalesItemFactory,
    CompletedSalesFactory,
)
from inventory.tests.factories import ProductFactory

# customer fixtures


@pytest.fixture
def customer(db):
    return CustomerFactory()


# product fixtures


@pytest.fixture
def product(db):
    return ProductFactory(
        stock_quantity=100,
        selling_price=Decimal("50.00"),
        low_stock_limit=5,
    )


@pytest.fixture
def out_of_stock_product(db):
    return ProductFactory(stock_quantity=0, low_stock_limit=5)


# ─── Sales ────────────────────────────────────────────────────────────────────


@pytest.fixture
def pending_sale(db, user, customer):
    return SalesFactory(
        user=user,
        customer=customer,
        payment_status="pending",
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )


@pytest.fixture
def completed_sale(db, user, customer):
    return CompletedSalesFactory(
        user=user,
        customer=customer,
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )


@pytest.fixture
def refunded_sale(db, user, customer):
    return RefundedSalesFactory(
        user=user,
        customer=customer,
        subtotal=Decimal("100.00"),
        total_amount=Decimal("100.00"),
    )


@pytest.fixture
def sale_with_item(db, user, customer, product):
    sale = SalesFactory(
        user=user,
        customer=customer,
        payment_status="pending",
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
    return sale


# ─── Payload helpers ─────────────────────────────────────────────────────────


@pytest.fixture
def sale_payload(customer, product):
    """Valid payload for creating a new sale via the API."""
    return {
        "customer": str(customer.id),
        "payment_method": "cash",
        "payment_status": "pending",
        "discount_amount": "0.00",
        "notes": "Test sale",
        "items": [
            {
                "product": str(product.id),
                "quantity": 2,
                "discount_amount": "0.00",
            }
        ],
    }
