import pytest
import uuid
from django.urls import reverse
from .factories import CustomerFactory
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
            "id", "name", "email", "phone_number", "address",
            "created_at", "updated_at",
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
        response = auth_client.get(reverse("customer-list"), {"email": "unique@example.com"})
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == str(target.id)

    def test_filter_by_phone_number(self, auth_client):
        target = CustomerFactory(phone_number="+10000000001")
        CustomerFactory(phone_number="+10000000002")
        response = auth_client.get(reverse("customer-list"), {"phone_number": "+10000000001"})
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
