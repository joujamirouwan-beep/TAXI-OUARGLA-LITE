# UPDATE 12 — تطوير مركز الإشعارات

**المشروع:** طاكسي ورڨلة لايت — `com.taxiouargla.lite`

## التغيير البرمجي
أضيف مركز إشعارات محفوظ في Supabase ومربوط من شاشة الراكب والسائق. يولّد الخادم الإشعارات من تغيّرات الرحلات، وليس من Flutter، لمنع المستخدم من تزوير إشعار أو إرساله لحساب آخر.

### الأحداث المغطاة
- عند إنشاء طلب جديد: إشعار للسائقين المعتمدين والمتصلين.
- عند قبول الرحلة: إشعار للراكب.
- عند وصول السائق: إشعار للراكب.
- عند بدء الرحلة: إشعار للراكب.
- عند اكتمال الرحلة: إشعار للراكب.
- عند إلغاء رحلة مسندة: إشعار للراكب والسائق المسند إليه.

### حماية البيانات
- RLS على `user_notifications`.
- القراءة للمستخدم صاحب الإشعار فقط.
- التحديث مسموح لحقل `read_at` فقط.
- لا يوجد INSERT أو DELETE مباشر للمستخدمين.
- Trigger يعمل بصلاحياته المحددة، ولا يكشف مفاتيح الخدمة للتطبيق.

## الملفات الجديدة/المعدلة
- `supabase/migrations/20261118_007_in_app_notifications.sql`
- `lib/models/app_notification.dart`
- `lib/services/notification_service.dart`
- `lib/screens/notifications_screen.dart`
- `test/models/app_notification_test.dart`
- تعديل `lib/app/app_dependencies.dart`
- تعديل `lib/screens/rider_home_screen.dart`
- تعديل `lib/screens/driver_home_screen.dart`
- `docs/NOTIFICATIONS_STAGE_05_AR.md`

## طريقة التحقق المطلوبة
1. Backup ثم تطبيق Migration 007 على staging فقط بعد مراجعة schema الحي.
2. تشغيل `flutter pub get`.
3. تشغيل `dart format lib test`.
4. تشغيل `flutter analyze` و`flutter test`.
5. اختبار عزل الإشعارات بين حسابين مختلفين.
6. اختبار كل حدث من الأحداث أعلاه بحساب راكب وسائق معتمد.

## حالة الاختبارات في بيئة إعداد الحزمة
- فحص المصدر الساكن: 51/51 PASS.
- تم التأكد من وجود جميع الاستيرادات النسبية.
- لم تتوفر أدوات Flutter/Dart أو PostgreSQL في بيئة إعداد الحزمة؛ لذلك لم يُدّعَ نجاح `flutter analyze` أو `flutter test` أو تنفيذ SQL على قاعدة فعلية.
- هذه إشعارات داخل التطبيق وليست Push/FCM. يتطلب FCM إعداد Firebase الرسمي وملفات المشروع الأصلية وEdge Function، ولا يجوز وضع مفاتيح الخدمة في Flutter.

## ثوابت لا تتغير
لا تغيّر `applicationId`، ولا تضف أجرة أو عمولة أو محفظة أو دفعاً داخل التطبيق، ولا تتجاوز RPC الآمنة للرحلات، ولا تسمح للإدارة بإلغاء رحلة جارية أو مكتملة.
