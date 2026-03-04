import pytest
from .factories import (
    UserFactory,
    AdminUserFactory,
    CategoryFactory,
    ProductFactory,
    StockMovementFactory,
    SupplierFactory,
)


# inventory fixtures
@pytest.fixture
def category(db):
    return CategoryFactory()


@pytest.fixture
def product(db):
    return ProductFactory()


@pytest.fixture
def supplier(db):
    return SupplierFactory()


@pytest.fixture
def low_stock_product(db):
    return ProductFactory(low_stock=True)


@pytest.fixture
def out_of_stock_product(db):
    return ProductFactory(out_of_stock=True)


@pytest.fixture
def stock_movement(db):
    return StockMovementFactory()


@pytest.fixture
def stock_in(db):
    return StockMovementFactory(stock_in=True)


@pytest.fixture
def stock_out(db):
    return StockMovementFactory(stock_out=True)


# payloads
@pytest.fixture
def category_payload():
    obj = CategoryFactory.build()
    return {"name": obj.name, "description": obj.description}


@pytest.fixture
def supplier_payload():
    obj = SupplierFactory.build()
    return {
        "name": obj.name,
        "email": obj.email,
        "phone": obj.phone,
        "address": obj.address,
    }


@pytest.fixture
def product_payload(db):
    category = CategoryFactory()
    supplier = SupplierFactory()
    obj = ProductFactory.build(category=category, supplier=supplier)
    return {
        "name": obj.name,
        "sku": obj.sku,
        "description": obj.description,
        "category": str(category.id),
        "supplier": str(supplier.id),
        "cost_price": str(obj.cost_price),
        "selling_price": str(obj.selling_price),
        "stock_quantity": obj.stock_quantity,
        "low_stock_limit": obj.low_stock_limit,
    }
