#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
fail() { printf 'ERROR: %s\n' "$1" >&2; exit 1; }

command -v flutter >/dev/null 2>&1 || fail "Flutter SDK غير مثبت أو غير موجود في PATH."
command -v dart >/dev/null 2>&1 || fail "Dart SDK غير موجود في PATH."
command -v java >/dev/null 2>&1 || fail "Java JDK غير موجود في PATH؛ يتطلب Android Gradle Plugin 8.3.2 بيئة JDK 17."
java -version 2>&1 | head -n1 | grep -Eq 'version "17([.]|")' || fail "إصدار Java الحالي ليس JDK 17؛ استخدم JDK 17 لهذا المشروع (AGP 8.3.2 / Gradle 8.4)."
command -v unzip >/dev/null 2>&1 || fail "أداة unzip مطلوبة لفحص سلامة AAB."
command -v jarsigner >/dev/null 2>&1 || fail "أداة jarsigner من JDK مطلوبة للتحقق من توقيع AAB."
[[ -x android/gradlew ]] || fail "android/gradlew غير موجود؛ استعد مجلد Android/Gradle Wrapper الأصلي من مشروع المبرمج ولا تنشئ Wrapper عشوائياً."
[[ -f android/gradle/wrapper/gradle-wrapper.jar ]] || fail "gradle-wrapper.jar مفقود من المشروع."
[[ -f android/key.properties ]] || fail "ملف android/key.properties غير موجود؛ أعد استخدام مفتاح التوقيع الأصلي للتطبيق."
for required in storeFile storePassword keyAlias keyPassword; do
  value="$(sed -n "s/^${required}=//p" android/key.properties | tail -n1 | tr -d '\r')"
  [[ -n "$value" ]] || fail "قيمة $required مفقودة من android/key.properties."
  [[ "$value" != REPLACE_LOCALLY ]] || fail "استبدل القيمة التجريبية $required في android/key.properties محلياً."
done
[[ -n "${SUPABASE_URL:-}" ]] || fail "عيّن متغير SUPABASE_URL قبل البناء."
[[ -n "${SUPABASE_ANON_KEY:-}" ]] || fail "عيّن متغير SUPABASE_ANON_KEY قبل البناء."
[[ "${BUILD_NUMBER:-}" =~ ^[1-9][0-9]*$ ]] || fail "عيّن BUILD_NUMBER رقماً صحيحاً أكبر من صفر، ويجب أن يكون أعلى من آخر إصدار على Google Play."

STORE_FILE="$(sed -n 's/^storeFile=//p' android/key.properties | tail -n1 | tr -d '\r')"
[[ -n "$STORE_FILE" ]] || fail "storeFile غير محدد في android/key.properties."
[[ -f "android/$STORE_FILE" ]] || [[ -f "$STORE_FILE" ]] || fail "ملف keystore المحدد غير موجود؛ لا تستبدله بمفتاح جديد."

printf '\n== Flutter version ==\n'
flutter --version
printf '\n== Dependencies ==\n'
flutter pub get
printf '\n== Format ==\n'
dart format lib test
printf '\n== Static analysis ==\n'
flutter analyze
printf '\n== Tests ==\n'
flutter test
printf '\n== Release AAB ==\n'
flutter build appbundle --release \
  --build-name="${BUILD_NAME:-3.10.1}" \
  --build-number="$BUILD_NUMBER" \
  --dart-define="SUPABASE_URL=$SUPABASE_URL" \
  --dart-define="SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY"

AAB="build/app/outputs/bundle/release/app-release.aab"
[[ -s "$AAB" ]] || fail "لم يتم إنشاء ملف AAB في المسار المتوقع."
printf '\n== AAB created ==\n%s\n' "$AAB"
unzip -t "$AAB" >/dev/null || fail "ملف AAB تالف أو غير مكتمل (ZIP integrity)."
jarsigner -verify "$AAB" >/dev/null 2>&1 || fail "تعذر التحقق من توقيع AAB؛ راجع إعدادات مفتاح الرفع."
printf 'AAB ZIP integrity: PASS\nAAB signature verification: PASS\n'
if command -v sha256sum >/dev/null 2>&1; then sha256sum "$AAB"; fi
