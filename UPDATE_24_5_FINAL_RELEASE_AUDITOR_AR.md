# UPDATE 24.5 — مدقق الإصدار النهائي

## الغرض
أداة محلية للمبرمج لتدقيق مصدر Flutter وملف Android App Bundle قبل التسليم. لا ترفع التطبيق ولا تنشره ولا تتصل بحساب Google Play.

## المتطلبات
- Python 3.9 أو أحدث.
- Flutter SDK مع Dart، ويجب أن يكونا في PATH.
- `bundletool` في PATH.
- JDK يحتوي `jarsigner` و`keytool` في PATH.
- آخر `versionCode` من Play Console.
- بصمة SHA-256 لشهادة **Upload key certificate** من Play Console > Test and release / Setup > App integrity (قد تختلف تسمية القائمة حسب واجهة الحساب).

## التشغيل من جذر المشروع

### Windows PowerShell
```powershell
python tools/final_release_auditor.py `
  --project-root . `
  --aab build/app/outputs/bundle/release/app-release.aab `
  --previous-version-code 31001 `
  --upload-cert-sha256 "ضع_بصمة_UPLOAD_KEY_الحقيقية_هنا"
```

### Linux/macOS
```bash
python3 tools/final_release_auditor.py \
  --project-root . \
  --aab build/app/outputs/bundle/release/app-release.aab \
  --previous-version-code 31001 \
  --upload-cert-sha256 'ضع_بصمة_UPLOAD_KEY_الحقيقية_هنا'
```

استبدل `31001` بآخر رقم منشور/مستخدم فعلياً في Play Console. لا تعتمد الرقم المثال. يجب أن يكون رقم AAB أكبر منه. لا تضع بصمة تجريبية أو بصمة App signing certificate بدلاً من Upload key certificate.

## ما يفحصه
1. وجود ملفات المصدر الأساسية وتهيئة Gradle وManifest.
2. وجود Flutter SDK وتشغيل `flutter analyze` و`flutter test`.
3. وجود AAB وسلامة ZIP وملفاته الأساسية.
4. `bundletool validate` وقراءة Manifest XML من الوحدة `base`.
5. تطابق `applicationId` مع `com.taxiouargla.lite` وارتفاع `versionCode` عن آخر إصدار.
6. التحقق من توقيع AAB ومقارنة بصمة الشهادة مع Upload key certificate.
7. بصمة SHA-256 لملف AAB نفسه.

## التقارير
ينشئ السكربت في جذر المشروع:
- `UPDATE_24_5_RELEASE_AUDIT_REPORT_AR.txt`
- `UPDATE_24_5_RELEASE_AUDIT_REPORT.json`

أي فحص إلزامي فاشل يجعل النتيجة النهائية FAIL ورمز الخروج 1. غياب أداة مطلوبة أو تعذر تنفيذ اختبار Flutter لا يُعامل على أنه نجاح.

## حدود مهمة
- لا يمكن للسكربت ضمان قبول Google Play أو سلامة وظائف التطبيق أثناء الاستخدام.
- نجاح `flutter analyze` و`flutter test` لا يغني عن الاختبار على أجهزة حقيقية.
- نجاح AAB لا يعني أن إصدار Internal Testing أصبح متاحاً للمختبرين؛ يجب إكمال خطوات Play Console وإتاحة الإصدار للمختبرين.
- لا ترسل keystore أو كلمات المرور أو `key.properties` أو service account JSON. البصمة ليست المفتاح الخاص.
- لا تنفذ migrations على قاعدة الإنتاج ضمن هذا التدقيق.
