# إعداد البناء الآلي على GitHub — طاكسي ورڨلة لايت

أضيف هذا المسار: `.github/workflows/build-aab.yml`. البناء يدوي التشغيل فقط ولا ينشر التطبيق تلقائياً إلى Google Play.

## أسرار المستودع المطلوبة (Settings → Secrets and variables → Actions)

- `SIGNING_KEY`: ملف keystore الأصلي بصيغة Base64، وليس كلمة المرور.
- `KEY_PROPERTIES`: محتوى ملف الخصائص مع `storeFile=app/upload-keystore.jks` وحقول `storePassword` و`keyAlias` و`keyPassword`.
- `SUPABASE_URL`: عنوان مشروع Supabase.
- `SUPABASE_ANON_KEY`: مفتاح anon/public فقط. ممنوع وضع service_role أو أي مفتاح إداري في تطبيق الهاتف.

لا تضع القيم السرية في المحادثة أو في ملفات Git. استخدم مفتاح الرفع الأصلي نفسه؛ لا تنشئ مفتاحاً جديداً لتحديث تطبيق منشور.

## التشغيل

1. ارفع محتويات هذا الأرشيف إلى مستودع التطبيق مع الحفاظ على الملفات الحالية.
2. أضف الأسرار الأربعة أعلاه بعد التأكد من صحتها.
3. افتح Actions ثم `Build Taxi Ouargla Lite AAB` ثم Run workflow.
4. أدخل `build_number` أعلى من أعلى versionCode منشور فعلياً في Play Console، و`build_name` المناسب.
5. بعد نجاح جميع الفحوص، نزّل artifact باسم `taxi-ouargla-lite-release-aab`.

## حدود مهمة

- هذا Workflow يبني ويرفع artifact فقط؛ لا ينشر إلى Google Play.
- رقم 31001 هو رقم المصدر الحالي وليس دليلاً على آخر رقم في Play Console.
- يلزم التأكد من توافق قاعدة Supabase الحية وسياسة الخصوصية واختبار التطبيق على جهاز قبل النشر.
- لا تعتبر البناء ناجحاً حتى يظهر GitHub Actions باللون الأخضر ويُنتج artifact.
