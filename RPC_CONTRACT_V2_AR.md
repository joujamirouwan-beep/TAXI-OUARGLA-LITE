# عقد التكامل المعتمد لهذه الحزمة — مرجع SQL V2

هذه الحزمة تتبع **عقد SQL V2 الموجود في حزمة V3.9**، وليس عقد RPC التجريبي الذي ظهر في Engineering Overlay السابق.

| الدالة | المعاملات | النتيجة في SQL V2 |
|---|---|---|
| `create_ride_secure` | `p_pickup_address`, `p_pickup_lat`, `p_pickup_lng`, `p_dropoff_address`, `p_dropoff_lat`, `p_dropoff_lng` | `JSONB` (`id`, `status`, `created_at`) |
| `accept_ride_secure` | `p_ride_id` | `BOOLEAN` |
| `set_ride_status_secure` | `p_ride_id`, `p_next_status` | `BOOLEAN` |
| `cancel_searching_ride_secure` | `p_ride_id` | `BOOLEAN` |
| `update_driver_location_secure` | `p_ride_id`, `p_lat`, `p_lng` | `BOOLEAN` |
| `set_driver_online_secure` | `p_is_online` | `BOOLEAN` |
| `rate_completed_ride_secure` | `p_ride_id`, `p_rating` | `BOOLEAN` |

إنشاء الرحلة يتم عبر `create_ride_secure` بستة معاملات للموقع والعناوين، ويستخرج الخادم المستخدم من `auth.uid()` ويثبت الحالة `searching` دون أن يقبل `driver_id` أو الحالة من العميل. أضيفت كذلك `get_ride_contact_phone_secure(p_ride_id)` للوصول إلى رقم الطرف الآخر للمشارك فقط أثناء الرحلة النشطة، و`admin_list_pending_drivers_secure()` لعرض طلبات اعتماد السائقين دون كشف الهاتف. لا تمنح صلاحية SELECT على عمود `profiles.phone`.

## حالات الرحلة

`searching`, `accepted`, `arrived`, `in_progress`, `completed`, `cancelled` فقط. لا توجد `en_route`.

- نشطة للراكب: `searching`, `accepted`, `arrived`, `in_progress`.
- نشطة للسائق: `accepted`, `arrived`, `in_progress`.
- لا يُسمح للإدارة بإلغاء أو تعديل رحلة جارية أو مكتملة.
- قاعدة البيانات وRLS/RPC هي حدود الأمان؛ تحقق Flutter ليس بديلاً عنها.

## حدود الاعتماد

هذا العقد مطابق لتعريفات الدوال في ملف SQL V2 المرجعي المرفق بالحزمة الأقدم، لكنه **لم يُثبت أنه يطابق قاعدة Supabase الفعلية**. يجب مطابقة أسماء الدوال والمعاملات والأنواع مع نتائج فحص قاعدة البيانات قبل الدمج أو الترحيل.
