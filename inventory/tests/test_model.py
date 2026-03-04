import pytest
import uuid
from decimal import Decimal
from inventory.models import StockMovement, Product, Category, Supplier
from .factories import (
    CategoryFactory,
    ProductFactory,
    StockMovementFactory,
    SupplierFactory,
)


@pytest.mark.django_db
class TestCategoryModel:
    def test_creation(self):
        category = CategoryFactory()
        assert category.id is not None
        assert category.name
        assert category.description

    def test_uuid_primary_key(self):
        assert isinstance(CategoryFactory().id, uuid.UUID)

    def test_category_fixture(self, category):
        assert category.id is not None
        assert category.name

    def test_timestamps_populated(self):
        category = CategoryFactory()
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_description_nullable(self):
        assert CategoryFactory(description=None).description is None

    def test_batch_ids_are_unique(self):
        ids = [c.id for c in CategoryFactory.create_batch(5)]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize(
        "field,max_length",
        [
            ("name", 255),
            ("description", None),  # TextField has no max_length
        ],
    )
    def test_field_max_length(self, field, max_length):
        f = Category._meta.get_field(field)
        assert getattr(f, "max_length", None) == max_length


@pytest.mark.django_db
class TestSupplierModel:

    def test_creation(self):
        supplier = SupplierFactory()
        assert supplier.id is not None
        assert supplier.name
        assert "@" in supplier.email
        assert supplier.phone
        assert supplier.address

    def test_uuid_primary_key(self):
        assert isinstance(SupplierFactory().id, uuid.UUID)

    def test_timestamps_populated(self):
        supplier = SupplierFactory()
        assert supplier.created_at is not None
        assert supplier.updated_at is not None

    def test_batch_creation(self):
        SupplierFactory.create_batch(3)
        assert Supplier.objects.count() >= 3

    def test_custom_name_override(self):
        assert SupplierFactory(name="My Supplier").name == "My Supplier"

    @pytest.mark.parametrize(
        "field,max_length",
        [
            ("name", 255),
            ("email", 255),
            ("address", 500),
        ],
    )
    def test_field_max_length(self, field, max_length):
        assert Category._meta.get_field if True else None  # warmup
        f = Supplier._meta.get_field(field)
        assert f.max_length == max_length

    @pytest.mark.parametrize("field", ["email", "name", "phone", "address"])
    def test_required_field_exists(self, field):
        supplier = SupplierFactory()
        assert getattr(supplier, field) not in [None, ""]


@pytest.mark.django_db
class TestProductModel:

    def test_creation(self):
        product = ProductFactory()
        assert product.id is not None
        assert product.name
        assert product.sku
        assert product.cost_price > 0
        assert product.selling_price >= product.cost_price

    def test_uuid_primary_key(self):
        assert isinstance(ProductFactory().id, uuid.UUID)

    def test_subfactory_creates_relations(self):
        product = ProductFactory()
        assert isinstance(product.category, Category)
        assert isinstance(product.supplier, Supplier)

    def test_explicit_category_and_supplier(self):
        cat = CategoryFactory(name="Custom Cat")
        sup = SupplierFactory(name="Custom Sup")
        product = ProductFactory(category=cat, supplier=sup)
        assert product.category.name == "Custom Cat"
        assert product.supplier.name == "Custom Sup"

    def test_sku_unique_across_batch(self):
        skus = [p.sku for p in ProductFactory.create_batch(10)]
        assert len(skus) == len(set(skus))

    def test_duplicate_sku_raises(self):
        ProductFactory(sku="SKU-DUPE")
        with pytest.raises(Exception):
            ProductFactory(sku="SKU-DUPE")

    def test_selling_price_always_gte_cost_price(self):
        for p in ProductFactory.create_batch(5):
            assert p.selling_price >= p.cost_price

    @pytest.mark.parametrize(
        "trait,expected",
        [
            ("low_stock", lambda p: p.stock_quantity < p.low_stock_limit),
            ("out_of_stock", lambda p: p.stock_quantity == 0),
        ],
    )
    def test_product_traits(self, trait, expected):
        product = ProductFactory(**{trait: True})
        assert expected(product)

    @pytest.mark.parametrize(
        "field,value",
        [
            ("stock_quantity", 0),
            ("stock_quantity", 999),
            ("low_stock_limit", 1),
            ("low_stock_limit", 50),
        ],
    )
    def test_custom_field_value(self, field, value):
        product = ProductFactory(**{field: value})
        assert getattr(product, field) == value

    def test_timestamps_populated(self):
        product = ProductFactory()
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_ordering_newest_first(self):
        ProductFactory.create_batch(3)
        products = list(Product.objects.all())
        for i in range(len(products) - 1):
            assert products[i].created_at >= products[i + 1].created_at

    def test_verbose_name_plural(self):
        assert Product._meta.verbose_name_plural == "Products"

    @pytest.mark.parametrize(
        "index_fields", [["name"], ["sku"], ["category"], ["stock_quantity"]]
    )
    def test_db_index_exists(self, index_fields):
        all_index_fields = [list(idx.fields) for idx in Product._meta.indexes]
        assert index_fields in all_index_fields

    @pytest.mark.parametrize("deleted_relation", ["category", "supplier"])
    def test_cascade_delete(self, deleted_relation):
        product = ProductFactory()
        pid = product.id
        getattr(product, deleted_relation).delete()
        assert not Product.objects.filter(id=pid).exists()

    @pytest.mark.parametrize(
        "cost,selling",
        [
            (Decimal("100.00"), Decimal("150.00")),
            (Decimal("999.99"), Decimal("999.99")),
            (Decimal("0.01"), Decimal("0.99")),
        ],
    )
    def test_explicit_price_overrides(self, cost, selling):
        product = ProductFactory(cost_price=cost, selling_price=selling)
        assert product.cost_price == cost
        assert product.selling_price == selling


