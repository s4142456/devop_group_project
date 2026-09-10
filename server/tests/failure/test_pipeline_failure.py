# RMIT University Vietnam
# Course: COSC2767 Systems Deployment and Operations
# Semester: 2026B
# Assessment: Assignment 2
# Author: Ngo Hoang Long
# ID: s4142456
# Created date: 03/09/2026
# Last modified: 03/09/2026
# Acknowledgement: pytest documentation; OpenAI Codex used for failure-test
# demonstration guidance.

"""Opt-in failure used to prove that CI blocks a broken release."""

import os

import pytest


def test_intentional_pipeline_failure_is_detected():
    """Fail only when explicitly enabled for the recorded Jenkins demonstration."""
    if os.environ.get("DEMO_INTENTIONAL_FAILURE") != "1":
        pytest.skip("Set DEMO_INTENTIONAL_FAILURE=1 only for the CI failure demo.")

    pytest.fail("Intentional Assignment 2 failure: Jenkins must block deployment.")
