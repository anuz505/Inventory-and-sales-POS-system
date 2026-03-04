import pytest
from decimal import Decimal
from inventory.serializers import (
    CategorySerializer,
    SupplierSerializer,
    ProductSerializer,
    StockMovementSerializer,
)
from inventory.models import Category, Supplier, Product
from .factories import (
    CategoryFactory,
    SupplierFactory,
    ProductFactory,
    StockMovementFactory,
    UserFactory,
)


@pytest.mark.django_db
class TestCategorySerializer:
    def test_serializers_correct_fields(self):
        data = CategorySerializer(CategoryFactory()).data
        assert set(data.keys()) == {
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        }

    def test_id_matches_instance(self):
        category = CategoryFactory()
        assert CategorySerializer(category).data["id"] == str(category.id)

    @pytest.mark.parametrize(
        "field", ["name", "description", "created_at", "updated_at"]
    )
    def test_field_present_in_output(self, field):
        assert field in CategorySerializer(CategoryFactory()).data

    @pytest.mark.parametrize(
        "payload,is_valid",
        [
            ({"name": "Books", "description": "blah blah"}, True),
            ({"name": "Books"}, True),
            ({"description": "someting dumb "}, False),
            ({}, False),
        ],
    )
    def test_input_validation(self, payload, is_valid):
        assert CategorySerializer(data=payload).is_valid() == is_valid

    def test_create_via_serializer(self):
        obj = CategoryFactory.build()
        s = CategorySerializer(data={"name": obj.name, "description": obj.description})
        assert s.is_valid()
        assert isinstance(s.save(), Category)

    def test_update_via_serializer(self):
        category = CategoryFactory()
        s = CategorySerializer(
            category, data={"name": "Updated", "description": "Updated desc"}
        )
        assert s.is_valid()
        assert s.save().name == "Updated"

    @pytest.mark.parametrize("field", ["id", "created_at", "updated_at"])
    def test_read_only_fields_present(self, field):
        assert field in CategorySerializer(CategoryFactory()).data


@pytest.mark.django_db
class TestSupplierSerializer:

    def test_serializes_correct_fields(self):
        data = SupplierSerializer(SupplierFactory()).data
        assert set(data.keys()) == {
            "id",
            "name",
            "email",
            "phone",
            "address",
            "created_at",
            "updated_at",
        }

    @pytest.mark.parametrize("field", ["id", "name", "email", "phone", "address"])
    def test_field_present_in_output(self, field):
        assert field in SupplierSerializer(SupplierFactory()).data

    @pytest.mark.parametrize(
        "bad_email",
        [
            "not-an-email",
            "missing@",
            "@nodomain",
            "nodot@nodot",
        ],
    )
    def test_invalid_email_rejected(self, bad_email):
        obj = SupplierFactory.build()
        s = SupplierSerializer(
            data={
                "name": obj.name,
                "email": bad_email,
                "phone": obj.phone,
                "address": obj.address,
            }
        )
        assert not s.is_valid()
        assert "email" in s.errors

    @pytest.mark.parametrize("missing_field", ["name", "email", "phone", "address"])
    def test_required_field_missing(self, missing_field):
        obj = SupplierFactory.build()
        payload = {
            "name": obj.name,
            "email": obj.email,
            "phone": obj.phone,
            "address": obj.address,
        }
        del payload[missing_field]
        assert not SupplierSerializer(data=payload).is_valid()

    def test_valid_payload_passes(self):
        obj = SupplierFactory.build()
        s = SupplierSerializer(
            data={
                "name": obj.name,
                "email": obj.email,
                "phone": obj.phone,
                "address": obj.address,
            }
        )
        assert s.is_valid(), s.errors

    def test_create_via_serializer(self):
        obj = SupplierFactory.build()
        s = SupplierSerializer(
            data={
                "name": obj.name,
                "email": obj.email,
                "phone": obj.phone,
                "address": obj.address,
            }
        )
        assert s.is_valid()
        assert isinstance(s.save(), Supplier)


