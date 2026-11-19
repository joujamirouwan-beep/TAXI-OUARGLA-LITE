#!/usr/bin/env python3
"""Static lock-order and lifecycle policy audit for migration 006."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "supabase/migrations/20261118_006_security_lifecycle_v3_1.sql"
source = SQL_PATH.read_text(encoding="utf-8")
failures = []
checks = []

def check(label, ok):
    checks.append((label, bool(ok)))
    if not ok:
        failures.append(label)

def function_body(name):
    pattern = re.compile(
        rf"CREATE OR REPLACE FUNCTION public\.{re.escape(name)}\s*\(.*?\)\s*"
        rf".*?AS \$\$(.*?)\$\$;",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(source)
    return match.group(1) if match else None

# Functions that lock both profile and ride rows must acquire profiles first.
for name in ("create_ride_secure", "accept_ride_secure", "update_driver_location_secure",
             "admin_set_driver_verification_secure"):
    body = function_body(name)
    check(f"{name}: function exists", body is not None)
    if body is not None:
        p_lock = re.search(r"FROM\s+public\.profiles\s+\w+.*?FOR\s+UPDATE", body, re.I | re.S)
        r_lock = re.search(r"FROM\s+public\.rides\s+\w+.*?FOR\s+UPDATE", body, re.I | re.S)
        check(f"{name}: if both rows are locked, profiles comes first",
              not (p_lock and r_lock) or p_lock.start() < r_lock.start())

# Ride-only lock functions must not acquire a profile row lock later.
for name in ("set_ride_status_secure", "cancel_searching_ride_secure",
             "rate_completed_ride_secure", "get_ride_contact_phone_secure"):
    body = function_body(name)
    check(f"{name}: function exists", body is not None)
    if body is not None:
        ride_lock = re.search(r"FROM\s+public\.rides\s+\w+.*?FOR\s+UPDATE", body, re.I | re.S)
        profile_lock = re.search(r"FROM\s+public\.profiles\s+\w+.*?FOR\s+UPDATE", body, re.I | re.S)
        check(f"{name}: no profile lock after ride lock", not (ride_lock and profile_lock and profile_lock.start() > ride_lock.start()))

# Business invariants are checked against the authoritative migration source.
admin_verification_body = function_body("admin_set_driver_verification_secure") or ""
admin_verification_body = function_body("admin_set_driver_verification_secure") or ""
checks_in_sql = {
    "rider one-active includes searching": "WHERE status IN ('searching','accepted','arrived','in_progress')" in source,
    "driver one-active excludes searching": "WHERE driver_id IS NOT NULL AND status IN ('accepted','arrived','in_progress')" in source,
    "admin verification function does not mutate rides": not bool(re.search(r"UPDATE\s+public\.rides|INSERT\s+INTO\s+public\.rides|DELETE\s+FROM\s+public\.rides", admin_verification_body, re.I)),
    "driver status progression is guarded": all(x in source for x in ("v_current='accepted' AND p_next_status='arrived'", "v_current='arrived' AND p_next_status='in_progress'", "v_current='in_progress' AND p_next_status='completed'")),
    "searching cancellation requires rider and no driver": "v_rider IS DISTINCT FROM v_uid OR v_status IS DISTINCT FROM 'searching' OR v_driver IS NOT NULL" in source,
    "driver cannot go offline during active ride": "IF NOT p_is_online AND EXISTS" in source and "لا يمكن قطع الاتصال أثناء وجود رحلة نشطة" in source,
    "admin cannot unverify driver during active ride": "IF NOT p_verified AND EXISTS" in source and "لا يمكن إلغاء اعتماد سائق لديه رحلة نشطة" in source,
}
for label, ok in checks_in_sql.items():
    check(label, ok)

for label, ok in checks:
    print(("PASS" if ok else "FAIL") + " | " + label)
print(f"RESULT: {len(checks)-len(failures)}/{len(checks)} checks passed")
if failures:
    sys.exit(1)
