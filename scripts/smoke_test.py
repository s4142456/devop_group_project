# RMIT University Vietnam
# Course: COSC2767 Systems Deployment and Operations
# Semester: 2026B
# Assessment: Assignment 2
# Author: Ngo Hoang Long
# ID: s4142456
# Created date: 03/09/2026
# Last modified: 03/09/2026
# Acknowledgement: Python urllib documentation and supplied RMIT Store application;
# OpenAI Codex used for smoke-test design guidance.

"""Post-deployment smoke tests for the public RMIT Store application."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def fetch(url, timeout, expected_content_type=None):
    """Return the response body and content type, or raise a useful error."""
    request = Request(url, headers={"User-Agent": "rmit-store-smoke-test/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            content_type = response.headers.get_content_type()
            body = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} from {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc.reason}") from exc

    if status != 200:
        raise RuntimeError(f"Expected HTTP 200 from {url}, received {status}")
    if expected_content_type and not content_type.startswith(expected_content_type):
        raise RuntimeError(
            f"Expected {expected_content_type} from {url}, received {content_type}"
        )
    return body, content_type


def fetch_json(url, timeout):
    body, _ = fetch(url, timeout, "application/json")
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid JSON returned by {url}") from exc


def application_url(base_url, path):
    return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SMOKE_BASE_URL", "http://localhost"),
        help="Public application origin, for example http://staging.example.com",
    )
    parser.add_argument(
        "--frontend-url",
        default=os.environ.get("SMOKE_FRONTEND_URL"),
        help="Optional separate frontend origin for local development",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("SMOKE_API_URL"),
        help="Optional separate API origin for local development",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    frontend_url = args.frontend_url or args.base_url
    api_url = args.api_url or args.base_url

    failures = []
    products = []

    def check(name, operation):
        try:
            detail = operation()
            print(f"[PASS] {name}: {detail}")
        except Exception as exc:  # noqa: BLE001 - every failed check is reported
            failures.append(f"{name}: {exc}")
            print(f"[FAIL] {name}: {exc}")

    def check_frontend():
        body, _ = fetch(application_url(frontend_url, "/"), args.timeout, "text/html")
        page = body.decode("utf-8", errors="replace")
        if '<div id="app"></div>' not in page:
            raise RuntimeError("response is HTML but not the Vue application shell")
        return "Vue application shell returned HTTP 200"

    def check_health():
        data = fetch_json(application_url(api_url, "/healthz/"), args.timeout)
        if data.get("status") != "ok":
            raise RuntimeError(f"unexpected response {data}")
        return "application process is live"

    def check_readiness():
        data = fetch_json(application_url(api_url, "/readyz/"), args.timeout)
        if data.get("database") != "ok" or data.get("storage") != "ok":
            raise RuntimeError(f"dependencies are not ready: {data}")
        return "database and storage are ready"

    def check_version():
        data = fetch_json(application_url(api_url, "/api/version/"), args.timeout)
        if not data.get("version") or not data.get("commit"):
            raise RuntimeError(f"version or commit is missing: {data}")
        return f"version={data['version']} commit={data['commit']}"

    def check_products():
        data = fetch_json(application_url(api_url, "/api/products/"), args.timeout)
        results = data.get("results") if isinstance(data, dict) else None
        if not results:
            raise RuntimeError("product API returned no products")
        products.extend(results)
        return f"product API returned {len(results)} product(s)"

    def check_media():
        if not products:
            data = fetch_json(application_url(api_url, "/api/products/"), args.timeout)
            products.extend(data.get("results") or [])
        image_urls = [
            product.get("image_url") for product in products if product.get("image_url")
        ]
        if not image_urls:
            raise RuntimeError("no product with an image URL was returned")

        last_error = None
        for image_url in image_urls:
            media_url = urljoin(f"{api_url.rstrip('/')}/", image_url)
            try:
                body, content_type = fetch(media_url, args.timeout, "image/")
                if body:
                    return f"{content_type}, {len(body)} bytes from {media_url}"
            except RuntimeError as exc:
                last_error = exc

        raise RuntimeError(
            f"none of the {len(image_urls)} returned image URLs worked; {last_error}"
        )

    check("frontend", check_frontend)
    check("liveness /healthz/", check_health)
    check("readiness /readyz/", check_readiness)
    check("version /api/version/", check_version)
    check("product API", check_products)
    check("media/image endpoint", check_media)

    if failures:
        print(f"\nSmoke test failed: {len(failures)} check(s) did not pass.")
        return 1

    print("\nSmoke test passed: all 6 deployment checks succeeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
