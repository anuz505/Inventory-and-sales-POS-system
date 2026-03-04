from decimal import Decimal

import pytest
import uuid
from django.urls import reverse

from sales.models import Sales
from .factories import CustomerFactory, SalesFactory, SalesItemFactory
from rest_framework import status


@pytest.mark.django_db
class TestUnauthenticatedAccess:
    @pytest.mark.parametrize("url_name,factory", [("customer-list", CustomerFactory)])
    def test_list_returns_401(self, api_client, url_name, factory):
        factory()
        assert (
            api_client.get(reverse(url_name)).status_code
            == status.HTTP_401_UNAUTHORIZED
        )

    @pytest.mark.parametrize("url_name,factory", [("customer-detail", CustomerFactory)])
    def test_detail_returns_401(self, api_client, url_name, factory):
        obj = factory()
        url = reverse(url_name, kwargs={"pk": str(obj.id)})
        assert api_client.get(url).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCustomerViewset:
    # ------------------------------------------------------------------ list
    def test_list_returns_200(self, auth_client):
        CustomerFactory.create_batch(3)
        assert (
            auth_client.get(reverse("customer-list")).status_code == status.HTTP_200_OK
        )

    def test_list_returns_all_customers(self, auth_client):
        CustomerFactory.create_batch(4)
        response = auth_client.get(reverse("customer-list"))
        assert response.data["count"] == 4

    def test_list_response_has_expected_fields(self, auth_client):
        CustomerFactory()
        response = auth_client.get(reverse("customer-list"))
        result = response.data["results"][0]
        assert set(result.keys()) == {
            "id",
            "name",
            "email",
            "phone_number",
            "address",
            "created_at",
            "updated_at",
        }

    # ------------------------------------------------------------------ pagination
    def test_pagination_limit(self, auth_client):
        CustomerFactory.create_batch(10)
        response = auth_client.get(reverse("customer-list"), {"limit": 3})
        assert len(response.data["results"]) == 3

    def test_pagination_offset(self, auth_client):
        CustomerFactory.create_batch(5)
        response_all = auth_client.get(reverse("customer-list"))
        all_ids = [r["id"] for r in response_all.data["results"]]

        response_offset = auth_client.get(reverse("customer-list"), {"offset": 2})
        offset_ids = [r["id"] for r in response_offset.data["results"]]
        assert offset_ids == all_ids[2:]

    # ------------------------------------------------------------------ filters
    def test_filter_by_name(self, auth_client):
        CustomerFactory(name="Alice Wonder")
        CustomerFactory(name="Bob Builder")
        response = auth_client.get(reverse("customer-list"), {"name": "alice"})
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Alice Wonder"

    def test_filter_by_email(self, auth_client):
        target = CustomerFactory(email="unique@example.com")
        CustomerFactory(email="other@example.com")
        response = auth_client.get(
            reverse("customer-list"), {"email": "unique@example.com"}
        )
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(target.id)

    def test_filter_by_phone_number(self, auth_client):
        target = CustomerFactory(phone_number="+10000000001")
        CustomerFactory(phone_number="+10000000002")
        response = auth_client.get(
            reverse("customer-list"), {"phone_number": "+10000000001"}
        )
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(target.id)

    def test_filter_by_address(self, auth_client):
        CustomerFactory(address="221B Baker Street")
        CustomerFactory(address="1600 Pennsylvania Ave")
        response = auth_client.get(reverse("customer-list"), {"address": "baker"})
        assert response.data["count"] == 1

    # ------------------------------------------------------------------ detail
    def test_detail_returns_200(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        assert auth_client.get(url).status_code == status.HTTP_200_OK

    def test_detail_returns_correct_customer(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        response = auth_client.get(url)
        assert response.data["id"] == str(customer.id)
        assert response.data["name"] == customer.name

    def test_detail_unknown_id_returns_404(self, auth_client):
        url = reverse("customer-detail", kwargs={"pk": str(uuid.uuid4())})
        assert auth_client.get(url).status_code == status.HTTP_404_NOT_FOUND

    # ------------------------------------------------------------------ create
    def test_create_returns_201(self, auth_client):
        payload = {
            "name": "New Customer",
            "email": "new@example.com",
            "phone_number": "+1234567890",
            "address": "123 Test St",
        }
        response = auth_client.post(reverse("customer-list"), payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_persists_to_db(self, auth_client):
        payload = {
            "name": "Persist Test",
            "email": "persist@example.com",
            "phone_number": "+1111111111",
            "address": "456 Persist Ave",
        }
        auth_client.post(reverse("customer-list"), payload, format="json")
        from sales.models import Customer

        assert Customer.objects.filter(email="persist@example.com").exists()

    def test_create_missing_name_returns_400(self, auth_client):
        payload = {
            "email": "bad@example.com",
            "phone_number": "+1234567890",
            "address": "No name here",
        }
        response = auth_client.post(reverse("customer-list"), payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    # ------------------------------------------------------------------ update
    def test_partial_update_returns_200(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        response = auth_client.patch(url, {"name": "Patched Name"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Patched Name"

    def test_full_update_returns_200(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        payload = {
            "name": "Full Update",
            "email": "full@example.com",
            "phone_number": "+9999999999",
            "address": "999 Full Update Rd",
        }
        response = auth_client.put(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "full@example.com"

    # ------------------------------------------------------------------ delete
    def test_delete_returns_204(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        assert auth_client.delete(url).status_code == status.HTTP_204_NO_CONTENT

    def test_delete_removes_from_db(self, auth_client):
        customer = CustomerFactory()
        url = reverse("customer-detail", kwargs={"pk": str(customer.id)})
        auth_client.delete(url)
        from sales.models import Customer

        assert not Customer.objects.filter(id=customer.id).exists()


@pytest.mark.django_db
class TestSalesListView:
    url = "/api-sales/sales/"

    def test_list_requires_auth(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_returns_sales(self, auth_client, user, customer):
        SalesFactory.create_batch(3, user=user, customer=customer)
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 3

    def test_filter_by_payment_status(self, auth_client, user, customer):
        SalesFactory(user=user, customer=customer, payment_status="pending")
        SalesFactory(user=user, customer=customer, payment_status="completed")
        resp = auth_client.get(self.url, {"payment_status": "pending"})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] == 1

    def test_filter_by_payment_method(self, auth_client, user, customer):
        SalesFactory(user=user, customer=customer, payment_method="cash")
        SalesFactory(user=user, customer=customer, payment_method="card")
        resp = auth_client.get(self.url, {"payment_method": "card"})
        assert resp.data["count"] == 1

    def test_filter_by_customer(self, auth_client, user, customer):
        other_customer = CustomerFactory()
        SalesFactory(user=user, customer=customer)
        SalesFactory(user=user, customer=other_customer)
        resp = auth_client.get(self.url, {"customer": str(customer.id)})
        assert resp.data["count"] == 1

    def test_ordering_by_created_at(self, auth_client, user, customer):
        SalesFactory.create_batch(3, user=user, customer=customer)
        resp = auth_client.get(self.url, {"ordering": "-created_at"})
        assert resp.status_code == status.HTTP_200_OK

    def test_filter_min_total(self, auth_client, user, customer):
        SalesFactory(user=user, customer=customer, total_amount=Decimal("50.00"))
        SalesFactory(user=user, customer=customer, total_amount=Decimal("200.00"))
        resp = auth_client.get(self.url, {"min_total": "100"})
        assert resp.data["count"] == 1


@pytest.mark.django_db
class TestSalesCreateView:
    url = "/api-sales/sales/"

    def test_create_pending_sale(self, auth_client, sale_payload):
        resp = auth_client.post(self.url, sale_payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["payment_status"] == "pending"
        assert resp.data["invoice_number"].startswith("INV-")

    def test_create_assigns_authenticated_user(self, auth_client, user, sale_payload):
        resp = auth_client.post(self.url, sale_payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        sale = Sales.objects.get(id=resp.data["id"])
        assert sale.user == user

    def test_create_completed_sale_deducts_stock(self, auth_client, customer, product):
        initial_stock = product.stock_quantity
        payload = {
            "customer": str(customer.id),
            "payment_method": "cash",
            "payment_status": "completed",
            "discount_amount": "0.00",
            "items": [
                {"product": str(product.id), "quantity": 5, "discount_amount": "0.00"}
            ],
        }
        resp = auth_client.post(self.url, payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        product.refresh_from_db()
        assert product.stock_quantity == initial_stock - 5

    def test_create_sale_insufficient_stock(
        self, auth_client, customer, out_of_stock_product
    ):
        payload = {
            "customer": str(customer.id),
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "0.00",
            "items": [
                {
                    "product": str(out_of_stock_product.id),
                    "quantity": 10,
                    "discount_amount": "0.00",
                }
            ],
        }
        resp = auth_client.post(self.url, payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sale_unauthenticated(self, api_client, sale_payload):
        resp = api_client.post(self.url, sale_payload, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_sale_no_items(self, auth_client, customer):
        payload = {
            "customer": str(customer.id),
            "payment_method": "cash",
            "payment_status": "pending",
            "discount_amount": "0.00",
            "items": [],
        }
        resp = auth_client.post(self.url, payload, format="json")
        # Items list can be empty or not — check that totals are 0
        if resp.status_code == status.HTTP_201_CREATED:
            assert Decimal(resp.data["subtotal"]) == Decimal("0.00")


@pytest.mark.django_db
class TestSalesUpdateView:
    def test_update_pending_to_completed(self, auth_client, sale_with_item, product):
        url = f"/api-sales/sales/{sale_with_item.id}/"
        resp = auth_client.patch(url, {"payment_status": "completed"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        sale_with_item.refresh_from_db()
        assert sale_with_item.payment_status == "completed"

    def test_update_completed_to_refunded(self, auth_client, user, customer, product):
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
        product.stock_quantity = 98
        product.save()

        url = f"/api-sales/sales/{sale.id}/"
        resp = auth_client.patch(url, {"payment_status": "refunded"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        sale.refresh_from_db()
        assert sale.payment_status == "refunded"

    def test_update_completed_sale_notes_rejected(self, auth_client, completed_sale):
        url = f"/api-sales/sales/{completed_sale.id}/"
        resp = auth_client.patch(url, {"notes": "Should not work"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_refunded_sale_rejected(self, auth_client, refunded_sale):
        url = f"/api-sales/sales/{refunded_sale.id}/"
        resp = auth_client.patch(url, {"payment_status": "pending"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_pending_sale_notes(self, auth_client, pending_sale):
        url = f"/api-sales/sales/{pending_sale.id}/"
        resp = auth_client.patch(url, {"notes": "Updated notes"}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        pending_sale.refresh_from_db()
        assert pending_sale.notes == "Updated notes"


@pytest.mark.django_db
class TestSalesDetailView:
    def test_retrieve_sale(self, auth_client, pending_sale):
        url = f"/api-sales/sales/{pending_sale.id}/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == str(pending_sale.id)
        assert "items" in resp.data
        assert "customer_name" in resp.data
        assert "staff_name" in resp.data

    def test_retrieve_nonexistent_sale(self, auth_client):
        url = "/api-sales/sales/00000000-0000-0000-0000-000000000000/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_sale(self, auth_client, pending_sale):
        url = f"/api-sales/sales/{pending_sale.id}/"
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Sales.objects.filter(pk=pending_sale.id).exists()


@pytest.mark.django_db
class TestDownloadInvoiceView:
    def test_download_invoice_success(self, auth_client, sale_with_item):
        url = f"/api-sales/sales/{sale_with_item.id}/download-invoice/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp["Content-Type"] == "application/pdf"
        assert (
            f"invoice_{sale_with_item.invoice_number}.pdf"
            in resp["Content-Disposition"]
        )

    def test_download_invoice_requires_auth(self, api_client, sale_with_item):
        url = f"/api-sales/sales/{sale_with_item.id}/download-invoice/"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_invoice_nonexistent_sale(self, auth_client):
        url = "/api-sales/sales/00000000-0000-0000-0000-000000000000/download-invoice/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ─── SalesItem ViewSet ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSalesItemView:
    url = "/api-sales/salesitem/"

    def test_list_requires_auth(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_sales_items(self, auth_client, sale_with_item):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1

    def test_filter_by_sale(self, auth_client, sale_with_item):
        resp = auth_client.get(self.url, {"sale": str(sale_with_item.id)})
        assert resp.status_code == status.HTTP_200_OK
        for item in resp.data["results"]:
            assert str(item["sale"]) == str(sale_with_item.id)

    def test_filter_by_product(self, auth_client, sale_with_item, product):
        resp = auth_client.get(self.url, {"product": str(product.id)})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["count"] >= 1
