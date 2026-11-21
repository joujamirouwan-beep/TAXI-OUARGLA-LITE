# UPDATE 14 — Android Gradle configuration correction

## What changed
- Replaced the incomplete `android/settings.gradle` with Flutter's plugin-loader configuration.
- Removed the incorrect Flutter Gradle plugin version declaration from the root `android/build.gradle`; Flutter's Gradle plugin is loaded from the locally installed Flutter SDK through `includeBuild`.
- Added `android/local.properties.example`.
- Strengthened `.gitignore` for local SDK paths and signing material.

## Preserved
- `applicationId` and namespace: `com.taxiouargla.lite`
- `versionName`: `3.10.1`
- `versionCode`: `31001` (must be checked against the current Play Console version before release)
- Gradle distribution: 8.4; Android Gradle Plugin: 8.3.2; Kotlin: 1.9.22
- Existing business rules and Supabase migrations.

## Important limitations
This is a source/configuration patch, not a built release. The archive still lacks:
- `android/gradlew`, `android/gradlew.bat`, and `android/gradle/wrapper/gradle-wrapper.jar`
- Flutter SDK and Dart SDK in this environment
- the original upload/release keystore and its local `android/key.properties`
- a verified original Android project from the programmer

The programmer must merge these Android configuration files into the authentic Flutter project, retain its original wrapper and signing key, set `flutter.sdk` in `android/local.properties`, then run `flutter pub get`, `flutter analyze`, `flutter test`, and the release AAB script. Do not replace the Play signing key.

## Notification scope
Migration `20261118_007_in_app_notifications.sql` creates durable in-app notifications. It does not implement push notifications delivered while the app is closed (FCM), and it has not been applied to a live Supabase project. Apply only after checking the live schema and backup.

## Release decision
SOURCE PATCH PREPARED / STATIC PREFLIGHT ONLY / AAB NOT BUILT OR VERIFIED.
