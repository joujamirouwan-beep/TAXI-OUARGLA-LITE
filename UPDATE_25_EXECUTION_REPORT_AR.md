# تقرير تنفيذ ومراجعة UPDATE 25 — طاكسي ورڨلة لايت

تاريخ التنفيذ: 2026-11-18
المصدر المفحوص: `Taxi_Ouargla_Lite_V3.10.1_UPDATE_24_5_FINAL_RELEASE_AUDITOR.zip` مع أرشيف المصدر `Taxi_Ouargla_Lite_V3.10.1_SOURCE_UPDATE_09.zip`.

## نتائج الفحوص المنفذة فعلياً

| الفحص | النتيجة | التفسير |
|---|---:|---|
| سلامة أرشيف ZIP للمصدر | PASS | `ZipFile.testzip()` لم يجد ملفات تالفة |
| source_preflight.py | 77/77 PASS | فحوص ساكنة للمصدر وقواعد الرحلات والأمان |
| lock_order_lifecycle_audit.py | 23/23 PASS | فحص ساكن لترتيب الأقفال ودورة حياة الرحلة |
| update_22_release_audit.py | 21/21 PASS | فحوص ساكنة لعقود RPC وقواعد التطبيق |
| update_24_android_preflight.py | 10/16 PASS | ستة موانع بناء موضحة أدناه |
| Python tools syntax | PASS | كل ملفات Python في tools اجتازت `py_compile` |
| Flutter analyze / test | NOT RUN | Flutter وDart غير مثبتين في بيئة التنفيذ |
| Gradle build / AAB | NOT RUN | Gradle wrapper ناقص وFlutter SDK غير متوفر |
| توقيع AAB | NOT RUN | لا يوجد AAB أو إعداد توقيع محلي متاح |

## موانع البناء الستة المؤكدة

1. `android/gradlew` غير موجود.
2. `android/gradle/wrapper/gradle-wrapper.jar` غير موجود.
3. `android/gradlew.bat` غير موجود.
4. `android/key.properties` غير موجود، ولا يوجد keystore أصلي متاح. لا تنشئ مفتاحاً بديلاً؛ يلزم مفتاح الرفع الأصلي.
5. Flutter SDK غير متوفر في PATH.
6. البيئة الحالية تحتوي OpenJDK 21، بينما سكربت البناء يطلب JDK 17 لهذا الإعداد.

## إعدادات يجب التحقق منها قبل البناء

- `applicationId` و`namespace` محفوظان كـ `com.taxiouargla.lite`.
- رقم البناء في `pubspec.yaml` هو `31001` حالياً؛ لا تستخدمه قبل التأكد من أعلى `versionCode` في Play Console. يجب أن يكون الجديد أعلى منه.
- لا تتوفر قيم `SUPABASE_URL` و`SUPABASE_ANON_KEY`؛ مرّر القيم العامة الصحيحة محلياً عند البناء. يمنع تضمين `service_role` أو أي سر إداري داخل التطبيق.
- لا توجد نتيجة تشغيلية لـ Supabase staging أو اختبارات OTP/رحلة حقيقية في هذه البيئة.

## ما تم الحفاظ عليه

- اسم التطبيق «طاكسي ورڨلة لايت» ومعرّف الحزمة الثابت.
- حالات الرحلة الست المعتمدة.
- عدم وجود كتابة مباشرة إلى جدول `rides` من تطبيق الهاتف.
- عدم وجود قراءة مباشرة لعمود `profiles.phone` من تطبيق الهاتف.
- قواعد الرحلة النشطة وترتيب الأقفال التي فحصتها الأدوات الساكنة.

## الحكم النهائي

**NO-GO — لا يوجد AAB نهائي في هذه الحزمة، ولا يجوز رفعها إلى Google Play على أنها إصدار جاهز.**

هذه الحزمة تحتوي المصدر وأدوات التدقيق وتقرير النتائج. لإنتاج AAB حقيقي يلزم استعادة Gradle Wrapper الأصلي، وتوفير Flutter SDK وJDK 17، واستخدام مفتاح الرفع الأصلي محلياً، وتحديد إعدادات Supabase العامة ورقم بناء أعلى من آخر إصدار منشور، ثم تشغيل `tools/build_release_aab.sh` واجتياز التحليل والاختبارات والبناء وفحص التوقيع.

لم يتم تضمين أي مفاتيح أو كلمات مرور أو بيانات اعتماد سرية في هذه الحزمة.
