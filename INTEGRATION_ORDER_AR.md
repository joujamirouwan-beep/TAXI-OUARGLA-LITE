# ترتيب الدمج المقترح

1. راجع `RPC_CONTRACT_V2_AR.md` مع ملف SQL V2 المرجعي، ثم قارن الدوال مع قاعدة Supabase الحقيقية.
2. أضف الاعتماديات من `pubspec.dependencies.yaml` دون استبدال `pubspec.yaml` بالكامل.
3. أضف `models/ride_status.dart` و`models/ride_model.dart` وشغّل اختبارات النماذج.
4. أضف `services/ride_rpc_client.dart` و`services/ride_service.dart`.
5. أضف `models/user_profile.dart` و`services/profile_service.dart`.
6. أضف `repositories/ride_data_source.dart` و`repositories/ride_repository.dart`.
7. بعد ذلك فقط، اربط الواجهات القديمة بالمستودع الجديد، شاشةً شاشة، ولا تنسخ شاشات V3.9 مباشرة.
8. طبقة الخرائط خطوة لاحقة منفصلة: `flutter_map` + `latlong2` + OSM، مع مراجعة سياسة استخدام خوادم البلاطات قبل النشر.

لا تنفذ SQL من هذه الحزمة؛ فهي حزمة Dart ومواصفة عقد فقط.
