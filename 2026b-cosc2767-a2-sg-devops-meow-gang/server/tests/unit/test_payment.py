# RMIT University Vietnam
# Course: COSC2767 Systems Deployment and Operations
# Semester: 2026B
# Assessment: Assignment 2
# Author: Ngo Hoang Long
# ID: s4142456
# Created date: 03/09/2026
# Last modified: 03/09/2026
# Acknowledgement: Django REST Framework and pytest documentation; OpenAI Codex used for test-design guidance.

from apps.orders.serializers import PaymentSerializer

def test_valid_payment_input():
    serializer = PaymentSerializer(
        data={
            "number": "4242 4242 4242 4242",
            "exp_month": 12,
            "exp_year": 2100,
            "cvc": "123",
            "name_on_card": "Test Customer",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["number"] == "4242424242424242"
    assert serializer.validated_data["cvc"] == "123"

def test_invalid_payment_input():
    valid_payment = {
        "number": "4242 4242 4242 4242",
        "exp_month": 12,
        "exp_year": 2100,
        "cvc": "123",
        "name_on_card": "Test Customer",
    }

    invalid_cases = [
        (
            {"number": "4242 4242 4242 4241"},
            "number",
        ),
        (
            {"exp_month": 1, "exp_year": 2000},
            "exp_year",
        ),
        (
            {"cvc": "12"},
            "cvc",
        ),
        (
            {"cvc": "abc"},
            "cvc",
        ),
    ]

    for changed_fields, expected_error_field in invalid_cases:
        payment_data = valid_payment.copy()
        payment_data.update(changed_fields)

        serializer = PaymentSerializer(data=payment_data)

        assert not serializer.is_valid(), (
            f"Payment data was unexpectedly accepted: {changed_fields}"
        )
        assert expected_error_field in serializer.errors, serializer.errors