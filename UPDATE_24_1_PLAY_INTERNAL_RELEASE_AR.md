# UPDATE 24.1 — الرفع الآمن إلى Google Play Internal Testing

## ما أضيف
- `tools/upload_to_play_internal.py`: رفع AAB موقّع عبر Google Play Android Publisher API الرسمي.
- `tools/verify_upload.py`: التحقق من ظهور versionCode على مسار internal وحالة الإصدار.
- `upload_to_play_internal.bat`: مشغل Windows.
- `tools/requirements-play-upload.txt`: اعتماديات Python.
- `play-api-key.template.json`: قالب توضيحي فقط؛ ليس بيانات اعتماد صالحة.
- `DEVELOPER_CHECKLIST_UPDATE_24_1_AR.md`: قائمة تنفيذ وتسليم.

## ثوابت لا تتغير
- Package / applicationId: `com.taxiouargla.lite`.
- لا تنشئ تطبيقاً جديداً في Play Console.
- لا تستبدل مفتاح الرفع/التوقيع الأصلي.
- لا تضع Service Account JSON أو keystore أو كلمات المرور في ZIP أو Git أو WhatsApp.

## إعداد حساب الخدمة
1. من Google Play Console افتح Setup > API access.
2. اربط مشروع Google Cloud الصحيح، وأنشئ Service Account وفق إرشادات Google.
3. امنح حساب الخدمة أقل صلاحية لازمة لإدارة الاختبار الداخلي للتطبيق.
4. نزّل JSON واحفظه محلياً بجانب المشروع باسم `play-api-key.json`.
5. لا ترفع هذا الملف إلى المحادثة أو المستودع أو ترسله عبر WhatsApp.

## تحقق شهادة الرفع
يجب أن تكون بصمة SHA-256 لشهادة رفع AAB مطابقة للشهادة المعتمدة في Play Console. عيّن متغير البيئة `EXPECTED_UPLOAD_CERT_SHA256` إلى 64 خانة hex (يمكن إزالة النقطتين من بصمة Play Console).

PowerShell:
```powershell
$env:EXPECTED_UPLOAD_CERT_SHA256 = 'ضع_بصمة_SHA256_المعتمدة_هنا'
```

## تثبيت وتشغيل
```powershell
python -m pip install -r tools/requirements-play-upload.txt
python tools/upload_to_play_internal.py --aab build/app/outputs/bundle/release/app-release.aab --package com.taxiouargla.lite --track internal --service-account play-api-key.json
```
أو شغّل `upload_to_play_internal.bat` بعد تعيين متغير البصمة.

السكربت يقوم بـ:
- فحص ZIP integrity للـ AAB.
- التحقق من توقيع JAR/AAB بواسطة `jarsigner`.
- استخراج شهادة التوقيع بواسطة `keytool` ومقارنتها بالبصمة المتوقعة.
- إنشاء edit، وفحص أعلى versionCode على المسارات التي تعرضها API.
- رفع AAB، ثم يضيف الإصدار إلى مسار internal بحالة `draft` ويحفظ التعديل.

## لماذا Draft؟
الرفع الآلي لا ينبغي أن ينشر إصداراً للمختبرين أو المستخدمين دون مراجعة بشرية. بعد الرفع، افتح Play Console وراجع الإصدار والملاحظات وسياسة الاختبار، ثم انشره للاختبار الداخلي يدوياً. حالة `draft` ليست رابط تثبيت ولا تعني أن الاختبار أصبح متاحاً.

## فحص ما بعد الرفع
استبدل `VERSION_CODE` بالقيمة التي طبعها سكربت الرفع:
```powershell
python tools/verify_upload.py --version-code VERSION_CODE --expected-status draft --service-account play-api-key.json
```
بعد نشر الإصدار من Play Console، أعد التحقق بالحالة المناسبة، مثلاً:
```powershell
python tools/verify_upload.py --version-code VERSION_CODE --expected-status completed --service-account play-api-key.json
```
قد تختلف حالة المسار حسب ما يظهر في Play Console؛ لا تعتبر `draft` منشوراً.

## حدود التحقق
- نجاح API يثبت أن Google Play قبل الإصدار وحفظه على المسار المحدد، ولا يثبت عمل التطبيق على جهاز فعلي.
- API لا يثبت أن المستخدمين يستطيعون التثبيت إذا بقي الإصدار Draft أو لم تكتمل متطلبات الاختبار.
- التحقق من تطابق بصمة شهادة الرفع محلياً لا يثبت وحده تطابق App Signing certificate التي تديرها Google Play؛ هاتان شهادتان قد تختلفان عند تفعيل Play App Signing.
- لا يقوم السكربت بترقية الإصدار إلى production ولا يرسل دعوات مختبرين.
