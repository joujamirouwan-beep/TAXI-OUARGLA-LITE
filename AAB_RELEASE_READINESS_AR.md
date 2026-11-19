# تجهيز إصدار AAB — طاكسي ورڨلة لايت

## ما تم تجهيزه في هذه الحزمة
- إضافة إعداد توقيع Release في `android/app/build.gradle` ليقرأ القيم محلياً من `android/key.properties`.
- إضافة `android/key.properties.example` كقالب بلا أسرار.
- إضافة سكربت بناء موحد لـ Linux/macOS وWindows؛ يوقف العملية إذا غابت أدوات البناء أو ملفات التوقيع أو إعدادات Supabase.
- السكربت يشغّل `flutter pub get` ثم التنسيق والتحليل والاختبارات ثم يبني AAB ويتحقق من وجوده ويطبع SHA-256.

## موانع البيئة الحالية التي لم يمكن تجاوزها من الأرشيف
1. لا يوجد Flutter SDK أو Dart SDK في بيئة العمل الحالية، لذلك لا يمكن تشغيل التحليل أو الاختبارات أو بناء AAB هنا.
2. ملفات `android/gradlew` و`android/gradlew.bat` و`android/gradle/wrapper/gradle-wrapper.jar` غير موجودة في الأرشيف؛ ملف `gradle-wrapper.properties` وحده لا يكفي. يجب استعادة هذه الملفات من مشروع Android الأصلي لدى المبرمج أو توليدها بأداة Flutter/Gradle الموثوقة بعد أخذ نسخة احتياطية.
3. لا يوجد ملف مفتاح التوقيع الأصلي ولا `android/key.properties`. يجب استخدام نفس مفتاح الرفع/التوقيع المرتبط بالتطبيق المنشور؛ لا تنشئ مفتاحاً جديداً على سبيل التجربة.
4. لا تتوفر بيانات Supabase في هذه البيئة. استخدم Project URL وanon/publishable key فقط كـ dart-defines؛ ممنوع وضع service_role key داخل التطبيق.
5. يجب التأكد أن `BUILD_NUMBER` أكبر من آخر versionCode منشور في Play Console. القيمة الحالية في المصدر `31001`، ولا تفترض أنها صالحة قبل التحقق.
6. يجب اختبار migrations على staging، ثم خطة ترحيل إنتاجية مع نسخة احتياطية. لا تنفذ SQL على الإنتاج لمجرد بناء AAB.

## إعداد التوقيع محلياً
- انسخ `android/key.properties.example` إلى `android/key.properties`.
- املأ `storeFile`, `storePassword`, `keyAlias`, `keyPassword` محلياً.
- ضع ملف keystore الأصلي في المسار المحدد.
- لا ترسل هذه الملفات أو كلمات المرور عبر المحادثات، ولا ترفعها إلى Git. `.gitignore` يستثني `key.properties` وملفات keystore.

## بناء AAB على Linux/macOS
```bash
export SUPABASE_URL='https://YOUR_PROJECT.supabase.co'
export SUPABASE_ANON_KEY='YOUR_PUBLIC_ANON_KEY'
export BUILD_NUMBER='31002' # غيّره إلى رقم أعلى من آخر إصدار في Play Console
./tools/build_release_aab.sh
```

## بناء AAB على Windows PowerShell
```powershell
$env:SUPABASE_URL = 'https://YOUR_PROJECT.supabase.co'
$env:SUPABASE_ANON_KEY = 'YOUR_PUBLIC_ANON_KEY'
$env:BUILD_NUMBER = '31002' # غيّره إلى رقم أعلى من آخر إصدار في Play Console
.\tools\BUILD_AAB_WINDOWS.ps1
```

## مكان الناتج بعد نجاح البناء
`build/app/outputs/bundle/release/app-release.aab`

لا تعتبر الإصدار جاهزاً للمتجر إلا بعد نجاح `flutter analyze` و`flutter test` وبناء AAB بتوقيع الرفع الأصلي، ثم فحصه ورفعه إلى Play Console وإكمال متطلبات صفحة المتجر وسياسة الخصوصية وData safety واختبار المسار الفعلي للراكب والسائق.

## ثوابت المشروع
- `applicationId` و`namespace`: `com.taxiouargla.lite`.
- الاسم: طاكسي ورڨلة لايت.
- لا أجرة أو تسعيرة أو عمولة أو محفظة أو دفع داخل التطبيق.
- الرحلات الحساسة عبر RPC الآمنة فقط.
