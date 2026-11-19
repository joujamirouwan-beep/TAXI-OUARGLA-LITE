# المصادقة والتوجيه حسب الملف الشخصي

## الملفات
- `lib/app/app_dependencies.dart`: حاوية اعتماديات واحدة بعد تهيئة Supabase.
- `lib/routing/auth_wrapper.dart`: يتابع `onAuthStateChange` ويعالج الدخول والخروج وأخطاء stream.
- `lib/routing/profile_router.dart`: يراقب صف المستخدم الحالي ويوجه حسب الدور والتحقق.
- `lib/routing/profile_destination.dart`: دالة قرار مستقلة قابلة للاختبار.

## مثال تركيب داخل التطبيق

```dart
final deps = AppDependencies.initialize(Supabase.instance.client);

AuthWrapper(
  client: Supabase.instance.client,
  signedOutBuilder: (_) => const LoginScreen(),
  loadingBuilder: (_) => const SplashScreen(),
  errorBuilder: (_, error) => ErrorScreen(error: error),
  authenticatedBuilder: (context, user) => buildProfileRouter(
    context: context,
    client: Supabase.instance.client,
    user: user,
    pages: ProfileRouterBuilder(
      riderHome: (_) => const RiderHomeScreen(),
      driverHome: (_) => const DriverHomeScreen(),
      driverPending: (_) => const DriverPendingScreen(),
      adminHome: (_) => const AdminHomeScreen(),
      loading: (_) => const SplashScreen(),
      missingProfile: (_) => const ProfileSetupScreen(),
      error: (_, error) => ErrorScreen(error: error),
    ),
  ),
)
```

استبدل أسماء الشاشات بأسماء المشروع الفعلية. لا تنشئ شاشات وهمية ولا تستبدل واجهات قديمة قبل مطابقة أسمائها وعقودها.

## شروط قاعدة البيانات
`ProfileService` الحالي يقرأ الأعمدة `id`, `role`, `is_verified`, `is_online`. تحقق من وجودها وأن سياسات RLS تسمح للمستخدم بقراءة صفه. `admin` في Flutter ليس صلاحية أمنية؛ يجب أن تمنع RLS وRPC غير المصرح بهما أي وصول إداري.

## ملاحظات الجلسة
- `AuthWrapper` يبدأ من `currentUser` ثم يتابع تغيرات المصادقة.
- `ProfileRouter` يثبت stream خارج `build` ويعيد ربطه عند تبدل المستخدم أو Supabase client.
- `ValueKey(user.id)` في helper يعزل حالة التوجيه بين حسابين.
- فشل قراءة الملف الشخصي يظهر كخطأ ولا يتحول بصمت إلى ملف غير موجود.
