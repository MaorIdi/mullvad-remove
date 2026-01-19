#!/usr/bin/env python3
"""
mullvad_device_cleaner.py

Periodically removes any Mullvad account devices not in an allowlist.

Requirements:
  pip install requests

Usage:
  export MULLVAD_ACCOUNT_NUMBER="6989742591567920"
  printf "happy-lion\ncalm-otter\n" > allowed_devices.txt

  # Dry run (recommended first):
  python mullvad_device_cleaner.py

  # Actually remove:
  python mullvad_device_cleaner.py --apply

  # Run every 5 minutes:
  python mullvad_device_cleaner.py --apply --interval 300
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Iterable, Set, Dict, Any, Optional

import requests

API_BASE = "https://api.mullvad.net"


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load_allowlist(path: str) -> Set[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            names = {line.strip().lower() for line in f if line.strip() and not line.strip().startswith("#")}
        if not names:
            die(f"Allowlist file '{path}' is empty.")
        return names
    except FileNotFoundError:
        die(f"Allowlist file '{path}' not found. Create it with one allowed device name per line.")


def get_access_token(account_number: str, timeout_s: int = 15) -> str:
    """
    Uses Mullvad's auth token endpoint documented in community notes:
      POST /auth/v1/token  {"account_number": "..."}
    """
    url = f"{API_BASE}/auth/v1/token"
    r = requests.post(url, json={"account_number": account_number}, timeout=timeout_s)
    if r.status_code != 200:
        die(f"Token request failed ({r.status_code}): {r.text[:300]}")
    data = r.json()
    token = data.get("access_token")
    if not token:
        die(f"Token response missing access_token: {data}")
    return token


def list_devices(access_token: str, timeout_s: int = 15) -> Iterable[Dict[str, Any]]:
    """
    GET /accounts/v1/devices  Authorization: Bearer <token>

    Some Mullvad API responses return a JSON list directly, others wrap in {"devices": [...] }.
    Handle both.
    """
    url = f"{API_BASE}/accounts/v1/devices"
    r = requests.get(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=timeout_s)
    if r.status_code != 200:
        die(f"List devices failed ({r.status_code}): {r.text[:300]}")

    data = r.json()

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        devices = data.get("devices")
        if isinstance(devices, list):
            return devices
        die(f"Unexpected devices payload (dict but devices is not a list): {data}")

    die(f"Unexpected devices payload type: {type(data).__name__}")



def delete_device(access_token: str, device_id: str, timeout_s: int = 15) -> requests.Response:
    """
    Many REST designs use:
      DELETE /accounts/v1/devices/{id}

    If this returns 404/405, Mullvad may have changed the endpoint; in that case,
    do NOT loop aggressively—stop and investigate.
    """
    url = f"{API_BASE}/accounts/v1/devices/{device_id}"
    return requests.delete(url, headers={"Authorization": f"Bearer {access_token}"}, timeout=timeout_s)


def summarize_devices(devices: Iterable[Dict[str, Any]]) -> None:
    print("Current devices on account:")
    for d in devices:
        name = str(d.get("name", "")).lower()
        did = d.get("id", "")
        created = d.get("created", d.get("created_at", ""))
        print(f"  - {name:20s}  id={did}  created={created}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allowlist", default="allowed_devices.txt", help="Path to allowlist file (one device name per line)")
    ap.add_argument("--apply", action="store_true", help="Actually remove non-allowlisted devices (default: dry-run)")
    ap.add_argument("--interval", type=int, default=0, help="Repeat every N seconds (0 = run once)")
    args = ap.parse_args()

    account = os.environ.get("MULLVAD_ACCOUNT_NUMBER", "").strip()
    if not account:
        die("Set MULLVAD_ACCOUNT_NUMBER in your environment.")

    allow = load_allowlist(args.allowlist)

    while True:
        try:
            token = get_access_token(account)
            devices = list(list_devices(token))

            print("\n" + time.strftime("%Y-%m-%d %H:%M:%S"))
            summarize_devices(devices)

            to_remove = []
            for d in devices:
                name = str(d.get("name", "")).strip().lower()
                did = str(d.get("id", "")).strip()
                if not name or not did:
                    continue
                if name not in allow:
                    to_remove.append((name, did))

            if not to_remove:
                print("No devices to remove (all devices are allowlisted).")
            else:
                print("Devices NOT in allowlist:")
                for name, did in to_remove:
                    print(f"  - {name}  (id={did})")

                if not args.apply:
                    print("Dry-run: no deletions performed. Re-run with --apply to remove.")
                else:
                    for name, did in to_remove:
                        print(f"Deleting {name} (id={did})...")
                        resp = delete_device(token, did)
                        if resp.status_code in (200, 204):
                            print("  -> deleted")
                        else:
                            # Fail closed: stop rather than possibly doing the wrong thing repeatedly.
                            die(f"Delete failed for {name} ({resp.status_code}): {resp.text[:300]}")

        except requests.RequestException as e:
            die(f"Network/API error: {e}")

        if args.interval <= 0:
            break
        time.sleep(args.interval)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
