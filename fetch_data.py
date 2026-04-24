#!/usr/bin/env python3
"""Fetches 성동구 연립다세대 매매 실거래가 from MOLIT API and saves to data.json."""
import json
import os
import sys
from datetime import datetime

import requests


def fetch_month(session, api_key, deal_ymd):
    url = "https://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
    params = {
        "LAWD_CD": "11200",
        "DEAL_YMD": deal_ymd,
        "serviceKey": api_key,
        "numOfRows": 1000,
        "_type": "json",
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    body = resp.json().get("response", {}).get("body", {})
    total = body.get("totalCount", 0)
    items = body.get("items") or {}
    if not items:
        return [], total
    raw = items.get("item", [])
    if isinstance(raw, dict):
        raw = [raw]
    return raw, total


def main():
    api_key = os.environ.get("MOLIT_API_KEY", "").strip()
    if not api_key:
        print("ERROR: MOLIT_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)

    now = datetime.now()
    results = []

    with requests.Session() as session:
        for offset in range(6):  # last 6 months
            year = now.year
            month = now.month - offset
            while month <= 0:
                month += 12
                year -= 1
            deal_ymd = f"{year}{month:02d}"
            try:
                items, total = fetch_month(session, api_key, deal_ymd)
                results.extend(items)
                print(f"  {deal_ymd}: {len(items)} / {total} records")
            except Exception as exc:
                print(f"  {deal_ymd}: FAILED — {exc}", file=sys.stderr)

    out_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    print(f"\nSaved {len(results)} total records → {out_path}")


if __name__ == "__main__":
    main()
