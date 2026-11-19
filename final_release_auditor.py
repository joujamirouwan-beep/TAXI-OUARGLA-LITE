#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Taxi Ouargla Lite UPDATE 24.5 — release auditor.

This tool is a pre-submission gate. It does not upload or publish anything.
Requires Python 3.9+, Flutter SDK, bundletool, and JDK (jarsigner/keytool).
Example (PowerShell):
  python tools/final_release_auditor.py --project-root . \
    --aab build/app/outputs/bundle/release/app-release.aab \
    --previous-version-code 31001 \
    --upload-cert-sha256 "AA:BB:..."
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

APP_ID = "com.taxiouargla.lite"
# يجب تعبئة القيمتين من Play Console قبل التشغيل، أو تمريرهما عبر CLI.
EXPECTED_MIN_VERSION_CODE: int | None = None
UPLOAD_KEY_SHA256: str | None = None
ANDROID_NS = "http://schemas.android.com/apk/res/android"

class Auditor:
    def __init__(self, root: Path, aab: Path, previous: int, expected_fp: str, timeout: int):
        self.root = root.resolve()
        self.aab = aab.resolve()
        self.previous = previous
        self.expected_fp = self.norm_fp(expected_fp)
        self.timeout = timeout
        self.results: list[dict[str, Any]] = []
        self.started = time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def norm_fp(value: str) -> str:
        return re.sub(r"[^0-9A-Fa-f]", "", value).upper()

    def record(self, name: str, ok: bool, detail: str, required: bool = True) -> None:
        self.results.append({"check": name, "status": "PASS" if ok else "FAIL", "required": required, "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}: {name} — {detail}")

    def command(self, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(args, cwd=str(cwd or self.root), text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  check=False, timeout=self.timeout)
        except FileNotFoundError:
            return subprocess.CompletedProcess(args, 127, f"الأداة غير موجودة: {args[0]}")
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or ""
            if isinstance(out, bytes): out = out.decode(errors="replace")
            return subprocess.CompletedProcess(args, 124, f"انتهت المهلة بعد {self.timeout} ثانية\n{out}")

    def source_checks(self) -> None:
        print("\n[1] تدقيق ملفات المصدر وإعدادات التطبيق")
        pubspec = self.root / "pubspec.yaml"
        gradle_candidates = [self.root / "android/app/build.gradle", self.root / "android/app/build.gradle.kts"]
        gradle = next((p for p in gradle_candidates if p.is_file()), None)
        self.record("pubspec.yaml", pubspec.is_file(), str(pubspec if pubspec.is_file() else "الملف مفقود"))
        if gradle is None:
            self.record("Android app Gradle config", False, "لم يُعثر على android/app/build.gradle أو build.gradle.kts")
        else:
            data = gradle.read_text(encoding="utf-8", errors="replace")
            app_id_ok = bool(re.search(r"applicationId\s*[= ]\s*['\"]" + re.escape(APP_ID) + r"['\"]", data))
            self.record("Gradle applicationId", app_id_ok, f"المتوقع {APP_ID}; الملف {gradle.relative_to(self.root)}")
        manifest = self.root / "android/app/src/main/AndroidManifest.xml"
        if manifest.is_file():
            try:
                root = ET.parse(manifest).getroot()
                self.record("Source AndroidManifest XML", root.tag == "manifest", f"root tag={root.tag}")
            except ET.ParseError as exc:
                self.record("Source AndroidManifest XML", False, str(exc))
        else:
            self.record("Source AndroidManifest XML", False, "ملف AndroidManifest.xml مفقود")
        lock = self.root / "pubspec.lock"
        self.record("pubspec.lock", lock.is_file(), "موجود" if lock.is_file() else "غير موجود؛ يجب توليده ومراجعته ضمن بيئة البناء")
        gitignore = self.root / ".gitignore"
        if gitignore.is_file():
            gi = gitignore.read_text(encoding="utf-8", errors="replace").lower()
            protected = ("key.properties" in gi and (".jks" in gi or "*.keystore" in gi or "keystore" in gi))
            self.record("Signing secrets ignored by Git", protected, "تحقق أساسي من استثناء key.properties وملفات keystore")
        else:
            self.record("Signing secrets ignored by Git", False, ".gitignore مفقود")

    def flutter_checks(self) -> None:
        print("\n[2] تحليل Flutter والاختبارات")
        flutter = shutil.which("flutter")
        self.record("Flutter SDK available", bool(flutter), flutter or "flutter غير موجود في PATH")
        if not flutter:
            self.record("flutter analyze", False, "تعذر التشغيل لغياب Flutter SDK")
            self.record("flutter test", False, "تعذر التشغيل لغياب Flutter SDK")
            return
        for label, args in [("flutter analyze", [flutter, "analyze"]), ("flutter test", [flutter, "test"] )]:
            proc = self.command(args)
            ok = proc.returncode == 0
            self.record(label, ok, f"exit={proc.returncode}\n{proc.stdout[-5000:]}")

    def aab_checks(self) -> None:
        print("\n[3] تدقيق ملف Android App Bundle")
        if not self.aab.is_file():
            self.record("AAB file exists", False, str(self.aab))
            return
        size = self.aab.stat().st_size
        self.record("AAB non-empty", size > 0, f"{size} bytes")
        if size == 0: return
        sha = hashlib.sha256()
        with self.aab.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                sha.update(chunk)
        self.aab_sha256 = sha.hexdigest()
        print(f"INFO: AAB file SHA-256 = {self.aab_sha256}")
        try:
            with zipfile.ZipFile(self.aab) as zf:
                bad = zf.testzip()
                names = set(zf.namelist())
                structural = bad is None and "BundleConfig.pb" in names and "base/manifest/AndroidManifest.xml" in names
                detail = "ZIP CRC سليم والملفات الأساسية موجودة" if structural else f"bad_entry={bad}; BundleConfig.pb={'yes' if 'BundleConfig.pb' in names else 'no'}; base manifest={'yes' if 'base/manifest/AndroidManifest.xml' in names else 'no'}"
                self.record("AAB ZIP structure", structural, detail)
        except (zipfile.BadZipFile, OSError) as exc:
            self.record("AAB ZIP structure", False, str(exc))
            return
        try:
            with zipfile.ZipFile(self.aab) as zf:
                flutter_libs = [n for n in zf.namelist() if re.fullmatch(r"base/lib/[^/]+/libflutter\\.so", n)]
                self.record("Flutter engine library libflutter.so", bool(flutter_libs),
                            ", ".join(flutter_libs) if flutter_libs else "لم يُعثر على libflutter.so داخل base/lib/<abi>/")
        except (zipfile.BadZipFile, OSError) as exc:
            self.record("Flutter engine library libflutter.so", False, str(exc))
        bt = shutil.which("bundletool")
        if not bt:
            self.record("bundletool available", False, "bundletool غير موجود في PATH")
            return
        v = self.command([bt, "version"])
        self.record("bundletool version", v.returncode == 0, v.stdout.strip()[:500])
        val = self.command([bt, "validate", f"--bundle={self.aab}"])
        self.record("bundletool validate", val.returncode == 0, f"exit={val.returncode}\n{val.stdout[-3000:]}")
        dump = self.command([bt, "dump", "manifest", f"--bundle={self.aab}", "--module=base"])
        if dump.returncode != 0:
            self.record("AAB manifest readable", False, dump.stdout[-3000:])
        else:
            try:
                root = ET.fromstring(dump.stdout)
                pkg = root.attrib.get("package", "")
                vc_raw = root.attrib.get(f"{{{ANDROID_NS}}}versionCode", "-1")
                vn = root.attrib.get(f"{{{ANDROID_NS}}}versionName", "")
                vc = int(vc_raw)
                self.record("AAB applicationId", pkg == APP_ID, f"actual={pkg}; expected={APP_ID}")
                self.record("AAB versionCode", vc > self.previous, f"actual={vc}; must be greater than Play Console latest {self.previous}")
                self.record("AAB versionName present", bool(vn.strip()), vn or "غير محدد")
            except (ET.ParseError, ValueError) as exc:
                self.record("AAB manifest parse", False, str(exc))
        self.signature_checks()

    def signature_checks(self) -> None:
        print("\n[4] التوقيع وشهادة Upload Key")
        jarsigner, keytool = shutil.which("jarsigner"), shutil.which("keytool")
        if not jarsigner or not keytool:
            self.record("JDK signing tools", False, "يلزم jarsigner وkeytool ضمن PATH")
            return
        verify = self.command([jarsigner, "-verify", "-certs", str(self.aab)])
        verified_text = "jar verified" in verify.stdout.lower()
        self.record("AAB JAR signature verification", verify.returncode == 0 and verified_text,
                    f"exit={verify.returncode}\n{verify.stdout[-2500:]}")
        cert = self.command([keytool, "-printcert", "-jarfile", str(self.aab)])
        matches = re.findall(r"SHA256:\s*([0-9A-Fa-f: ]+)", cert.stdout, flags=re.I)
        actual = self.norm_fp(matches[0]) if matches else ""
        valid_expected = len(self.expected_fp) == 64
        same = bool(actual) and len(actual) == 64 and valid_expected and actual == self.expected_fp
        self.record("Upload certificate SHA-256 match", same,
                    f"actual={actual or 'NOT FOUND'}; expected={self.expected_fp or 'INVALID / EMPTY'}")

    def finish(self) -> int:
        failed = [r for r in self.results if r["required"] and r["status"] != "PASS"]
        passed = len(self.results) - len(failed)
        overall = "PASS" if not failed and self.results else "FAIL"
        report = {"project": "TAXI OUARGLA LITE", "release_audit": "UPDATE 24.5", "application_id_expected": APP_ID,
                  "started_at": self.started, "project_root": str(self.root), "aab_path": str(self.aab),
                  "aab_sha256": getattr(self, "aab_sha256", None), "previous_version_code": self.previous,
                  "checks_passed": passed, "checks_failed": len(failed), "overall": overall, "results": self.results}
        out_json = self.root / "UPDATE_24_5_RELEASE_AUDIT_REPORT.json"
        out_txt = self.root / "UPDATE_24_5_RELEASE_AUDIT_REPORT_AR.txt"
        out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        lines = ["تقرير تدقيق إصدار طاكسي ورڨلة لايت — UPDATE 24.5", f"النتيجة: {overall}",
                 f"الفحوص الناجحة: {passed}", f"الفحوص الفاشلة: {len(failed)}", f"AAB SHA-256: {report['aab_sha256'] or 'غير متاح'}", ""]
        lines += [f"{r['status']}: {r['check']} — {r['detail']}" for r in self.results]
        lines += ["", "تنبيه: PASS يعني اجتياز الفحوص التي ينفذها هذا السكربت فقط؛ لا يضمن قبول Google Play ولا يغني عن الاختبار اليدوي وInternal Testing."]
        out_txt.write_text("\n".join(lines), encoding="utf-8")
        print("\n=== النتيجة النهائية ===")
        print(f"{overall}: {passed}/{len(self.results)} checks passed")
        print(f"التقرير: {out_txt.name}")
        print(f"JSON: {out_json.name}")
        if failed:
            print("لا تسلّم ولا ترفع الإصدار حتى إصلاح جميع الفحوص الفاشلة.")
            return 1
        print("اجتازت الحزمة الفحوص الآلية؛ يلزم اختبار Internal Testing ومراجعة Play Console قبل النشر.")
        return 0


def main() -> int:
    p = argparse.ArgumentParser(description="مدقق الإصدار النهائي لطاكسي ورڨلة لايت UPDATE 24.5")
    p.add_argument("--project-root", default=".", help="مجلد مشروع Flutter")
    p.add_argument("--aab", default="build/app/outputs/bundle/release/app-release.aab", help="مسار AAB نسبةً للمجلد الحالي أو مسار مطلق")
    p.add_argument("--previous-version-code", type=int, default=EXPECTED_MIN_VERSION_CODE, help="آخر versionCode مستخدم في Play Console؛ يجب أن يكون AAB أكبر منه")
    p.add_argument("--upload-cert-sha256", default=UPLOAD_KEY_SHA256, help="بصمة SHA-256 لشهادة Upload key certificate من Play Console")
    p.add_argument("--timeout", type=int, default=900, help="مهلة كل أمر بالثواني")
    a = p.parse_args()
    if a.previous_version_code is None:
        print("FAIL: EXPECTED_MIN_VERSION_CODE غير محدد. راجعه من Play Console > Release > آخر إصدار.")
        return 2
    if not a.upload_cert_sha256 or not a.upload_cert_sha256.strip():
        print("FAIL: UPLOAD_KEY_SHA256 غير محدد. انسخه من Upload key certificate في Play Console.")
        return 2
    root = Path(a.project_root).expanduser().resolve()
    aab = Path(a.aab).expanduser()
    if not root.is_dir():
        print(f"FAIL: project root not found: {root}"); return 2
    if not aab.is_absolute(): aab = (root / aab).resolve()
    fp = Auditor.norm_fp(a.upload_cert_sha256)
    if len(fp) != 64:
        print("FAIL: بصمة Upload certificate غير صالحة؛ يجب أن تحتوي 64 خانة hex (32 bytes). لا تستخدم قيمة تجريبية.")
        return 2
    if a.previous_version_code < 0:
        print("FAIL: previous-version-code لا يمكن أن يكون سالباً"); return 2
    audit = Auditor(root, aab, a.previous_version_code, a.upload_cert_sha256, a.timeout)
    print("=== TAXI OUARGLA LITE — UPDATE 24.5 FINAL RELEASE AUDITOR ===")
    audit.source_checks()
    audit.flutter_checks()
    audit.aab_checks()
    return audit.finish()

if __name__ == "__main__":
    raise SystemExit(main())
