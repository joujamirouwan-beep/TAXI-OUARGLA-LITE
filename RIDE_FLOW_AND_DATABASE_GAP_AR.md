# تدفق الرحلة وفجوة قاعدة البيانات — V3.10.1

## نتيجة المراجعة الفعلية للملفات المحفوظة

تمت مقارنة `lib/services/ride_service.dart` مع ملف SQL V2 المرجعي الموجود في مكتبة المشروع.

- `createRide`: يستخدم INSERT محدود الأعمدة في `rides`؛ وهذا يطابق منح INSERT وسياسة `rides_create_own_search_request` في المخطط المرجعي.
- `acceptRide`: يستدعي `accept_ride_secure(p_ride_id)` ويتوقع `BOOLEAN`؛ مطابق لتعريف SQL V2.
- `setRideStatus`: يستدعي `set_ride_status_secure(p_ride_id, p_next_status)`؛ مطابق.
- `cancelSearchingRide`: يستدعي `cancel_searching_ride_secure(p_ride_id)`؛ مطابق.
- `updateDriverLocation`: يستدعي `update_driver_location_secure(p_ride_id, p_lat, p_lng)`؛ مطابق.
- `setDriverOnline`: يستدعي `set_driver_online_secure(p_is_online)`؛ مطابق.
- `rateCompletedRide`: يستدعي `rate_completed_ride_secure(p_ride_id, p_rating)`؛ مطابق.

هذه مطابقة مصدرية للعقد المرجعي فقط، وليست تحققاً من قاعدة Supabase الفعلية.

## الفجوة المكتشفة

النسخة المحفوظة من SQL V2 تنشئ فهرساً فريداً جزئياً للسائق (`one_active_ride_per_driver`) لكنها لا تنشئ فهرساً مماثلاً للراكب. لذلك فإن قاعدة البيانات لا تفرض حالياً في هذا المخطط المرجعي شرط رحلة نشطة واحدة لكل راكب، رغم وجود التحقق في منطق التطبيق/المتطلبات.

## المعالجة المضافة

- `supabase/audit/one_active_ride_preflight.sql`: استعلامات قراءة فقط لفحص التكرارات والفهارس.
- `supabase/migrations/20261118_001_one_active_ride_per_rider.sql`: ترقية مستقلة تتحقق من عدم وجود تكرارات قبل إنشاء الفهرس.
- لا توجد أوامر DROP؛ إذا وجدت تكرارات أو كان اسم الفهرس مستخدماً، تتوقف الترقية برسالة واضحة.
- نطاق الرحلة النشطة للراكب: `searching`, `accepted`, `arrived`, `in_progress`.
- نطاق الرحلة النشطة للسائق: `accepted`, `arrived`, `in_progress`.

## إجراء الاعتماد

1. شغّل استعلامات `one_active_ride_preflight.sql` على قاعدة البيانات المستهدفة.
2. راجع الصفوف الناتجة؛ لا تحذف أو تعدل رحلات تلقائياً.
3. إذا لم توجد تكرارات، راجع تعريف الفهارس والسياسات الحالية.
4. نفّذ Migration فقط بعد التأكد من مطابقة الجدول الفعلي للمخطط.
5. أعد استعلام الفهرس رقم 4 للتحقق من وجوده وتعريفه الصحيح.

## قيود لم تتغير

- لا توجد عمولات أو محافظ أو خصومات مالية.
- لا توجد حالة `en_route`.
- لا تلغي الإدارة الرحلات الجارية أو المكتملة.
- تغييرات حالة الرحلة تبقى عبر RPC المقيّد في قاعدة البيانات.
- `com.taxiouargla.lite` ثابت.

**الحالة: NO-GO — PRODUCTION** إلى أن تُراجع نتائج قاعدة البيانات الفعلية، وتنجح اختبارات Flutter والبناء والتكامل.
