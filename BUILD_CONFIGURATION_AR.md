# إعدادات البناء

يتم تمرير إعدادات Supabase وقت البناء عبر --dart-define:

```bash
flutter run --dart-define=SUPABASE_URL=https://YOUR_PROJECT.supabase.co --dart-define=SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

استخدم anon/publishable key فقط في تطبيق العميل مع RLS مضبوط. يمنع وضع service_role أو مفاتيح خاصة داخل التطبيق.
