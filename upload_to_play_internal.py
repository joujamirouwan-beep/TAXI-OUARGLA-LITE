#!/usr/bin/env python3
"""Upload a signed Android App Bundle to Google Play's internal track as a draft."""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, zipfile
from pathlib import Path

PACKAGE_DEFAULT = "com.taxiouargla.lite"
SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]


def die(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def signing_fingerprint(path: Path) -> str:
    keytool = os.environ.get("KEYTOOL", "keytool")
    try:
        out = subprocess.check_output(
            [keytool, "-printcert", "-jarfile", str(path)],
            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace"
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        die(f"تعذر قراءة شهادة توقيع AAB بواسطة keytool: {exc}")
    match = re.search(r"SHA256:\s*([0-9A-Fa-f: ]{32,})", out, re.I)
    if not match:
        die("لم أستطع استخراج بصمة SHA-256 لشهادة التوقيع من مخرجات keytool.")
    return re.sub(r"[^0-9A-Fa-f]", "", match.group(1)).upper()


def list_version_codes(service, package: str, edit_id: str) -> list[int]:
    response = service.edits().tracks().list(packageName=package, editId=edit_id).execute()
    codes: list[int] = []
    for track in response.get("tracks", []):
        for release in track.get("releases", []):
            codes.extend(int(v) for v in release.get("versionCodes", []))
    return codes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aab", default="build/app/outputs/bundle/release/app-release.aab")
    ap.add_argument("--package", default=PACKAGE_DEFAULT)
    ap.add_argument("--track", default="internal", choices=["internal"])
    ap.add_argument("--service-account", default=os.environ.get("PLAY_SERVICE_ACCOUNT_JSON", "play-api-key.json"))
    ap.add_argument("--release-notes", default="إصلاحات وتحسينات — طاكسي ورڨلة لايت")
    ap.add_argument("--expected-cert-sha256", default=os.environ.get("EXPECTED_UPLOAD_CERT_SHA256", ""),
                    help="بصمة شهادة رفع AAB المتوقعة، 64 خانة hex، بدون فواصل")
    ap.add_argument("--dry-run", action="store_true", help="تحقق محلي فقط ولا يتصل بـ Google Play")
    args = ap.parse_args()

    aab = Path(args.aab).resolve()
    credentials_file = Path(args.service_account).resolve()
    if args.package != PACKAGE_DEFAULT:
        die(f"package name must remain {PACKAGE_DEFAULT}; refusing package {args.package!r}.")
    if not aab.is_file() or aab.stat().st_size == 0:
        die(f"AAB غير موجود أو فارغ: {aab}")
    try:
        with zipfile.ZipFile(aab) as zf:
            bad = zf.testzip()
            if bad:
                die(f"AAB ZIP integrity failed at entry: {bad}")
    except zipfile.BadZipFile:
        die("الملف ليس AAB/ZIP صالحاً.")

    jarsigner = os.environ.get("JARSIGNER", "jarsigner")
    try:
        subprocess.check_call([jarsigner, "-verify", str(aab)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        die("فشل jarsigner -verify؛ لن نرفع AAB غير موقّع أو غير صالح.")

    fingerprint = signing_fingerprint(aab)
    expected = re.sub(r"[^0-9A-Fa-f]", "", args.expected_cert_sha256).upper()
    if not re.fullmatch(r"[0-9A-F]{64}", expected or ""):
        die("حدد EXPECTED_UPLOAD_CERT_SHA256 أو --expected-cert-sha256 ببصمة الشهادة المعتمدة من Play Console.")
    if fingerprint != expected:
        die(f"بصمة شهادة AAB لا تطابق البصمة المعتمدة. Actual={fingerprint}, Expected={expected}")

    digest = sha256(aab)
    print(f"AAB: {aab}\nSHA-256: {digest}\nPackage: {args.package}\nUpload certificate SHA-256: {fingerprint}")
    if args.dry_run:
        print("DRY RUN PASS: local checks passed; no upload was performed.")
        return
    if not credentials_file.is_file():
        die(f"Service Account JSON غير موجود: {credentials_file}")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        die("ثبت المتطلبات أولاً: python -m pip install -r tools/requirements-play-upload.txt")

    creds = service_account.Credentials.from_service_account_file(str(credentials_file), scopes=SCOPES)
    service = build("androidpublisher", "v3", credentials=creds, cache_discovery=False)
    edit_id = None
    try:
        edit = service.edits().insert(packageName=args.package, body={}).execute()
        edit_id = edit["id"]
        existing = list_version_codes(service, args.package, edit_id)
        latest = max(existing, default=0)
        upload = service.edits().bundles().upload(
            packageName=args.package, editId=edit_id, media_body=str(aab),
            media_mime_type="application/octet-stream"
        ).execute()
        version_code = int(upload["versionCode"])
        if version_code <= latest:
            die(f"versionCode {version_code} ليس أكبر من أعلى versionCode معروف ({latest}). تم إلغاء التعديل غير المنشور.")
        track_body = {"track": args.track, "releases": [{
            "name": f"UPDATE 24.1 internal {version_code}",
            "versionCodes": [str(version_code)],
            "status": "draft",
            "releaseNotes": [{"language": "ar-DZ", "text": args.release_notes}],
        }]}
        service.edits().tracks().update(
            packageName=args.package, editId=edit_id, track=args.track, body=track_body
        ).execute()
        service.edits().commit(packageName=args.package, editId=edit_id).execute()
        print(f"UPLOAD COMMITTED AS DRAFT: track={args.track}, versionCode={version_code}")
        print("ملاحظة: الإصدار Draft غير متاح للمختبرين حتى يراجعه المسؤول وينشره من Play Console.")
    except Exception as exc:
        if edit_id:
            try:
                service.edits().delete(packageName=args.package, editId=edit_id).execute()
            except Exception:
                pass
        die(f"فشل الرفع/الحفظ عبر Google Play Developer API: {exc}")

if __name__ == "__main__":
    main()
