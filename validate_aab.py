#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate Taxi Ouargla Lite AAB metadata and upload certificate.

Requires: Python 3.9+, Java JDK tools (bundletool, jarsigner, keytool).
Usage:
  python validate_aab.py --aab app-release.aab \\
    --previous-version-code 5 \\
    --expected-upload-cert-sha256 AA:BB:...:FF

The expected certificate fingerprint must come from Play Console > App integrity
> Upload key certificate. This script does not upload or publish the bundle.
"""
from __future__ import annotations
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EXPECTED_APP_ID = "com.taxiouargla.lite"
ANDROID_NS = "http://schemas.android.com/apk/res/android"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)


def norm_fp(value: str) -> str:
    return re.sub(r"[^0-9A-F]", "", value.upper())


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser(description="فحص AAB قبل تسليمه للمبرمج/المالك")
    ap.add_argument("--aab", default="app-release.aab", help="مسار ملف AAB")
    ap.add_argument("--previous-version-code", type=int, required=True,
                    help="آخر versionCode موجود في Play Console")
    ap.add_argument("--expected-upload-cert-sha256", required=True,
                    help="SHA-256 لشهادة Upload key certificate من Play Console")
    ns = ap.parse_args()

    aab = Path(ns.aab).expanduser().resolve()
    checks: list[bool] = []
    print("=== TAXI OUARGLA LITE — AAB VALIDATION ===")
    if not aab.is_file():
        fail(f"ملف AAB غير موجود: {aab}")
        return 1
    if aab.stat().st_size == 0:
        fail("ملف AAB فارغ")
        return 1
    digest = hashlib.sha256(aab.read_bytes()).hexdigest()
    print(f"INFO: AAB SHA-256 = {digest}")

    bundletool = shutil.which("bundletool")
    if not bundletool:
        fail("bundletool غير موجود في PATH")
        return 1
    btver = run([bundletool, "version"])
    checks.append(btver.returncode == 0)
    print(("PASS" if checks[-1] else "FAIL") + f": bundletool version: {btver.stdout.strip()}")

    print("[1] قراءة Manifest من AAB عبر bundletool")
    manifest = run([bundletool, "dump", "manifest", f"--bundle={aab}", "--module=base"])
    if manifest.returncode != 0:
        fail("bundletool لم يستطع قراءة Manifest: " + manifest.stdout.strip())
        checks.append(False)
        package = ""
        version_code = -1
        version_name = ""
    else:
        try:
            root = ET.fromstring(manifest.stdout)
            package = root.attrib.get("package", "")
            version_code = int(root.attrib.get(f"{{{ANDROID_NS}}}versionCode", "-1"))
            version_name = root.attrib.get(f"{{{ANDROID_NS}}}versionName", "")
            ok = package == EXPECTED_APP_ID
            checks.append(ok)
            print(("PASS" if ok else "FAIL") + f": applicationId = {package!r}; expected {EXPECTED_APP_ID}")
            ok = version_code > ns.previous_version_code
            checks.append(ok)
            print(("PASS" if ok else "FAIL") +
                  f": versionCode = {version_code}; must be > {ns.previous_version_code}")
            print(f"INFO: versionName = {version_name or '(غير محدد)'}")
        except (ET.ParseError, ValueError) as exc:
            fail(f"تعذر تحليل Manifest XML: {exc}")
            checks.extend([False, False])
            package, version_code, version_name = "", -1, ""

    print("[2] التحقق من توقيع AAB")
    jarsigner = shutil.which("jarsigner")
    keytool = shutil.which("keytool")
    if not jarsigner or not keytool:
        fail("jarsigner أو keytool غير موجود؛ ثبّت JDK وأضفه إلى PATH")
        checks.append(False)
    else:
        sig = run([jarsigner, "-verify", "-verbose", "-certs", str(aab)])
        sig_ok = sig.returncode == 0 and "jar verified" in sig.stdout.lower()
        checks.append(sig_ok)
        print(("PASS" if sig_ok else "FAIL") + ": jarsigner verification")
        if not sig_ok:
            print(sig.stdout[-2500:])

        cert = run([keytool, "-printcert", "-jarfile", str(aab)])
        found = re.findall(r"SHA256:\s*([0-9A-Fa-f: ]+)", cert.stdout)
        actual = norm_fp(found[0]) if found else ""
        expected = norm_fp(ns.expected_upload_cert_sha256)
        fp_ok = bool(actual) and len(expected) == 64 and actual == expected
        checks.append(fp_ok)
        print(("PASS" if fp_ok else "FAIL") + ": Upload certificate SHA-256 comparison")
        print(f"INFO: actual   = {':'.join(actual[i:i+2] for i in range(0, len(actual), 2)) if actual else 'NOT FOUND'}")
        print(f"INFO: expected = {ns.expected_upload_cert_sha256}")
        if not actual:
            print(cert.stdout[-2000:])

    print("[3] النتيجة")
    if checks and all(checks):
        print("PASS: اجتازت الفحوص المحددة. هذا لا يغني عن اختبار التطبيق أو مراجعة Play Console.")
        return 0
    print(f"FAIL: {sum(bool(x) for x in checks)}/{len(checks)} فحوص نجحت. لا ترفع هذا الملف.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
