"""Standalone GA4 Data API connection smoke test.

Usage:
    export GA_PROPERTY_ID="123456789"
    export GA_CREDENTIALS_PATH="/path/to/service-account-key.json"
    ./venv/bin/python harness/test_ga_connection.py

This pulls the simplest possible report (last 7 days, total page views) and
prints the raw response. If this works, the GA4 Data API connection is ready
to be wired into the analytics agent.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    property_id = os.environ.get("GA_PROPERTY_ID", "").strip()
    credentials_path = os.environ.get("GA_CREDENTIALS_PATH", "").strip()

    if not property_id:
        _fail("GA_PROPERTY_ID not set. Find it in GA4 → Admin → Property Settings.")
    if not credentials_path:
        _fail("GA_CREDENTIALS_PATH not set. Point it to the service-account JSON key.")
    if not Path(credentials_path).exists():
        _fail(f"Credentials file not found: {credentials_path}")

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
        from google.oauth2 import service_account
    except ImportError as e:
        print("Missing dependency. Install with:", file=sys.stderr)
        print("  ./venv/bin/pip install google-analytics-data", file=sys.stderr)
        _fail(str(e))

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )

    print(f"Connecting to GA4 property: {property_id}")
    print(f"Using credentials: {credentials_path}")
    try:
        response = client.run_report(request)
    except Exception as e:
        _fail(f"GA4 API call failed: {e}")

    print("\n--- Raw response ---")
    print(response)

    print("\n--- Parsed ---")
    print(f"Row count: {len(response.rows)}")
    for header in response.metric_headers:
        print(f"Metric: {header.name}")
    for row in response.rows:
        for val in row.metric_values:
            print(f"  Value: {val.value}")

    print("\nConnection successful. GA4 Data API is reachable.")


if __name__ == "__main__":
    main()
