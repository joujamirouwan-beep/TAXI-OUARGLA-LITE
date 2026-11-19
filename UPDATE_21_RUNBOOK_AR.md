# UPDATE 21 — حزمة تحقق العقود واختبارات التزامن

## نتيجة مراجعة المصدر

الأرشيف المرجعي `V3.10.1_UPDATE_19_LOCK_ORDER_LIFECYCLE_AUDIT` يحتوي بالفعل على:
- `create_ride_secure(text,double precision,double precision,text,double precision,double precision)`
- `accept_ride_secure(uuid)`
- `set_ride_status_secure(uuid,text)`
- `set_driver_online_secure(boolean)`
- `admin_set_driver_verification_secure(uuid,boolean)`
- `get_ride_contact_phone_secure(uuid)`
- فهرسي PostgreSQL فريدين للرحلات النشطة.

**لا تضف RPCs بديلة** مثل `create_ride_request_secure` أو `get_ride_counterparty_contact_secure` إلى هذا المصدر قبل توحيد Flutter وSQL. ولا تضف تريغر تحقق ثانياً على `profiles.is_verified` بصورة عمياء: عمود `is_verified` غير قابل للتحديث مباشرة من دور `authenticated`، والتغيير الإداري يمر عبر `admin_set_driver_verification_secure` التي تقفل `profiles` أولاً ثم تفحص الرحلات النشطة. يجب اختبار هذه الدالة القائمة بدلاً من تكرار منطقها.

## A. فحص ساكن على بيئة Staging

```bash
psql "$STAGING_DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f supabase/tests/update_21_contract_assertions.sql
```

يجب أن تنتهي العبارة برسالة `PASS`، وألا يعيد استعلاما التكرارات أي صفوف.

## B. تجهيز بيانات pgbench

أنشئ في مشروع Staging فقط حساب راكب واحداً، وسائقاً موثقاً ومتصلًا، وطلبَي رحلة `searching` مستقلين لراكبين مختلفين. استخدم UUIDs اختبارية حقيقية من `auth.users` و`profiles` و`rides`، ولا تستخدم حسابات الإنتاج.

## C. سباق إنشاء طلبين للراكب نفسه

```bash
pgbench "$STAGING_DATABASE_URL" -n -c 8 -j 4 -t 10 \
  -D rider_id=RIDER_UUID \
  -f supabase/tests/pgbench_same_rider_create.sql
```

النجاح المتوقع: طلب نشط واحد كحد أقصى لهذا الراكب. ستظهر أخطاء متوقعة لمحاولات الزيادة؛ لا تستخدم `--exit-on-error` في هذا الاختبار.

## D. سباق قبول رحلتين من السائق نفسه

شغّل جلستين متوازيتين، كل واحدة تستهدف رحلة مختلفة للسائق نفسه:

```bash
pgbench "$STAGING_DATABASE_URL" -n -c 1 -j 1 -t 1 \
  -D driver_id=DRIVER_UUID -D ride_id=RIDE_A_UUID \
  -f supabase/tests/pgbench_same_driver_accept.sql &
pgbench "$STAGING_DATABASE_URL" -n -c 1 -j 1 -t 1 \
  -D driver_id=DRIVER_UUID -D ride_id=RIDE_B_UUID \
  -f supabase/tests/pgbench_same_driver_accept.sql &
wait
```

النجاح المتوقع: رحلة واحدة فقط تصبح `accepted` لهذا السائق؛ الطلب الآخر يبقى `searching` أو يعيد RPC رفضاً متوقعاً. نفّذ هذا الاختبار بعد تجهيز السائق والرحلتين في Staging فقط.
## E. فحوص يدوية إلزامية عبر حسابات Staging

1. سائق لديه رحلة `accepted` يحاول `set_driver_online_secure(false)` — يجب الرفض.
2. مسؤول يحاول `admin_set_driver_verification_secure(driver_id,false)` أثناء رحلة `accepted` أو `arrived` أو `in_progress` — يجب الرفض.
3. السائق يكمل الرحلة إلى `completed` ثم يعاد اختبار إلغاء الاعتماد — يجب السماح وفق سياسة الإدارة.
4. الإدارة تحاول تعديل أو إلغاء رحلة نشطة مباشرة — يجب أن تمنعها الصلاحيات/RPC contract.
5. مستخدم غير مشارك يحاول جلب هاتف الطرف الآخر — يجب ألا يحصل على بيانات.

## F. حدود الإثبات

- فحص SQL أعلاه يختبر تعريفات الكتالوج والبيانات الحالية، وليس سلوكاً متزامناً.
- pgbench يختبر التزامن الحقيقي فقط عند تشغيله على قاعدة Staging مع JWT claims وبيانات اختبار صحيحة.
- لا يمكن إعلان نجاح اختبار حي أو جاهزية Google Play قبل تنفيذ هذه الأوامر على مشروع Supabase الفعلي، وتشغيل Flutter/Android build من بيئة المبرمج.
- بعد الاختبارات، نظّف حسابات وطلبات الاختبار وفق إجراء Staging المعتمد.
