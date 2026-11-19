# رسالة تسليم المبرمج — UPDATE 24.5 FINAL

السلام عليكم،

أرفق لك حزمة UPDATE 24.5 FINAL RELEASE AUDITOR الخاصة بتطبيق طاكسي ورڨلة لايت.

قبل التشغيل:
1. افتح `tools/final_release_auditor.py`.
2. أدخل آخر versionCode الحقيقي من Play Console في `EXPECTED_MIN_VERSION_CODE`.
3. أدخل SHA-256 الحقيقي لشهادة **Upload key certificate** في `UPLOAD_KEY_SHA256`.
4. لا تستخدم قيماً تجريبية. إذا تركت إحدى القيمتين فارغة فسيتوقف المدقق برسالة FAIL.

شغّل من جذر المشروع:
`python tools/final_release_auditor.py --project-root . --aab build/app/outputs/bundle/release/app-release.aab`

سلّمني:
- `app-release.aab`
- `UPDATE_24_5_RELEASE_AUDIT_REPORT_AR.txt`
- `UPDATE_24_5_RELEASE_AUDIT_REPORT.json`
- صورة كاملة للطرفية Terminal
- تأكيد إتمام الفحص المزدوج اليدوي وفق `MANUAL_DOUBLE_CHECK_AR.md`

قواعد ثابتة:
- `applicationId = com.taxiouargla.lite` ممنوع تغييره.
- لا تغيير لمفتاح الرفع إلا عبر Reset رسمي وموافقة المالك.
- ممنوع إرسال keystore أو كلمات المرور أو key.properties أو Service Account JSON.
- Internal Testing فقط قبل أي نشر عام.
- لا تنشر ولا ترفع إلى Production قبل موافقتي الخطية الصريحة.

حتى لو ظهرت PASS، سأراجع الملف يدوياً. لا ترفع أي شيء للمتجر قبل أن أقول لك صراحة: «ارفع».
