import pytest
import uuid
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from .factories import (
    CategoryFactory,
    SupplierFactory,
    ProductFactory,
    StockMovementFactory,
    UserFactory,
)

# Auth Enforcement


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """All protected endpoints must return 401 for unauthenticated requests."""

    @pytest.mark.parametrize(
        "url_name,factory",
        [
            ("supplier-list", SupplierFactory),
            ("products-list", ProductFactory),
            ("stockmovement-list", StockMovementFactory),
        ],
    )
    def test_list_returns_401(self, api_client, url_name, factory):
        factory()
        assert (
            api_client.get(reverse(url_name)).status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    @pytest.mark.parametrize(
        "url_name,factory",
        [
            ("supplier-list", SupplierFactory),
            ("products-list", ProductFactory),
            ("stockmovement-list", StockMovementFactory),
        ],
    )
    def test_post_returns_401(self, api_client, url_name, factory):
        assert (
            api_client.post(reverse(url_name), {}, format="json").status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    @pytest.mark.parametrize(
        "url_name,factory",
        [
            ("supplier-detail", SupplierFactory),
            ("products-detail", ProductFactory),
            ("stockmovement-detail", StockMovementFactory),
        ],
    )
    def test_detail_returns_401(self, api_client, url_name, factory):
        obj = factory()
        url = reverse(url_name, kwargs={"pk": str(obj.id)})
        assert api_client.get(url).status_code == status.HTTP_401_UNAUTHORIZED


# Category ViewSet


@pytest.mark.django_db
class TestCategoryViewSet:

    def test_list_returns_200(self, api_client):
        CategoryFactory.create_batch(3)
        assert (
            api_client.get(reverse("category-list")).status_code == status.HTTP_200_OK
        )

    def test_create_returns_201(self, api_client, category_payload):
        response = api_client.post(
            reverse("category-list"), category_payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == category_payload["name"]

    def test_retrieve_returns_200(self, api_client):
        cat = CategoryFactory()
        response = api_client.get(
            reverse("category-detail", kwargs={"pk": str(cat.id)})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == cat.name

    def test_retrieve_nonexistent_returns_404(self, api_client):
        url = reverse("category-detail", kwargs={"pk": str(uuid.uuid4())})
        assert api_client.get(url).status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "method,expected_status",
        [
            ("put", status.HTTP_200_OK),
            ("patch", status.HTTP_200_OK),
        ],
    )
    def test_update_methods(self, api_client, method, expected_status):
        cat = CategoryFactory()
        url = reverse("category-detail", kwargs={"pk": str(cat.id)})
        payload = {"name": "Updated", "description": "Updated desc"}
        response = getattr(api_client, method)(url, payload, format="json")
        assert response.status_code == expected_status
        assert response.data["name"] == "Updated"

    def test_delete_returns_204(self, api_client):
        cat = CategoryFactory()
        response = api_client.delete(
            reverse("category-detail", kwargs={"pk": str(cat.id)})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("limit,expected_max", [(2, 2), (5, 5), (1, 1)])
    def test_pagination_limit(self, api_client, limit, expected_max):
        CategoryFactory.create_batch(10)
        response = api_client.get(reverse("category-list"), {"limit": limit})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) <= expected_max


# Supplier ViewSet


@pytest.mark.django_db
class TestSupplierViewSet:

    def test_list_authenticated_returns_200(self, auth_client):
        SupplierFactory.create_batch(2)
        assert (
            auth_client.get(reverse("supplier-list")).status_code == status.HTTP_200_OK
        )

    def test_create_supplier(self, auth_client, supplier_payload):
        response = auth_client.post(
            reverse("supplier-list"), supplier_payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == supplier_payload["email"]

    @pytest.mark.parametrize("bad_email", ["not-email", "missing@", "@nodomain"])
    def test_create_with_invalid_email_returns_400(
        self, auth_client, supplier_payload, bad_email
    ):
        supplier_payload["email"] = bad_email
        response = auth_client.post(
            reverse("supplier-list"), supplier_payload, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_supplier(self, auth_client):
        supplier = SupplierFactory()
        response = auth_client.get(
            reverse("supplier-detail", kwargs={"pk": str(supplier.id)})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == supplier.name

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_update_supplier(self, auth_client, method):
        supplier = SupplierFactory()
        new = SupplierFactory.build()
        payload = {
            "name": new.name,
            "email": new.email,
            "phone": new.phone,
            "address": new.address,
        }
        url = reverse("supplier-detail", kwargs={"pk": str(supplier.id)})
        response = getattr(auth_client, method)(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_delete_supplier(self, auth_client):
        supplier = SupplierFactory()
        response = auth_client.delete(
            reverse("supplier-detail", kwargs={"pk": str(supplier.id)})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("limit", [1, 2, 5])
    def test_pagination(self, auth_client, limit):
        SupplierFactory.create_batch(8)
        response = auth_client.get(reverse("supplier-list"), {"limit": limit})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) <= limit


# Product ViewSet


@pytest.mark.django_db
class TestProductViewSet:

    def test_list_returns_200(self, auth_client):
        ProductFactory.create_batch(2)
        assert (
            auth_client.get(reverse("products-list")).status_code == status.HTTP_200_OK
        )

    def test_list_includes_nested_names(self, auth_client):
        ProductFactory()
        result = auth_client.get(reverse("products-list")).data["results"][0]
        assert "category_name" in result
        assert "supplier_name" in result

    def test_create_product(self, auth_client, product_payload):
        response = auth_client.post(
            reverse("products-list"), product_payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["sku"] == product_payload["sku"]

    @pytest.mark.parametrize(
        "cost,selling",
        [
            ("999.00", "1.00"),
            ("500.00", "499.99"),
            ("100.00", "0.01"),
        ],
    )
    def test_create_invalid_price_returns_400(
        self, auth_client, product_payload, cost, selling
    ):
        product_payload["cost_price"] = cost
        product_payload["selling_price"] = selling
        response = auth_client.post(
            reverse("products-list"), product_payload, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize(
        "cost,selling",
        [
            ("100.00", "150.00"),
            ("200.00", "200.00"),
        ],
    )
    def test_create_valid_price_returns_201(
        self, auth_client, product_payload, cost, selling
    ):
        product_payload["cost_price"] = cost
        product_payload["selling_price"] = selling
        response = auth_client.post(
            reverse("products-list"), product_payload, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_product(self, auth_client):
        product = ProductFactory()
        response = auth_client.get(
            reverse("products-detail", kwargs={"pk": str(product.id)})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["sku"] == product.sku

    def test_partial_update_stock_quantity(self, auth_client):
        product = ProductFactory(stock_quantity=10)
        response = auth_client.patch(
            reverse("products-detail", kwargs={"pk": str(product.id)}),
            {"stock_quantity": 99},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["stock_quantity"] == 99

    def test_delete_product(self, auth_client):
        product = ProductFactory()
        response = auth_client.delete(
            reverse("products-detail", kwargs={"pk": str(product.id)})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_duplicate_sku_returns_400(self, auth_client, product_payload):
        existing = ProductFactory()
        product_payload["sku"] = existing.sku
        response = auth_client.post(
            reverse("products-list"), product_payload, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_category(self, auth_client):
        cat = CategoryFactory()
        ProductFactory.create_batch(3, category=cat)
        ProductFactory.create_batch(2)
        response = auth_client.get(reverse("products-list"), {"category": str(cat.id)})
        assert response.status_code == status.HTTP_200_OK
        assert all(str(r["category"]) == str(cat.id) for r in response.data["results"])

    @pytest.mark.parametrize(
        "ordering,key,reverse_sort",
        [
            ("name", "name", False),
            ("-name", "name", True),
            ("selling_price", "selling_price", False),
            ("-selling_price", "selling_price", True),
            ("stock_quantity", "stock_quantity", False),
        ],
    )
    def test_ordering(self, auth_client, ordering, key, reverse_sort):
        ProductFactory.create_batch(5)
        response = auth_client.get(reverse("products-list"), {"ordering": ordering})
        assert response.status_code == status.HTTP_200_OK
        numeric_keys = {
            "selling_price",
            "cost_price",
            "stock_quantity",
            "low_stock_limit",
        }
        raw = [r[key] for r in response.data["results"]]
        values = [Decimal(str(v)) for v in raw] if key in numeric_keys else raw
        assert values == sorted(values, reverse=reverse_sort)

    @pytest.mark.parametrize("limit", [1, 3, 5])
    def test_pagination(self, auth_client, limit):
        ProductFactory.create_batch(10)
        response = auth_client.get(reverse("products-list"), {"limit": limit})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) <= limit

    @pytest.mark.parametrize(
        "trait,field,check",
        [
            ("low_stock", "stock_quantity", lambda v, p: v < p["low_stock_limit"]),
            ("out_of_stock", "stock_quantity", lambda v, _: v == 0),
        ],
    )
    def test_trait_products_in_list(self, auth_client, trait, field, check):
        ProductFactory(**{trait: True})
        response = auth_client.get(reverse("products-list"))
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert any(check(r[field], r) for r in results)


# StockMovement ViewSet


@pytest.mark.django_db
class TestStockMovementViewSet:

    def test_list_returns_200(self, auth_client):
        StockMovementFactory.create_batch(2)
        assert (
            auth_client.get(reverse("stockmovement-list")).status_code
            == status.HTTP_200_OK
        )

    def test_list_includes_product_name_and_username(self, auth_client):
        StockMovementFactory()
        result = auth_client.get(reverse("stockmovement-list")).data["results"][0]
        assert "product_name" in result
        assert "username" in result

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
    def test_create_valid_movement(self, auth_client, movement_type, reason):
        product = ProductFactory()
        user = UserFactory()
        response = auth_client.post(
            reverse("stockmovement-list"),
            {
                "product": str(product.id),
                "quantity": 10,
                "movement_type": movement_type,
                "reason": reason,
                "user": str(user.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["movement_type"] == movement_type

    @pytest.mark.parametrize("bad_type", ["INVALID", "in", "out", ""])
    def test_invalid_movement_type_returns_400(self, auth_client, bad_type):
        product = ProductFactory()
        user = UserFactory()
        response = auth_client.post(
            reverse("stockmovement-list"),
            {
                "product": str(product.id),
                "quantity": 5,
                "movement_type": bad_type,
                "reason": "SALE",
                "user": str(user.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("bad_reason", ["UNKNOWN", "buy", "sell", ""])
    def test_invalid_reason_returns_400(self, auth_client, bad_reason):
        product = ProductFactory()
        user = UserFactory()
        response = auth_client.post(
            reverse("stockmovement-list"),
            {
                "product": str(product.id),
                "quantity": 5,
                "movement_type": "OUT",
                "reason": bad_reason,
                "user": str(user.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_movement(self, auth_client):
        movement = StockMovementFactory()
        response = auth_client.get(
            reverse("stockmovement-detail", kwargs={"pk": str(movement.id)})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["movement_type"] == movement.movement_type

    def test_delete_movement(self, auth_client):
        movement = StockMovementFactory()
        response = auth_client.delete(
            reverse("stockmovement-detail", kwargs={"pk": str(movement.id)})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize("movement_type", ["IN", "OUT"])
    def test_filter_by_movement_type(self, auth_client, movement_type):
        StockMovementFactory.create_batch(
            3, **{"stock_in" if movement_type == "IN" else "stock_out": True}
        )
        response = auth_client.get(
            reverse("stockmovement-list"), {"movement_type": movement_type}
        )
        assert response.status_code == status.HTTP_200_OK
        assert all(
            r["movement_type"] == movement_type for r in response.data["results"]
        )

    @pytest.mark.parametrize("limit", [1, 3, 5])
    def test_pagination(self, auth_client, limit):
        StockMovementFactory.create_batch(10)
        response = auth_client.get(reverse("stockmovement-list"), {"limit": limit})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) <= limit

    @pytest.mark.parametrize("quantity", [1, 10, 100])
    def test_create_with_various_quantities(self, auth_client, quantity):
        product = ProductFactory()
        user = UserFactory()
        response = auth_client.post(
            reverse("stockmovement-list"),
            {
                "product": str(product.id),
                "quantity": quantity,
                "movement_type": "IN",
                "reason": "PURCHASE",
                "user": str(user.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == quantity
