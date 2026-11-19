# دليل ربط تدفق الرحلة بالواجهات — V3.10.1

## حدود المسؤولية
- `RideFlowPolicy` يحدد ما ينبغي إظهاره أو تعطيله في الواجهة فقط.
- `RideRepository` يمرر أوامر الرحلات إلى `RideService` ويعرض Streams.
- RLS ودوال SECURITY DEFINER والفهارس في PostgreSQL هي الحماية الفعلية. لا تعتبر شروط الواجهة حماية أمنية.

## شاشة الراكب
1. عند فتح الشاشة: اشترك في `watchRiderRides(currentUserId)`.
2. اعرض الرحلة النشطة فقط وفق `status.isActiveForRider`، مع معالجة حالة وجود أكثر من سجل نشط كخطأ بيانات.
3. عند إنشاء طلب: تحقق من العناوين والإحداثيات، ثم استدع `repository.createRide(...)`.
4. لا تعرض زر الإلغاء إلا إذا `RideFlowPolicy.riderCanCancel(ride, currentUserId)`.
5. الإلغاء متاح فقط في `searching` وقبل إسناد سائق.
6. بعد `completed` اعرض التقييم إذا `RideFlowPolicy.riderCanRate(...)`.

## شاشة السائق
1. اشترك في `watchAvailableRides()` عند اتصال السائق، واعرض الطلبات ذات `searching` فقط.
2. لا تعرض طلب السائق نفسه؛ سياسة العرض تستعمل `RideFlowPolicy.driverCanAccept`.
3. عند القبول: استدع `repository.acceptRide(ride.id)` ثم انتظر تحديث Stream؛ لا تفترض النجاح من الضغط وحده.
4. أزرار الحالة تتبع `nextDriverStatus`: `accepted → arrived → in_progress → completed`.
5. أوقف تحديث الموقع بعد `completed` أو `cancelled`، ولا ترسل الموقع إلا لرحلة السائق المسندة والنشطة.
6. لا تسمح بإيقاف اتصال السائق أثناء رحلة نشطة؛ الخادم يفرض ذلك أيضاً.

## حالات الواجهة المطلوبة
- loading / empty / data / error لكل Stream.
- انقطاع الشبكة مع زر إعادة المحاولة دون تكرار أمر RPC تلقائياً.
- عند انتهاء المهلة أو تبدل الحساب: أعد قراءة الرحلة قبل إعادة أي أمر؛ قد يكون RPC قد نفذ رغم ضياع الاستجابة.
- عند `23505`: اعرض أن هناك رحلة نشطة بالفعل، ثم حدّث قائمة الرحلات.
- عند فشل القبول لأن سائقاً آخر سبقك: أزل الطلب من القائمة بعد وصول Stream.

## عقد الحالات
`searching`, `accepted`, `arrived`, `in_progress`, `completed`, `cancelled` فقط. لا تضف `en_route`.

## قبل الدمج
- طابق `pubspec.yaml` واسم package import `taxi_ouargla_lite` مع المشروع الفعلي.
- تحقق من أعمدة `rides` وRLS وRPC في Supabase الحقيقي.
- شغّل `flutter pub get`, `flutter analyze`, `flutter test` على مشروع Flutter الكامل.
