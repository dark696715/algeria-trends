# دليل الإعداد خطوة بخطوة 🛠️

هذا الدليل يشرح كيف تجعل الـ workflow يعمل من الصفر: تثبيت المتطلبات، الحصول على المفاتيح والتوكنات لكل منصة، ثم التشغيل والجدولة التلقائية.

> **نصيحة:** ابدأ بتيليغرام فقط (الأسهل)، تأكّد أن كل شيء يعمل، ثم أضِف بقية المنصات واحدة تلو الأخرى.

---

## 0) المتطلبات الأساسية

- تثبيت **Python 3.9** أو أحدث.
- في مجلد المشروع، نفّذ:

```bash
pip install -r requirements.txt
cp config.example.json config.json
```

ثم افتح `config.json` بمحرّر نصوص لتعبئته في الخطوات التالية.

---

## 1) جمع الترندات

### أ) YouTube (أكثر الفيديوهات رواجاً في الجزائر)

1. ادخل إلى **Google Cloud Console**: https://console.cloud.google.com/
2. أنشئ مشروعاً جديداً (New Project).
3. من القائمة: **APIs & Services → Library** وابحث عن **YouTube Data API v3** ثم فعّلها (Enable).
4. اذهب إلى **APIs & Services → Credentials → Create Credentials → API key**.
5. انسخ المفتاح وضعه في `config.json`:

```json
"youtube": { "enabled": true, "api_key": "المفتاح_هنا", "max_results": 15 }
```

> مجاني ضمن حصّة يومية سخيّة (10,000 وحدة/يوم). كل تشغيلة تستهلك القليل جداً.

### ب) Google Trends (بديل مجاني عن ترندات تيك توك)

لا يحتاج أي مفتاح — يعمل مباشرة. فقط اترك:

```json
"google_trends": { "enabled": true, "geo": "DZ", "max_results": 15 }
```

> **بخصوص تيك توك:** لا توفّر منصة تيك توك واجهة API رسمية مجانية لجلب "الترندات". لذلك نعتمد Google Trends كمصدر موثوق يعكس اهتمامات الجزائريين. (يمكن لاحقاً إضافة مصدر تيك توك عبر خدمة خارجية مدفوعة إن رغبت.)

---

## 2) النشر — إعداد كل منصة

### أ) تيليغرام ✅ (الأسهل — ابدأ هنا)

1. في تطبيق تيليغرام ابحث عن **@BotFather**.
2. أرسل `/newbot` واتبع التعليمات لتحصل على **bot token** (شكله: `123456:ABC-DEF...`).
3. أنشئ قناة (Channel) وأضِف البوت فيها **كمشرف (Admin)** بصلاحية النشر.
4. لمعرفة `chat_id`:
   - إن كانت قناتك عامة: استخدم اسمها مثل `@my_channel`.
   - إن كانت خاصة: أرسل رسالة في القناة، ثم افتح في المتصفح:
     `https://api.telegram.org/bot<التوكن>/getUpdates` وابحث عن `"chat":{"id":-100...}`.
5. في `config.json`:

```json
"telegram": {
  "enabled": true,
  "bot_token": "123456:ABC-DEF...",
  "chat_id": "@my_channel"
}
```

### ب) فيسبوك (صفحة Page فقط)

> ⚠️ لا يمكن النشر تلقائياً على حساب شخصي — فقط على **صفحة**.

1. أنشئ **صفحة فيسبوك** إن لم تكن لديك.
2. ادخل إلى **Meta for Developers**: https://developers.facebook.com/ وأنشئ تطبيقاً (App) من نوع **Business**.
3. أضِف منتج **Facebook Login** ومنح الصلاحيات: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`.
4. من **Graph API Explorer** احصل على **User Access Token** بهذه الصلاحيات، ثم استبدله بـ **Page Access Token** طويل الأمد:
   - نفّذ `GET /me/accounts` للحصول على `page_id` وتوكن الصفحة.
   - حوّل التوكن إلى طويل الأمد عبر أداة: **Access Token Debugger → Extend**.
5. في `config.json`:

```json
"facebook": {
  "enabled": true,
  "page_id": "معرّف_الصفحة",
  "page_access_token": "توكن_الصفحة_طويل_الأمد"
}
```

### ج) إنستغرام (حساب أعمال/منشئ)

> ⚠️ إنستغرام يتطلب أن تكون الصورة/الفيديو متاحة على **رابط عام** (لأن إنستغرام يجلبها من الرابط)، ولا يمكن نشر منشور بدون وسيط.

1. حوّل حساب إنستغرام إلى **Business** أو **Creator**، واربطه بصفحة فيسبوك.
2. استخدم نفس تطبيق Meta السابق وأضِف صلاحيات: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`.
3. احصل على **ig_user_id** عبر: `GET /{page_id}?fields=instagram_business_account`.
4. استخدم **توكن وصول طويل الأمد** (نفس آلية فيسبوك).
5. في `config.json`:

