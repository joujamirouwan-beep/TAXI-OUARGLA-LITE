# إعداد Google Maps في Android (V3.9)

يستخدم `AndroidManifest.xml` في الحزمة المتغير `${GOOGLE_MAPS_API_KEY}`. يجب تعريفه في ملف Gradle الأصلي، مع عدم استبدال إعدادات التوقيع أو بقية إعدادات التطبيق.

## Groovy — `android/app/build.gradle`

داخل كتلة `android { defaultConfig { ... } }` أضف السطر التالي مع الاحتفاظ ببقية الخصائص:

```gradle
manifestPlaceholders = [
    GOOGLE_MAPS_API_KEY: providers.gradleProperty("GOOGLE_MAPS_API_KEY").getOrElse("")
]
```

## Kotlin DSL — `android/app/build.gradle.kts`

داخل كتلة `android { defaultConfig { ... } }` أضف:

```kotlin
manifestPlaceholders["GOOGLE_MAPS_API_KEY"] =
    providers.gradleProperty("GOOGLE_MAPS_API_KEY").orElse("").get()
```

## تمرير المفتاح

Linux / macOS / Git Bash:

```bash
export GOOGLE_MAPS_API_KEY="YOUR_ANDROID_MAPS_KEY"
export ORG_GRADLE_PROJECT_GOOGLE_MAPS_API_KEY="$GOOGLE_MAPS_API_KEY"
```

PowerShell:

```powershell
$env:GOOGLE_MAPS_API_KEY = "YOUR_ANDROID_MAPS_KEY"
$env:ORG_GRADLE_PROJECT_GOOGLE_MAPS_API_KEY = $env:GOOGLE_MAPS_API_KEY
```

قيّد مفتاح Android في Google Cloud Console باسم الحزمة `com.taxiouargla.lite` وبصمة SHA-1 المناسبة (debug/release حسب الاستخدام)، وفعّل Maps SDK for Android. لا تضع المفتاح في Git أو في محادثة عامة.
