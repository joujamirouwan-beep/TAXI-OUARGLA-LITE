# UPDATE 24.5 FINAL — مدقق الإصدار النهائي

## قبل التشغيل — إلزامي
افتح `tools/final_release_auditor.py` واملأ القيمتين من بيانات تطبيقك الحقيقية:

```python
EXPECTED_MIN_VERSION_CODE = None  # آخر versionCode مستخدم/موجود في Play Console
UPLOAD_KEY_SHA256 = None          # SHA-256 لشهادة Upload key certificate
```

لا تترك أي قيمة `None`. عند تركها فارغة يتوقف السكربت فوراً برسالة `FAIL`.
يمكن بدلاً من ذلك تمرير القيم عبر وسيطَي التشغيل `--previous-version-code` و`--upload-cert-sha256`.
لا تستخدم أرقاماً أو بصمات أمثلة أو قيماً وهمية. لا تخلط بين Upload key certificate وApp signing certificate.

## المتطلبات
- Python 3.10 أو أحدث.
- Flutter SDK وDart ضمن PATH.
- `bundletool` ضمن PATH.
- JDK يتضمن `jarsigner` و`keytool` ضمن PATH.

## التشغيل
من جذر مشروع Flutter:

```bash
python tools/final_release_auditor.py --project-root . --aab build/app/outputs/bundle/release/app-release.aab
```

## ما يفحصه المدقق
- ملفات المصدر الأساسية وإعداد Gradle و`applicationId`.
- `flutter analyze` و`flutter test`.
- وجود AAB وسلامة ZIP ومكوناته الأساسية.
- وجود `libflutter.so` ضمن مكتبات ABI في AAB.
- `bundletool validate` وقراءة Manifest عبر bundletool.
- `applicationId = com.taxiouargla.lite` وكون versionCode أعلى من آخر رقم Play Console.
- صحة توقيع AAB ومطابقة SHA-256 لشهادة Upload key certificate.
- إنشاء SHA-256 لملف AAB نفسه.

أي فحص إلزامي يفشل يجعل النتيجة النهائية `FAIL` ورمز الخروج غير صفري. لا تعتبر تعذر تنفيذ أداة أو اختبار نجاحاً.

## الفحص المزدوج اليدوي — مطلوب حتى مع PASS
1. فك/قراءة AAB باستخدام bundletool، وتحقق من `applicationId`.
2. نفّذ `keytool -printcert -jarfile app-release.aab` وقارن SHA-256 مع **Upload key certificate** في Play Console.
3. قارن `versionCode` الموجود في AAB مع Play Console، وتأكد أنه أعلى من آخر رقم مستخدم.
4. افتح AAB كأرشيف ZIP وتأكد من وجود `base/lib/<abi>/libflutter.so`.
5. نفّذ تثبيتاً واختباراً عملياً على Internal Testing قبل أي نشر عام.

## التقارير والتسليم
ينشئ المدقق:
- `UPDATE_24_5_RELEASE_AUDIT_REPORT_AR.txt`
- `UPDATE_24_5_RELEASE_AUDIT_REPORT.json`

سلّم AAB والتقريرين وصورة كاملة للطرفية (Terminal). التقرير ليس موافقة على النشر، ولا يثبت وحده قبول Google Play أو سلامة كل وظائف التطبيق.

## حماية الأسرار
ممنوع إرسال `keystore.jks` أو ملفات `key.properties` أو كلمات المرور أو Service Account JSON عبر واتساب أو إرفاقها بالحزمة. لا يرفع هذا السكربت التطبيق ولا ينشره.
