# تقرير التدقيق الهندسي والتسليم — TAXI OUARGLA LITE V3.10.1 / UPDATE 11

**التاريخ:** 18 نوفمبر 2026  
**الغرض:** تسليم نتائج قابلة للتحقق للمبرمج دون الادعاء ببناء أو نشر لم يحدث.

## 1) الثوابت الوظيفية التي يجب عدم تغييرها
- اسم العرض: طاكسي ورڨلة لايت.
- Android applicationId وnamespace: `com.taxiouargla.lite`.
- لا توجد أجرة/تسعيرة/عمولة/محفظة/دفع داخل التطبيق؛ الاتفاق على الأجرة خارج التطبيق.
- حالات الرحلة: `searching`, `accepted`, `arrived`, `in_progress`, `completed`, `cancelled`.
- رحلة نشطة واحدة كحد أقصى لكل راكب ولكل سائق.
- لا تلغي الإدارة رحلة `in_progress` أو `completed` ولا تغيّر حالتها.
- عمليات الكتابة الحساسة للرحلات عبر RPC فقط، وليس CRUD مباشر على `rides` من تطبيق الهاتف.
- لا يقرأ التطبيق `profiles.phone` مباشرة؛ رقم الاتصال عبر RPC المقيّدة بالمشاركين في رحلة نشطة.

## 2) نتائج أعيد تنفيذها على UPDATE 10
- سلامة ZIP: PASS (تم فتح الأرشيف وقراءة أعضائه دون خطأ).
- `python tools/source_preflight.py`: **51/51 PASS**.
- `applicationId` و`namespace`: مطابقان للمعرّف المعتمد.
- Android Manifest قابل للتحليل، ويتضمن INTERNET وACCESS_FINE_LOCATION وACCESS_COARSE_LOCATION.
- حالات الرحلة الست موجودة، ولم يظهر status قديم `ongoing` في فحص preflight.
- فحص المصدر لم يجد INSERT/UPDATE/DELETE مباشرًا على جدول `rides`.
- فحص المصدر لم يجد قراءة مباشرة لعمود `profiles.phone`.
- فحص المصدر لم يجد حقول wallet أو commission أو fare_amount أو price_per_km.
- لا توجد علامات TODO/FIXME أو UnimplementedError واضحة في `lib` وملفات migrations.

**تنبيه:** نتائج preflight فحوص ساكنة وليست تشغيلًا للتطبيق أو إثباتًا لصحة قاعدة Supabase الحية.

## 3) الموانع الدقيقة التي بقيت
1. الأرشيف يعرض نفسه صراحة كمصدر مُعاد بناؤه/مستكمل جزئيًا، وليس نسخة مؤكدة من المشروع الأصلي الذي أنشأه المبرمج.
2. الموجود `gradle-wrapper.properties` فقط؛ المفقود `android/gradlew` و`android/gradlew.bat` و`android/gradle/wrapper/gradle-wrapper.jar`.
3. لا يحتوي الأرشيف على `android/local.properties` (وهو ملف بيئي محلي عادةً ويجب توليده على جهاز البناء) ولا ملفات Android الأصلية الأخرى التي قد تكون في مشروع المبرمج.
4. بيئة التدقيق الحالية تحتوي Java فقط؛ Flutter SDK وDart SDK غير متاحين. لذلك لم يمكن تنفيذ `flutter pub get`, `dart format`, `flutter analyze`, `flutter test` أو بناء APK/AAB.
5. لم يتم الاتصال بمشروع Supabase فعلي أو تطبيق migrations على staging؛ لا يجوز تنفيذ Migration 006 على الإنتاج قبل مطابقة schema ونسخة احتياطية.
6. لم يتم التحقق من مفتاح توقيع التطبيق أو `versionCode` مقابل سجل Google Play.

## 4) تعليمات دمج مباشرة للمبرمج
- استخدم مشروع Flutter الأصلي الكامل باعتباره قاعدة الدمج؛ انقل إليه ملفات `lib/` و`test/` و`supabase/` والوثائق المطلوبة بعد مراجعة الفروقات.
- لا تستبدل مجلد Android الأصلي بمجلد Android المعاد بناؤه في هذا الأرشيف.
- حافظ على `applicationId = com.taxiouargla.lite` وعلى مفتاح التوقيع الأصلي.
- لا ترفع أو تشغّل schema الكامل على قاعدة قائمة. خذ backup، طابق schema، ثم اختبر migrations على staging أولًا.
- راجع Migration `20261118_006_security_lifecycle_v3_1.sql` مقابل قاعدة staging الفعلية، ثم نفّذ postflight لامتيازات RPC وRLS والقيود الفريدة.
- تأكد من تهيئة Supabase مرة واحدة في `lib/main.dart` ومن عدم وضع service-role key داخل التطبيق.

## 5) أوامر قبول الإصدار
من جذر **المشروع الأصلي بعد الدمج** وباستخدام Flutter stable وAndroid SDK وJDK متوافق:

```bash
flutter --version
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build apk --debug --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
```

بعد نجاح الاختبارات واختبار سيناريوهات OTP والراكب والسائق والإدارة وتدفق الرحلة وانقطاع الشبكة على staging وجهاز فعلي:

```bash
flutter build appbundle --release --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
```

ثم تحقق من توقيع AAB وversionCode واختبر Internal testing قبل Production.

## 6) قرار الإصدار

**الحالة: SOURCE PREFLIGHT PASS / BUILD NOT VERIFIED / STORE RELEASE NOT READY.**

هذا التقرير لا يصف التطبيق بأنه مكتمل أو منشور. يصبح الإصدار جاهزًا فقط عند إرفاق سجلات نجاح التحليل والاختبارات وبناء AAB والتوقيع واختبار staging والجهاز الفعلي.
