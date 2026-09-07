# RMIT University Vietnam
# Course: COSC2767 Systems Deployment and Operations
# Semester: 2026B
# Assessment: Assignment 2
# Author: Ngo Hoang Long
# ID: s4142456
# Created date: 03/09/2026
# Last modified: 03/09/2026
# Acknowledgement: Supplied RMIT Store application; Django REST Framework,
# pytest-django and Django testing documentation; OpenAI Codex used for
# integration-test design guidance.

"""API/database integration tests for the checkout and order boundary."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.orders.models import Order


pytestmark = pytest.mark.django_db


def make_user(email):
    return User.objects.create_user(email=email, password="TestPassword123!")


def card(number="4242 4242 4242 4242"):
    return {
        "number": number,
        "exp_month": 12,
        "exp_year": 2100,
        "cvc": "123",
        "name_on_card": "Integration Test Customer",
    }


def checkout_payload(product, quantity=1, payment=None):
    return {
        "items": [{"product": product.pk, "quantity": quantity}],
        "payment": payment or card(),
    }


def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_successful_checkout_creates_order_and_decrements_stock():
    user = make_user("buyer@example.com")
    product = Product.objects.create(
        sku="INT-001",
        name="Integration Product",
        price=Decimal("20.00"),
        quantity=5,
        taxable=True,
    )

    response = authenticated_client(user).post(
        "/api/orders/", checkout_payload(product, quantity=2), format="json"
    )

    assert response.status_code == 201, response.data
    assert Order.objects.filter(user=user).count() == 1
    order = Order.objects.get(user=user)
    assert order.subtotal == Decimal("40.00")
    assert order.total_tax == Decimal("2.00")
    assert order.total == Decimal("42.00")
    assert order.payment_status == "paid"
    assert order.card_last4 == "4242"
    assert order.items.get().quantity == 2
    product.refresh_from_db()
    assert product.quantity == 3


def test_declined_checkout_rolls_back_order_and_stock():
    user = make_user("declined@example.com")
    product = Product.objects.create(
        sku="INT-002",
        name="Decline Product",
        price=Decimal("15.00"),
        quantity=4,
        taxable=False,
    )

    response = authenticated_client(user).post(
        "/api/orders/",
        checkout_payload(product, quantity=2, payment=card("4000 0000 0000 0002")),
        format="json",
    )

    assert response.status_code == 402, response.data
    assert response.data["decline_code"] == "card_declined"
    assert Order.objects.filter(user=user).count() == 0
    product.refresh_from_db()
    assert product.quantity == 4


def test_order_list_is_scoped_to_authenticated_user():
    first_user = make_user("first@example.com")
    second_user = make_user("second@example.com")
    product = Product.objects.create(
        sku="INT-003",
        name="Ownership Product",
        price=Decimal("10.00"),
        quantity=5,
    )

    first_response = authenticated_client(first_user).post(
        "/api/orders/", checkout_payload(product), format="json"
    )
    assert first_response.status_code == 201, first_response.data
    order_id = first_response.data["id"]

    second_client = authenticated_client(second_user)
    list_response = second_client.get("/api/orders/")
    detail_response = second_client.get(f"/api/orders/{order_id}/")

    assert list_response.status_code == 200
    assert list_response.data["count"] == 0
    assert detail_response.status_code == 404


def test_anonymous_user_cannot_access_orders():
    response = APIClient().get("/api/orders/")

    assert response.status_code == 401
