# قائمة المبرمج — UPDATE 24.1

## قبل البناء
- [ ] استعادة `android/gradlew`, `android/gradlew.bat`, و`android/gradle/wrapper/gradle-wrapper.jar` الأصلية والمتوافقة مع Gradle 8.4.
- [ ] استخدام JDK 17 وFlutter SDK متوافق مع `pubspec.yaml`.
- [ ] تأكيد `applicationId` و`namespace` يساويان `com.taxiouargla.lite`.
- [ ] استعادة keystore الأصلي و`android/key.properties` محلياً، وعدم تغيير مفتاح الرفع.
- [ ] إدخال `SUPABASE_URL` و`SUPABASE_ANON_KEY` فقط؛ يمنع تضمين `service_role` داخل التطبيق.
- [ ] التحقق من آخر versionCode في Play Console واختيار رقم أعلى منه.
- [ ] تشغيل `flutter pub get`, `flutter analyze`, و`flutter test` ومعالجة الأخطاء.
- [ ] بناء `app-release.aab` والتحقق من ZIP integrity والتوقيع وSHA-256.

## قبل الرفع
- [ ] التأكد أن Service Account تابع لمشروع Play Console الصحيح ومخوّل للتطبيق.
- [ ] حفظ `play-api-key.json` محلياً فقط وعدم مشاركته.
- [ ] أخذ بصمة Upload certificate SHA-256 من Play Console ومقارنتها مع AAB.
- [ ] تشغيل `tools/upload_to_play_internal.py` لمسار `internal` فقط.
- [ ] تسجيل versionCode وSHA-256 ونتيجة الرفع.

## بعد الرفع
- [ ] تشغيل `tools/verify_upload.py` والتحقق من versionCode وحالة `draft`.
- [ ] مراجعة الإصدار يدوياً في Play Console ثم نشره للاختبار الداخلي.
- [ ] التحقق من أهلية المختبرين ورابط الانضمام وإتاحة الإصدار.
- [ ] اختبار التثبيت وتسجيل الدخول وSupabase والخريطة والرحلات والإشعارات والموقع على أجهزة فعلية.
- [ ] عدم الانتقال إلى production قبل اجتياز الاختبارات ومراجعة المتطلبات القانونية وسياسات Google Play.

## ما يسلّمه المبرمج
- [ ] `app-release.aab` فقط عبر قناة آمنة.
- [ ] SHA-256 للـ AAB.
- [ ] versionCode وversionName وapplicationId.
- [ ] نتائج `flutter analyze` و`flutter test`.
- [ ] نتيجة التحقق من التوقيع وبصمة شهادة الرفع (البصمة فقط، لا المفتاح).
- [ ] نتيجة `verify_upload.py` ورابط الاختبار الداخلي بعد نشر الإصدار.
