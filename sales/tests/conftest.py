import pytest
from .factories import CustomerFactory

# customer fixtures


@pytest.fixture
def customer(db):
    return CustomerFactory()
