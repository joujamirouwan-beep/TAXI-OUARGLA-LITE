# تهيئة التطبيق وربط الاعتماديات

لا تضع مفاتيح فعلية داخل الملفات أو الحزمة. استخدم إعدادات بيئة آمنة للمشروع المحلي، ولا تشارك `service_role` مطلقاً مع تطبيق الهاتف.

## ترتيب main

1. `WidgetsFlutterBinding.ensureInitialized()`.
2. `Supabase.initialize(url: ..., anonKey: ...)` باستخدام إعدادات المشروع الصحيحة.
3. `AppDependencies.initialize(Supabase.instance.client)` مرة واحدة.
4. `runApp(...)`.
5. في جذر الواجهة، استخدم `AuthWrapper` ثم `buildProfileRouter` كما في `AUTH_ROUTING_AR.md`.

لا تهيئ `AppDependencies` داخل `build` أو داخل `buildProfileRouter`. الحاوية singleton ولا توفر reset مقصوداً أثناء التشغيل الطبيعي.

## إعداد Android

حافظ على `applicationId` و`namespace` المتوافقين مع المشروع الأصلي، وعلى الأقل لا تغيّر:

`com.taxiouargla.lite`

لا تستبدل ملفات Gradle أو Manifest من الحزم القديمة دون مقارنة إعدادات المشروع الفعلية.
