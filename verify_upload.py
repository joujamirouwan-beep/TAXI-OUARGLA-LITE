#!/usr/bin/env python3
"""Verify the committed release is present on the Google Play internal track."""
import argparse, os, re, sys
from pathlib import Path

PACKAGE = "com.taxiouargla.lite"
SCOPE = ["https://www.googleapis.com/auth/androidpublisher"]


def fail(msg):
    raise SystemExit(f"FAIL: {msg}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--package", default=PACKAGE)
    p.add_argument("--version-code", required=True, type=int)
    p.add_argument("--service-account", default=os.environ.get("PLAY_SERVICE_ACCOUNT_JSON", "play-api-key.json"))
    p.add_argument("--track", default="internal", choices=["internal"])
    p.add_argument("--expected-status", default="draft", choices=["draft", "inProgress", "completed", "halted"])
    a = p.parse_args()
    if a.package != PACKAGE:
        fail(f"Package must be {PACKAGE}")
    if a.version_code <= 0:
        fail("version-code must be positive")
    cred_file = Path(a.service_account)
    if not cred_file.is_file():
        fail(f"Service Account JSON not found: {cred_file}")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        fail("Install tools/requirements-play-upload.txt first")
    creds = service_account.Credentials.from_service_account_file(str(cred_file), scopes=SCOPE)
    api = build("androidpublisher", "v3", credentials=creds, cache_discovery=False)
    edit_id = None
    try:
        edit_id = api.edits().insert(packageName=a.package, body={}).execute()["id"]
        track = api.edits().tracks().get(packageName=a.package, editId=edit_id, track=a.track).execute()
        releases = track.get("releases", [])
        matches = [r for r in releases if a.version_code in [int(x) for x in r.get("versionCodes", [])]]
        if not matches:
            fail(f"versionCode {a.version_code} not found on track {a.track}")
        statuses = {r.get("status") for r in matches}
        if a.expected_status not in statuses:
            fail(f"Expected status {a.expected_status}; observed {sorted(str(x) for x in statuses)}")
        print("PASS: package =", a.package)
        print("PASS: track =", a.track)
        print("PASS: versionCode =", a.version_code)
        print("PASS: release status =", a.expected_status)
        print("NOTE: API confirmation does not prove that testers can install it; a Draft release must be published in Play Console.")
    finally:
        if edit_id:
            try:
                api.edits().delete(packageName=a.package, editId=edit_id).execute()
            except Exception:
                pass

if __name__ == "__main__":
    main()