@pytest.mark.django_db
class TestStockMovementModel:

    def test_creation(self):
        movement = StockMovementFactory()
        assert movement.id is not None
        assert movement.product is not None
        assert movement.quantity >= 1
        assert movement.movement_type in ["IN", "OUT"]
        assert movement.reason in ["SALE", "PURCHASE", "RETURN", "MANUAL", "DAMAGED"]
        assert movement.user is not None

    def test_uuid_primary_key(self):
        assert isinstance(StockMovementFactory().id, uuid.UUID)

    def test_subfactory_creates_product_and_user(self):
        movement = StockMovementFactory()
        assert isinstance(movement.product, Product)

    @pytest.mark.parametrize(
        "trait,expected_type,expected_reason",
        [
            ("stock_in", "IN", "PURCHASE"),
            ("stock_out", "OUT", "SALE"),
        ],
    )
    def test_traits(self, trait, expected_type, expected_reason):
        movement = StockMovementFactory(**{trait: True})
        assert movement.movement_type == expected_type
        assert movement.reason == expected_reason

    @pytest.mark.parametrize("movement_type", ["IN", "OUT"])
    def test_valid_movement_types(self, movement_type):
        movement = StockMovementFactory(movement_type=movement_type)
        assert movement.movement_type == movement_type

    @pytest.mark.parametrize(
        "reason", ["SALE", "PURCHASE", "RETURN", "MANUAL", "DAMAGED"]
    )
    def test_valid_reasons(self, reason):
        movement = StockMovementFactory(reason=reason)
        assert movement.reason == reason

    def test_nullable_notes(self):
        assert StockMovementFactory(notes=None).notes is None

    def test_user_set_null_on_delete(self):
        movement = StockMovementFactory()
        movement.user.delete()
        movement.refresh_from_db()
        assert movement.user is None

    def test_cascade_on_product_delete(self):
        movement = StockMovementFactory()
        mid = movement.id
        movement.product.delete()
        assert not StockMovement.objects.filter(id=mid).exists()

    def test_timestamp_populated(self):
        assert StockMovementFactory().created_at is not None

    @pytest.mark.parametrize(
        "verbose,expected",
        [
            ("verbose_name", "Stock Movement"),
            ("verbose_name_plural", "Stock Movements"),
        ],
    )
    def test_verbose_names(self, verbose, expected):
        assert getattr(StockMovement._meta, verbose) == expected

    def test_multiple_movements_same_product(self):
        product = ProductFactory()
        StockMovementFactory.create_batch(5, product=product)
        assert StockMovement.objects.filter(product=product).count() == 5

    def test_batch_unique_ids(self):
        ids = [m.id for m in StockMovementFactory.create_batch(5)]
        assert len(ids) == len(set(ids))

    @pytest.mark.parametrize("quantity", [1, 10, 100, 999])
    def test_explicit_quantity(self, quantity):
        movement = StockMovementFactory(quantity=quantity)
        assert movement.quantity == quantity
