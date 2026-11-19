# تقرير تنفيذ الأمان ودورة حياة الرحلة — V3.1

## أساس المطابقة
تمت مطابقة التغييرات مع مصدر `SOURCE_UPDATE_05` الموجود في الأرشيف.

**ملاحظة بنيوية حاسمة:** المخطط المرجعي في هذا الأرشيف يعرّف `public.rides.status` على أنه `TEXT` مع CHECK للحالات الست، ولا يعرّف `public.ride_status_enum`. كما يخزن إحداثيات السائق في `rides.driver_lat` و`rides.driver_lng` ولا يعرّف جدول `public.driver_locations` أو `public.ride_ratings`. لذلك تم إعداد Migration V3.1 على هذا العقد الفعلي، مع فشل Preflight إذا كانت قاعدة Supabase الحية مختلفة. لا يجوز تحويل status إلى ENUM أو إضافة جداول جديدة دون مراجعة قاعدة الإنتاج وعقود Flutter.

## التعديلات

1. إضافة `supabase/migrations/20261118_006_security_lifecycle_v3_1.sql`.
2. جرد وحذف سياسات rides القديمة ثم إنشاء سياسة واحدة لا تكشف طلبات البحث للسائقين عبر SELECT مباشر.
3. إعادة بناء سياسات profiles لحصر القراءة في الملف الشخصي والعلاقات المصرح بها والإدارة.
4. سحب امتيازات الجدول والأعمدة القديمة على profiles وrides، ثم منح الحد الأدنى اللازم؛ لا يوجد SELECT على `profiles.phone`.
5. إضافة RPC قراءة محكومة: `list_available_rides_secure`, `list_my_rides_secure`, `admin_list_rides_secure`.
6. إعادة تأمين RPC دورة الحياة، مع التحقق الصريح من NULL والمدخلات والحالة والهوية.
7. الإبقاء على عقد `create_ride_secure` كما يتوقعه Flutter: ستة معاملات بالترتيب الحالي ونتيجة JSONB تحتوي `id`, `status`, `created_at`.
8. دالة الهاتف تقفل صف الرحلة `FOR UPDATE` قبل فحص المشاركة والحالة، ثم تقرأ هاتف الطرف الآخر دون قفل profiles.
9. إضافة فحوصات Postflight توقف المعاملة عند بقاء صلاحية هاتف أو كتابة مباشرة أو سياسة rides غير متوقعة أو نقص الفهارس.
10. تحويل مصادر قراءة الرحلات في Flutter من Realtime/SELECT عام إلى RPC polling كل 5–8 ثوانٍ، لأن الطلبات المتاحة لم تعد مكشوفة عبر RLS.
11. تحويل فحص الرحلة النشطة قبل خروج السائق إلى `list_my_rides_secure`.

## ملفات Flutter المعدلة

- `lib/repositories/ride_data_source.dart`
- `lib/services/trip_service.dart`
- `lib/screens/admin_dashboard.dart`
- `lib/screens/driver_home_screen.dart`

## حدود الاعتماد

- لم تُشغّل Migration على Supabase.
- لم يُنفذ SQL على قاعدة اختبار أو إنتاج؛ لذلك صحة التنفيذ الفعلية لم تثبت بعد.
- لم يتوفر Flutter/Dart SDK في بيئة الفحص؛ لم تُشغّل `flutter pub get`, `dart format`, `flutter analyze`, `flutter test`.
- مجلد Android لا يحتوي `gradlew` أو `gradle-wrapper.jar`؛ لا يمكن بناء APK/AAB من هذه الحزمة كما هي.
- يجب مطابقة Preflight مع قاعدة Supabase الحية قبل التطبيق. إذا كانت القاعدة تستخدم ENUM أو جدول driver_locations أو ride_ratings، تتوقف هذه النسخة عمداً ويجب إنشاء migration توافق منفصلة.

## قرار النشر

`NO-GO`. هذه حزمة مصدر محدثة للمراجعة والدمج، وليست إصداراً مثبتاً أو مبنياً أو صالحاً للنشر بعد.
