# UPDATE 22 — التدقيق الأمني النهائي وتجهيز التسليم

## مرجع العمل
الأرشيف الأساسي: `Taxi_Ouargla_Lite_V3.10.1_UPDATE_19_LOCK_ORDER_LIFECYCLE_AUDIT`.
أُدمجت ملفات اختبارات UPDATE 21 في `supabase/tests/` وأضيف مدقق مصدر مستقل.

## نتائج التدقيق الساكن
- `tools/source_preflight.py`: **77/77 PASS** عند إعداد هذه الحزمة.
- `tools/lock_order_lifecycle_audit.py`: **23/23 PASS**.
- `tools/update_22_release_audit.py`: يفحص هوية Android وعقود RPC والحالات الست وحدود وصول Flutter ووجود Gradle Wrapper.
- applicationId وnamespace ثابتان: `com.taxiouargla.lite`.

## قرار أمني: لا نضيف Trigger ثانياً لإلغاء اعتماد السائق
المصدر المرجعي لا يسمح للعميل authenticated بتحديث `profiles.is_verified` مباشرة، ويجعل التغيير الإداري يمر عبر `admin_set_driver_verification_secure`.
هذه الدالة تقفل سجل `profiles` أولاً ثم تمنع إلغاء الاعتماد عند وجود رحلة `accepted` أو `arrived` أو `in_progress`.
إضافة Trigger مستقل الآن تكرر المنطق وقد تخلق عقداً متعارضة. يجب اختبار RPC الموجودة بدلاً من تكرارها.

## حدود اختبارات التزامن
ملفات `supabase/tests/pgbench_same_rider_create.sql` و`pgbench_same_driver_accept.sql` هي أدوات تشغيل وليست نتائج اختبار حي. يجب تشغيلها على STAGING مع حسابات وبيانات اختبار وJWT claims صحيحة. لا تستخدم قاعدة الإنتاج للاختبارات المتنافسة.

## حواجز الإصدار الحالية
- لا يوجد `android/gradlew` ولا `gradle-wrapper.jar` في الأرشيف الحالي.
- لم يتم تشغيل Flutter/Dart analyzer أو الاختبارات لعدم توفر SDK في بيئة التدقيق.
- لم تُطبّق migrations على Supabase STAGING ولم تُراجع نتائج RLS/ACL الحية.
- لم يُنتج AAB ولم يتم توقيعه أو رفعه إلى Google Play.

**قرار النشر: NO-GO حتى إغلاق الحواجز أعلاه.**

## أوامر التحقق
```bash
python tools/source_preflight.py
python tools/lock_order_lifecycle_audit.py
python tools/update_22_release_audit.py
python -m zipfile -t Taxi_Ouargla_Lite_V3.10.1_UPDATE_22_SOURCE_AUDIT.zip
```

## أوامر STAGING
راجع `supabase/tests/UPDATE_21_RUNBOOK_AR.md` وشغّل `update_21_contract_assertions.sql` ثم اختبارات pgbench المتوازية. سجّل النتائج الفعلية ووقت التنفيذ ونسخة PostgreSQL قبل تغيير قرار النشر.
