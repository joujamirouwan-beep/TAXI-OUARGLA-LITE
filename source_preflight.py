#!/usr/bin/env python3
"""Offline structural checks for TAXI OUARGLA LITE source (not Flutter/DB tests)."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors, checks = [], []
def check(name, ok, detail=''):
    checks.append((name, bool(ok), detail))
    if not ok:
        errors.append(name + (': ' + detail if detail else ''))

pubspec = (ROOT / 'pubspec.yaml').read_text(encoding='utf-8')
check('pubspec exists and declares package', "name: taxi_ouargla_lite" in pubspec)
manifest_path = ROOT / 'android/app/src/main/AndroidManifest.xml'
try:
    manifest = ET.parse(manifest_path).getroot()
    ns = '{http://schemas.android.com/apk/res/android}'
    check('Android manifest parses', True)
    check('Internet permission exists', any(x.attrib.get(ns+'name') == 'android.permission.INTERNET' for x in manifest.findall('uses-permission')))
except Exception as exc:
    manifest = None
    check('Android manifest parses', False, str(exc))

gradle = (ROOT / 'android/app/build.gradle').read_text(encoding='utf-8')
check('applicationId preserved', "applicationId 'com.taxiouargla.lite'" in gradle)
check('namespace preserved', "namespace 'com.taxiouargla.lite'" in gradle)

states = {'searching','accepted','arrived','in_progress','completed','cancelled'}
status_file = (ROOT / 'lib/models/ride_status.dart').read_text(encoding='utf-8')
for state in states:
    check('ride state '+state, state in status_file)
check('legacy ongoing status absent', not re.search(r"['\"]ongoing['\"]", '\n'.join(p.read_text(errors='ignore') for p in (ROOT/'lib').rglob('*.dart'))))

migration = (ROOT/'supabase/migrations/20261118_006_security_lifecycle_v3_1.sql').read_text(encoding='utf-8')
for fn in ['create_ride_secure','accept_ride_secure','set_ride_status_secure','cancel_searching_ride_secure','update_driver_location_secure','set_driver_online_secure','rate_completed_ride_secure','get_ride_contact_phone_secure','admin_list_pending_drivers_secure','admin_set_driver_verification_secure','list_available_rides_secure','list_my_rides_secure','admin_list_rides_secure']:
    check('migration contains '+fn, ('FUNCTION public.'+fn) in migration)
check('migration is transactional', migration.strip().startswith('--') and 'BEGIN;' in migration and migration.rstrip().endswith('COMMIT;'))
check('phone column explicitly revoked', 'REVOKE SELECT (phone) ON TABLE public.profiles FROM PUBLIC, anon, authenticated;' in migration)
check('phone RPC locks ride', bool(re.search(r'get_ride_contact_phone_secure.*?FOR UPDATE', migration, re.S)))
check('migration blocks unexpected RPC overloads', 'unexpected RPC overload/signature exists' in migration)
check('migration verifies RLS in postflight', 'RLS is not enabled on rides and profiles' in migration)

notifications_migration = (ROOT/'supabase/migrations/20261118_007_in_app_notifications.sql').read_text(encoding='utf-8')
check('notification migration is transactional', notifications_migration.strip().startswith('--') and 'BEGIN;' in notifications_migration and notifications_migration.rstrip().endswith('COMMIT;'))
check('notification table has owner-scoped RLS', 'USING (user_id = auth.uid())' in notifications_migration and 'WITH CHECK (user_id = auth.uid())' in notifications_migration)
check('notification clients can only update read_at', 'GRANT UPDATE (read_at) ON TABLE public.user_notifications TO authenticated;' in notifications_migration)
check('busy drivers excluded from new-request notifications', "active_ride.status IN ('accepted', 'arrived', 'in_progress')" in notifications_migration)
check('notification trigger does not grant direct execution', 'REVOKE ALL ON FUNCTION public.create_ride_notifications_v1() FROM PUBLIC, anon, authenticated;' in notifications_migration)
check('core security postflight audit exists', (ROOT/'supabase/audit/core_security_postflight.sql').is_file())
core_postflight = (ROOT/'supabase/audit/core_security_postflight.sql').read_text(encoding='utf-8')
for core_guard in [
    'RPC is not SECURITY DEFINER',
    'unsafe function config',
    'incorrect client EXECUTE grants',
    'authenticated has direct rides DML privileges',
    'authenticated can read profiles.phone',
    'active-ride unique indexes are missing',
    'validated six-state ride constraint is missing',
]:
    check('core security postflight guards: '+core_guard, core_guard in core_postflight)
check('notification postflight audit exists', (ROOT/'supabase/audit/notifications_postflight.sql').is_file())
notification_postflight = (ROOT/'supabase/audit/notifications_postflight.sql').read_text(encoding='utf-8')
for audit_guard in [
    'RLS is disabled',
    'unexpected policy inventory',
    'column update grants are incorrect',
    'trigger function must be SECURITY DEFINER',
    'search_path/row_security config is unsafe',
    'directly executable by clients',
    'expected enabled rides notification trigger is missing',
]:
    check('notification postflight guards: '+audit_guard, audit_guard in notification_postflight)

def function_body(sql, function_name):
    match = re.search(r'CREATE OR REPLACE FUNCTION public\.' + re.escape(function_name) + r'\b.*?AS \$\$(.*?)\$\$;', sql, re.S | re.I)
    return match.group(1) if match else ''

for function_name in ['create_ride_secure', 'accept_ride_secure', 'update_driver_location_secure']:
    body = function_body(migration, function_name)
    profile_lock = body.find('FROM public.profiles')
    profile_for_update = body.find('FOR UPDATE', profile_lock) if profile_lock >= 0 else -1
    ride_read = body.find('FROM public.rides')
    ride_for_update = body.find('FOR UPDATE', ride_read) if ride_read >= 0 else -1
    # create_ride_secure has no ride row lock; its unique index is the final race guard.
    if function_name == 'create_ride_secure':
        check('create ride locks profile before insert and relies on unique active-ride index', profile_for_update >= 0 and 'INSERT INTO public.rides' in body)
    else:
        check(function_name + ' locks profile before ride', profile_for_update >= 0 and ride_for_update > profile_for_update)
check('admin RPCs expose no ride cancellation function', not re.search(r'FUNCTION public\.admin_\w*cancel|FUNCTION public\.admin_cancel', migration, re.I))
check('admin verification RPC does not update rides', 'UPDATE public.rides' not in function_body(migration, 'admin_set_driver_verification_secure'))

all_dart = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in (ROOT/'lib').rglob('*.dart'))
check('no direct rides INSERT/UPDATE/DELETE from Flutter', not re.search(r"\.from\(['\"]rides['\"]\)\s*\.\s*(insert|update|delete|upsert)\s*\(", all_dart, re.I))
check('no direct phone-column read from Flutter', not re.search(r"\.from\(['\"]profiles['\"]\).*?\.select\(['\"][^'\"]*\bphone\b", all_dart, re.I|re.S))
for forbidden in ['wallet','commission','fare_amount','price_per_km']:
    check('forbidden business field absent: '+forbidden, forbidden not in all_dart.lower())

missing = []
for dart in (ROOT/'lib').rglob('*.dart'):
    text = dart.read_text(encoding='utf-8', errors='ignore')
    for imp in re.findall(r"import\s+'([^']+)'", text):
        if imp.startswith('.') and not (dart.parent / imp).resolve().exists():
            missing.append(f'{dart.relative_to(ROOT)} -> {imp}')
check('relative Dart imports resolve', not missing, '; '.join(missing[:8]))

# User-facing screens must not interpolate raw backend/transport exceptions.
error_screens = [
    ROOT / 'lib/screens/auth/auth_gate_screen.dart',
    ROOT / 'lib/screens/admin_dashboard.dart',
    ROOT / 'lib/screens/ride_tracking_screen.dart',
    ROOT / 'lib/screens/rider_home_screen.dart',
    ROOT / 'lib/screens/driver_home_screen.dart',
]
auth_body = (ROOT / 'lib/screens/auth/auth_gate_screen.dart').read_text(encoding='utf-8')
check('auth screen distinguishes new and existing accounts', '_isNewAccount' in auth_body and 'الدخول إلى حساب موجود' in auth_body)
check('existing-account OTP omits signup metadata', ' : const {},' in auth_body and 'data: _isNewAccount' in auth_body)
check('existing-account OTP cannot silently create a new user', 'shouldCreateUser: _isNewAccount' in auth_body)
check('new-account profile fields are conditionally required', '_isNewAccount && _name.text.trim().length < 2' in auth_body)

for screen in error_screens:
    body = screen.read_text(encoding='utf-8', errors='ignore')
    check('safe error mapper wired: ' + screen.name + '/' + screen.parent.name,
          'AppErrorMessage.from' in body)
    raw_error_patterns = [r'Text\([^\n]*\$error', r'Text\([^\n]*\$e[\)\}]', r'snapshot\.error\}']
    leaks = [pattern for pattern in raw_error_patterns if re.search(pattern, body)]
    check('no raw exception interpolation: ' + screen.name + '/' + screen.parent.name,
          not leaks, '; '.join(leaks))

for name, ok, detail in checks:
    print(('PASS' if ok else 'FAIL') + ' | ' + name + ((' | '+detail) if detail else ''))
print(f'RESULT: {len(checks)-len(errors)}/{len(checks)} checks passed')
if errors:
    sys.exit(1)


# Execute the dedicated lock-order/lifecycle static audit.
import subprocess as _subprocess
_lock_audit = _subprocess.run(
    [sys.executable, str(ROOT/'tools/lock_order_lifecycle_audit.py')],
    capture_output=True, text=True
)
check('lock-order/lifecycle audit passes', _lock_audit.returncode == 0)
