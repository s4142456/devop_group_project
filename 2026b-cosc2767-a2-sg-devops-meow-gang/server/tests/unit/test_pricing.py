# RMIT University Vietnam
# Course: COSC2767 Systems Deployment and Operations
# Semester: 2026B
# Assessment: Assignment 2
# Author: Ngo Hoang Long
# ID: s4142456
# Created date: 03/09/2026
# Last modified: 03/09/2026
# Acknowledgement: pytest, pytest-django and pytest-cov documentation.

from decimal import Decimal

from django.test import override_settings

from apps.orders.services import subtotal_for, tax_for, total_for

# Test subtotal values. Pytest auto detects fuctions name test_
def test_subtotal_calculation():
    subtotal = subtotal_for(
        [
            # Represents product 1 & 2
            (Decimal("19.99"), 2),
            (Decimal("10.00"), 1),            
        ]
    )

    assert subtotal == Decimal("49.98")

# Django test decorator, set sales tax rate for just this test
@override_settings(SALES_TAX_RATE=0.05)
def test_tax_calculations():
    taxable_tax = tax_for(
        amount=Decimal("39.98"),
        taxable=True,
    )
    non_taxable_tax = tax_for(
        amount=Decimal("10.00"),
        taxable=False,
    )
    assert taxable_tax == Decimal("2.00")
    assert non_taxable_tax == Decimal("0.00")

def test_total_calculation():
    total = total_for(
        subtotal=Decimal("49.98"),
        total_tax=Decimal("2.00"),
    )

    assert total == Decimal("51.98")