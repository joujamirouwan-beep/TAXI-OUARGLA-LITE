#!/usr/bin/env python3
"""Static source/release audit for TAXI OUARGLA LITE UPDATE 22.
This does not connect to Supabase or build Flutter/Android artifacts.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "supabase/migrations/20261118_006_security_lifecycle_v3_1.sql").read_text(encoding="utf-8")
APP = (ROOT / "android/app/build.gradle").read_text(encoding="utf-8")
DART = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "lib").rglob("*.dart"))
checks=[]
def check(label, ok):
    checks.append((label, bool(ok)))

def fn(name):
    m = re.search(rf"CREATE OR REPLACE FUNCTION public\.{re.escape(name)}\s*\(.*?\).*?AS \$\$(.*?)\$\$;", SQL, re.I|re.S)
    return m.group(1) if m else ""

# Release identity and lifecycle domain.
check("Android namespace is canonical", "namespace 'com.taxiouargla.lite'" in APP)
check("Android applicationId is canonical", "applicationId 'com.taxiouargla.lite'" in APP)
check("exact six ride states are constrained", all(x in SQL for x in ["'searching'", "'accepted'", "'arrived'", "'in_progress'", "'completed'", "'cancelled'"]))
check("rider active index includes searching and assigned states", "uq_rides_one_active_trip_per_rider" in SQL and "WHERE status IN ('searching','accepted','arrived','in_progress')" in SQL)
check("driver active index excludes searching", "uq_rides_one_active_trip_per_driver" in SQL and "WHERE driver_id IS NOT NULL AND status IN ('accepted','arrived','in_progress')" in SQL)

# Canonical RPCs and identity derivation.
for name in ["create_ride_secure", "accept_ride_secure", "set_ride_status_secure", "set_driver_online_secure", "admin_set_driver_verification_secure", "get_ride_contact_phone_secure"]:
    check(f"canonical RPC exists: {name}", bool(fn(name)))
check("ride creation derives identity from auth.uid", "auth.uid()" in fn("create_ride_secure"))
check("ride acceptance derives identity from auth.uid", "auth.uid()" in fn("accept_ride_secure"))
check("driver offline is blocked during active ride", "IF NOT p_is_online AND EXISTS" in fn("set_driver_online_secure") and "accepted','arrived','in_progress" in fn("set_driver_online_secure"))
check("admin verification removal blocked during active ride", "IF NOT p_verified AND EXISTS" in fn("admin_set_driver_verification_secure"))
check("admin verification does not mutate rides", not re.search(r"(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+public\.rides", fn("admin_set_driver_verification_secure"), re.I))
check("driver lifecycle progression is restricted", all(x in fn("set_ride_status_secure") for x in ["v_current='accepted' AND p_next_status='arrived'", "v_current='arrived' AND p_next_status='in_progress'", "v_current='in_progress' AND p_next_status='completed'"]))
check("contact lookup limits access to active ride participants", all(x in fn("get_ride_contact_phone_secure") for x in ["v_status NOT IN ('accepted','arrived','in_progress')", "v_uid=v_rider", "v_uid=v_driver"]))

# Client-side safety boundaries.
check("Flutter does not directly write rides", not re.search(r"\.from\(['\"]rides['\"]\)\s*\.\s*(insert|update|upsert|delete)", DART, re.I))
check("Flutter does not directly select profiles.phone", not re.search(r"\.from\(['\"]profiles['\"]\)\s*\.\s*select\s*\(['\"][^'\"]*\bphone\b", DART, re.I))
check("experimental alternate RPC names are not used", not any(x in DART for x in ["create_ride_request_secure", "get_ride_counterparty_contact_secure"]))

# Runtime/build blockers are explicit evidence, not assumed away.
wrapper = ROOT / "android/gradlew"
wrapper_jar = ROOT / "android/gradle/wrapper/gradle-wrapper.jar"
blockers = []
if not wrapper.exists(): blockers.append("android/gradlew missing")
if not wrapper_jar.exists(): blockers.append("android/gradle/wrapper/gradle-wrapper.jar missing")

failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("PASS" if ok else "FAIL") + " | " + name)
print(f"RESULT: {len(checks)-len(failed)}/{len(checks)} static checks passed")
for item in blockers:
    print("BLOCKER | " + item)
if failed:
    sys.exit(1)
