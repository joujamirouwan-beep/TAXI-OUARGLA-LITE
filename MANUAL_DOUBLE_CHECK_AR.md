# الفحص اليدوي المزدوج — UPDATE 24.5

هذا الفحص إلزامي بعد نتيجة PASS الآلية.

- [ ] فك AAB أو اقرأ Manifest بواسطة bundletool وتأكد أن package/applicationId هو `com.taxiouargla.lite`.
- [ ] استخرج شهادة AAB بواسطة `keytool -printcert -jarfile app-release.aab`.
- [ ] طابق SHA-256 مع **Upload key certificate** وليس App signing certificate.
- [ ] تأكد أن versionCode داخل AAB أكبر من آخر versionCode في Play Console.
- [ ] افتح AAB كـ ZIP وتأكد من وجود `base/lib/<abi>/libflutter.so`.
- [ ] راجع تقريري TXT وJSON وصورة Terminal كاملة.
- [ ] اختبر الإصدار عبر Internal Testing فقط.

لا تعني أي نتيجة PASS موافقة على النشر العام. النشر ممنوع حتى موافقة المالك الخطية.