@pytest.mark.django_db
class TestProductSerializer:

    def test_serializes_correct_fields(self):
        expected = {
            "id",
            "name",
            "sku",
            "description",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "low_stock_limit",
            "created_at",
            "updated_at",
        }
        assert set(ProductSerializer(ProductFactory()).data.keys()) == expected

    @pytest.mark.parametrize("field", ["category_name", "supplier_name"])
    def test_nested_read_only_name_fields(self, field):
        product = ProductFactory()
        data = ProductSerializer(product).data
        assert data[field]  # not empty
        assert isinstance(data[field], str)

    def test_category_name_matches_related(self):
        product = ProductFactory()
        assert ProductSerializer(product).data["category_name"] == product.category.name

    def test_supplier_name_matches_related(self):
        product = ProductFactory()
        assert ProductSerializer(product).data["supplier_name"] == product.supplier.name

    @pytest.mark.parametrize(
        "cost,selling,is_valid",
        [
            ("100.00", "150.00", True),  # selling > cost  ✓
            ("300.00", "300.00", True),  # selling == cost ✓
            ("500.00", "100.00", False),  # selling < cost  ✗
            ("999.00", "1.00", False),  # large gap       ✗
        ],
    )
    def test_price_validation(self, cost, selling, is_valid, product_payload):
        product_payload["cost_price"] = cost
        product_payload["selling_price"] = selling
        assert ProductSerializer(data=product_payload).is_valid() == is_valid

    @pytest.mark.parametrize(
        "missing_field",
        ["name", "sku", "category", "supplier", "cost_price", "selling_price"],
    )
    def test_required_field_missing(self, missing_field, product_payload):
        del product_payload[missing_field]
        s = ProductSerializer(data=product_payload)
        assert not s.is_valid()
        assert missing_field in s.errors

    def test_create_via_serializer(self, product_payload):
        s = ProductSerializer(data=product_payload)
        assert s.is_valid(), s.errors
        instance = s.save()
        assert isinstance(instance, Product)
        assert instance.sku == product_payload["sku"]

    def test_update_via_serializer(self, product_payload):
        product = ProductFactory()
        product_payload["sku"] = product.sku
        s = ProductSerializer(product, data=product_payload)
        assert s.is_valid(), s.errors
        assert s.save().name == product_payload["name"]

    @pytest.mark.parametrize(
        "cost,selling",
        [
            (Decimal("99.99"), Decimal("149.99")),
            (Decimal("10.00"), Decimal("10.00")),
            (Decimal("0.50"), Decimal("1.00")),
        ],
    )
    def test_decimal_precision_preserved(self, cost, selling):
        product = ProductFactory(cost_price=cost, selling_price=selling)
        data = ProductSerializer(product).data
        assert Decimal(data["cost_price"]) == cost
        assert Decimal(data["selling_price"]) == selling


@pytest.mark.django_db
class TestStockMovementSerializer:

    def test_serializes_correct_fields(self):
        expected = {
            "id",
            "product",
            "product_name",
            "quantity",
            "movement_type",
            "reason",
            "user",
            "username",
            "notes",
            "created_at",
        }
        assert (
            set(StockMovementSerializer(StockMovementFactory()).data.keys()) == expected
        )

    def test_product_name_matches_related(self):
        movement = StockMovementFactory()
        assert (
            StockMovementSerializer(movement).data["product_name"]
            == movement.product.name
        )

    def test_username_matches_related(self):
        movement = StockMovementFactory()
        assert (
            StockMovementSerializer(movement).data["username"] == movement.user.username
        )

    @pytest.mark.parametrize(
        "movement_type,reason",
        [
            ("IN", "PURCHASE"),
            ("IN", "RETURN"),
            ("IN", "MANUAL"),
            ("OUT", "SALE"),
            ("OUT", "DAMAGED"),
            ("OUT", "MANUAL"),
        ],
    )
    def test_valid_type_reason_combinations(self, movement_type, reason):
        product = ProductFactory()
        user = UserFactory()
        s = StockMovementSerializer(
            data={
                "product": str(product.id),
                "quantity": 5,
                "movement_type": movement_type,
                "reason": reason,
                "user": str(user.id),
            }
        )
        assert s.is_valid(), f"Failed for {movement_type}/{reason}: {s.errors}"

    @pytest.mark.parametrize("bad_type", ["INVALID", "in", "out", "BOTH", "", "X"])
    def test_invalid_movement_type_rejected(self, bad_type):
        product = ProductFactory()
        user = UserFactory()
        s = StockMovementSerializer(
            data={
                "product": str(product.id),
                "quantity": 5,
                "movement_type": bad_type,
                "reason": "SALE",
                "user": str(user.id),
            }
        )
        assert not s.is_valid()
        assert "movement_type" in s.errors

    @pytest.mark.parametrize("bad_reason", ["UNKNOWN", "sale", "buy", "", "THEFT"])
    def test_invalid_reason_rejected(self, bad_reason):
        product = ProductFactory()
        user = UserFactory()
        s = StockMovementSerializer(
            data={
                "product": str(product.id),
                "quantity": 5,
                "movement_type": "OUT",
                "reason": bad_reason,
                "user": str(user.id),
            }
        )
        assert not s.is_valid()
        assert "reason" in s.errors

    @pytest.mark.parametrize("missing_field", ["product", "movement_type", "reason"])
    def test_required_field_missing(self, missing_field):
        product = ProductFactory()
        user = UserFactory()
        payload = {
            "product": str(product.id),
            "quantity": 5,
            "movement_type": "IN",
            "reason": "PURCHASE",
            "user": str(user.id),
        }
        del payload[missing_field]
        s = StockMovementSerializer(data=payload)
        assert not s.is_valid()
        assert missing_field in s.errors

    def test_notes_optional(self):
        product = ProductFactory()
        user = UserFactory()
        s = StockMovementSerializer(
            data={
                "product": str(product.id),
                "quantity": 5,
                "movement_type": "IN",
                "reason": "PURCHASE",
                "user": str(user.id),
            }
        )
        assert s.is_valid(), s.errors

    @pytest.mark.parametrize("quantity", [1, 10, 50, 999])
    def test_various_quantities_accepted(self, quantity):
        product = ProductFactory()
        user = UserFactory()
        s = StockMovementSerializer(
            data={
                "product": str(product.id),
                "quantity": quantity,
                "movement_type": "IN",
                "reason": "PURCHASE",
                "user": str(user.id),
            }
        )
        assert s.is_valid(), f"Failed for quantity={quantity}: {s.errors}"
