# حالة المشروع — SOURCE UPDATE 07

- الاسم: طاكسي ورقلة لايت.
- Android Application ID: `com.taxiouargla.lite` محفوظ.
- السعر والعمولة والمحفظة: غير موجودة؛ الاتفاق على الأجرة خارج التطبيق.
- حالات الرحلة: searching, accepted, arrived, in_progress, completed, cancelled.
- أساس البيانات: `rides.status TEXT` مع CHECK، وموقع السائق في `rides.driver_lat/driver_lng`.
- Migration الأمنية: `supabase/migrations/20261118_006_security_lifecycle_v3_1.sql`.
- فحوص مصدر قابلة لإعادة التشغيل: `tools/source_preflight.py`.

## تحديثات SOURCE UPDATE 07

- إضافة كشف مبكر عن RPC overloads غير المتوافقة.
- إضافة فحص وجود `is_admin_user()` قبل الاعتماد على سياسات RLS.
- تقوية Postflight لفحص تفعيل RLS وصلاحيات EXECUTE لكل RPC.
- توثيق حدود الاختبارات التي لم تتوفر بيئتها.

## النتائج

- الفحص الساكن: 37/37 PASS.
- اختبارات Flutter: لم تنفذ لغياب Flutter/Dart SDK.
- Migration وRLS: لم تنفذ على قاعدة اختبار أو إنتاج.
- APK/AAB: لم يبنَ لغياب Gradle Wrapper والبيئة اللازمة.

**الحالة النهائية: NO-GO للنشر.**
