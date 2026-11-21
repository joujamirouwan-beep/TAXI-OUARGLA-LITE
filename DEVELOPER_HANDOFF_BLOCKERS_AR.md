# تسليم عاجل للمبرمج — طاكسي ورڨلة لايت V3.10.1

**تاريخ التدقيق:** 18 نوفمبر 2026  
**الحكم:** NO-GO مؤقتاً — لا ترفع هذه الحزمة إلى Google Play قبل إغلاق البنود أدناه.

## نتيجة ما أمكن التحقق منه

- سلامة أرشيف ZIP: PASS، دون عضو تالف.
- فحص المصدر `python tools/source_preflight.py`: **51/51 PASS**.
- `applicationId` و`namespace`: `com.taxiouargla.lite`.
- أسماء الحالات الست للرحلة محفوظة.
- لا يوجد INSERT/UPDATE/DELETE مباشر لجدول `rides` من Flutter.
- لا توجد قراءة مباشرة لعمود `profiles.phone` من Flutter.
- لم تظهر حقول أجرة/عمولة/محفظة في منطق Flutter.

هذه نتائج فحص ساكن فقط، وليست دليلاً على أن التطبيق يُبنى أو يعمل على هاتف.

## الموانع الفعلية

1. الحزمة الحالية إعادة تجميع للمصدر المتاح وليست نسخة مؤكدة من مشروع Android الأصلي الكامل.
2. لا يوجد Flutter SDK أو Dart SDK في بيئة التدقيق؛ لذلك لم تنفذ أو تنجح أوامر `flutter pub get` أو `flutter analyze` أو `flutter test`.
3. ملفات Gradle Wrapper التنفيذية ناقصة: `android/gradlew` و`android/gradlew.bat` و`android/gradle/wrapper/gradle-wrapper.jar`.
4. لم يتم اختبار تسجيل OTP مع Supabase فعلياً.
5. لم يتم فحص قاعدة Supabase الحية أو تطبيق migrations على staging؛ لا تشغّل SQL على الإنتاج مباشرة.
6. لم يتم إعداد/التحقق من مفتاح توقيع Android App Bundle الأصلي.
7. لم يتم إنشاء APK/AAB، ولم يتم اختبار التطبيق على جهاز Android.

## المطلوب من المبرمج لإغلاق الإصدار

### أ — استعادة المشروع الأصلي

- دمج هذه الملفات مع **مشروع Flutter الأصلي الكامل** الذي يحتوي إعدادات Android وGradle Wrapper وموارد التطبيق الأصلية.
- عدم استبدال ملفات Android الأصلية عشوائياً، وعدم تغيير `applicationId`.
- التأكد من أن نقطة الدخول `lib/main.dart` تهيئ Supabase ثم `AppDependencies` مرة واحدة.
- توفير `SUPABASE_URL` و`SUPABASE_ANON_KEY` عبر إعدادات build آمنة؛ لا تضع مفاتيح service-role أو أسراراً في التطبيق.

### ب — الاختبارات الإلزامية

من جذر المشروع بعد تثبيت Flutter stable وAndroid SDK وJDK متوافق:

```bash
flutter --version
flutter pub get
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build apk --debug --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
```

عالج كل خطأ قبل الانتقال. اختبر على هاتف فعلي: إنشاء حساب راكب، إنشاء حساب سائق، OTP للدخول لحساب موجود، اعتماد السائق، طلب رحلة، قبولها، الوصول، بدء الرحلة، إنهاؤها، الإلغاء المسموح، تحديث الموقع، انقطاع الشبكة، وتبديل الحساب.

### ج — قاعدة البيانات والأمان

- خذ نسخة احتياطية أولاً.
- طابق schema الفعلي مع SQL V2.1 وMigration 006 قبل أي تنفيذ.
- جرّب migrations على staging، ثم نفذ فحوص RLS وACL وRPC postflight.
- لا تنفذ schema الكامل على قاعدة قائمة.

### د — إصدار Google Play

- استخدم مفتاح upload الأصلي، ولا تنشئ مفتاحاً بديلاً إذا كان التطبيق مرتبطاً بمفتاح سابق.
- تحقق من `versionCode` أعلى من آخر إصدار مرفوع.
- بعد نجاح الاختبارات والبناء:

```bash
flutter build appbundle --release --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
```

- افحص ملف AAB ووقّعه بالمفتاح الصحيح، ثم اختبر Internal testing قبل Production.

## قواعد المنتج التي يمنع تغييرها

- الاسم: **طاكسي ورڨلة لايت**.
- `applicationId`: **com.taxiouargla.lite**.
- لا توجد تسعيرة أو أجرة أو عمولة أو محفظة أو دفع داخل التطبيق؛ الاتفاق على الأجرة خارج التطبيق.
- حالات الرحلة المسموحة فقط: `searching`, `accepted`, `arrived`, `in_progress`, `completed`, `cancelled`.
- لكل سائق رحلة نشطة واحدة كحد أقصى، ولكل راكب رحلة نشطة واحدة كحد أقصى.
- الإدارة لا تلغي الرحلات الجارية أو المكتملة ولا تغير حالاتها.
- عمليات الرحلات الحساسة عبر RPC المحمية، وليس كتابة مباشرة إلى جدول `rides` من تطبيق الهاتف.

**لا تعلن أن التطبيق جاهز للنشر إلا بعد وجود نتيجة فعلية ناجحة لـ analyze وtest وAAB واختبار الهاتف وSupabase staging.**