```json
"instagram": {
  "enabled": true,
  "ig_user_id": "معرّف_حساب_الأعمال",
  "access_token": "التوكن_طويل_الأمد"
}
```

> بما أن ثمبنيل يوتيوب متاح على رابط عام، فهو يصلح كصورة لمنشور إنستغرام تلقائياً.

### د) تيك توك (الأصعب)

> ⚠️ يتطلب **فيديو حقيقياً** + تطبيق مطوّر **معتمَد** من TikTok، وقد تحتاج مراجعة/موافقة قد تستغرق وقتاً.

1. سجّل في **TikTok for Developers**: https://developers.tiktok.com/
2. أنشئ تطبيقاً واطلب صلاحية **Content Posting API** (`video.publish`).
3. وثّق نطاقك (Domain verification) إن كنت ستستخدم `PULL_FROM_URL`.
4. احصل على **access_token** عبر OAuth.
5. في `config.json`:

```json
"tiktok": { "enabled": true, "access_token": "توكن_تيك_توك" }
```

> ملاحظة: منشورات الترندات لدينا نصّية/صور مصغّرة، لذا لن ينشر تيك توك إلا إذا وفّرت رابط فيديو (.mp4). ابدأ بجعل `privacy_level` على `SELF_ONLY` للاختبار (موجود في `publishers/tiktok.py`).

---

## 3) التشغيل

```bash
# تجربة آمنة أولاً (يطبع ما سيُنشر دون نشر فعلي)
python main.py --dry-run

# نشر فعلي: اجعل "dry_run": false في config.json ثم
python main.py
```

- ملف `state/seen.json` يمنع تكرار نفس الترند (لمدة 7 أيام افتراضياً).
- ملف `logs/workflow.log` يسجّل كل عملية.

---

## 4) الجدولة التلقائية (عدة مرات يومياً) ⏰

بما أنك تريد النشر **عدة مرات يومياً تلقائياً**، تحتاج مكاناً يعمل بشكل دائم. إليك ثلاثة خيارات مرتّبة من الأسهل:

### الخيار (أ): GitHub Actions — مجاني ويعمل 24/7 (موصى به)

المشروع يتضمّن ملفاً جاهزاً في `.github/workflows/publish.yml`:

1. ارفع المشروع إلى مستودع **خاص (Private)** على GitHub.
2. من **Settings → Secrets and variables → Actions**، أضِف مفاتيحك كـ Secrets:
   `YOUTUBE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `FB_PAGE_ID`, `FB_PAGE_TOKEN`, `IG_USER_ID`, `IG_TOKEN`, `TIKTOK_TOKEN`.
3. سيعمل تلقائياً كل 6 ساعات (يمكنك تعديل الجدول في الملف).

### الخيار (ب): جهازك الشخصي عبر cron (لينكس/ماك)

```bash
crontab -e
# نشر 3 مرات يومياً (9ص، 3م، 9م):
0 9,15,21 * * *  cd /مسار/المشروع && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

### الخيار (ج): Windows — Task Scheduler

افتح **Task Scheduler → Create Basic Task**، اختر التكرار اليومي، وفي الإجراء اختر:
`python.exe` مع الوسيط `main.py` ومجلد العمل هو مجلد المشروع.

> **ملاحظة عن تطبيق Claude:** المهام المجدولة داخل تطبيق Claude تعمل فقط أثناء فتح التطبيق، وبيئته معزولة عن مفاتيحك المحفوظة محلياً. لذلك للتشغيل الدائم الحقيقي استخدم أحد الخيارات الثلاثة أعلاه.

---

## استكشاف الأخطاء

| المشكلة | الحل |
|---|---|
| `تم تخطّي يوتيوب` | مفتاح YouTube غير موضوع أو غير صالح. |
| `تعذّرت قراءة RSS` | مشكلة شبكة مؤقتة، أو أن جهازك خلف Proxy/VPN يحجب Google. جرّب `pip install pytrends`. |
| منشور تيليغرام لا يظهر | تأكّد أن البوت **مشرف** في القناة وأن `chat_id` صحيح. |
| فيسبوك يرفض النشر | تأكّد أنه توكن **صفحة** طويل الأمد وبالصلاحيات المطلوبة. |
| إنستغرام يفشل | تأكّد أن الحساب **Business** والصورة على رابط عام. |

انتهى ✅ — أي منصة تريد ضبطها أولاً، أنا جاهز لمساعدتك في تفاصيلها.
