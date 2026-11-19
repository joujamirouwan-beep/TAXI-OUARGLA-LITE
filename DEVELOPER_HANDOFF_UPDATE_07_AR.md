# تسليم هندسي — SOURCE UPDATE 07

## ما أضيف في هذه المراجعة

1. تقوية Migration `20261118_006_security_lifecycle_v3_1.sql` بفحص وجود `public.is_admin_user()` قبل إنشاء سياسات تعتمد عليه.
2. إضافة Preflight يرفض وجود overloads غير متوافقة لأسماء RPC الأساسية بدلاً من ترك عقد قديم قابل للاستدعاء بجانب العقد المعتمد.
3. إضافة Postflight يتحقق من تفعيل RLS على `rides` و`profiles`.
4. توسيع Postflight للتحقق من صلاحية EXECUTE لكل RPC المتوقعة، مع منع تنفيذ `anon` لها.
5. إضافة أداة مستقلة `tools/source_preflight.py` لإجراء فحوصات بنيوية قابلة لإعادة التشغيل دون Flutter SDK.

## نتائج فحص SOURCE UPDATE 07

`python tools/source_preflight.py`

**37/37 فحصاً ساكناً ناجحاً.** شملت سلامة Manifest، هوية التطبيق، حالات الرحلة الست، وجود RPC، حماية عمود الهاتف، منع الكتابة المباشرة إلى rides، غياب حقول التسعير والمحافظ والعمولات، وصحة الاستيرادات النسبية.

## حدود مهمة

هذه الفحوصات لا تثبت صحة SQL بالتنفيذ ولا تغني عن PostgreSQL. لم تتوفر في بيئة العمل أدوات Flutter/Dart أو PostgreSQL/Supabase أو Gradle، ولذلك لم تنفذ:

- `flutter pub get`
- `dart format`
- `flutter analyze`
- `flutter test`
- تشغيل Migration على قاعدة اختبار
- اختبارات تزامن فعلية أو RLS عبر أدوار Supabase
- بناء APK/AAB

كما أن Android Gradle Wrapper (`gradlew` و`gradle-wrapper.jar`) غير موجود في المصدر.

## تنبيه قبل الإنتاج

Migration V3.1 تفترض عقد SOURCE_UPDATE_05: `rides.status TEXT`، وإحداثيات السائق في `rides.driver_lat/driver_lng`، مع وجود `public.is_admin_user()` من المخطط السابق. إذا اختلفت قاعدة Supabase الحية، يجب أن يفشل Preflight وتُراجع البنية قبل أي تطبيق.

**الحالة: NO-GO للنشر.** هذه نسخة مصدر محسنة للمراجعة والتشغيل على بيئة اختبار، وليست إصداراً مبنياً أو Migration مثبتة على قاعدة حية.
