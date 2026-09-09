# Tol-Termux AI Agent 🤖

وكيل ذكاء اصطناعي يعمل داخل Termux باستخدام OpenRouter.

## التثبيت

```bash
git clone https://github.com/mohmb142/Tol-Termux-.git
cd Tol-Termux-
bash install.sh
```

أثناء التثبيت سيطلب منك:
- OpenRouter API Key
- اسم نموذج OpenRouter، والقيمة الافتراضية `google/gemini-2.5-flash`

ثم شغّل:

```bash
termux-ai
```

## ماذا يفعل؟

- يفهم الطلب باللغة العربية أو الإنجليزية.
- يولد أوامر مناسبة لـ Termux.
- ينفذ الأوامر ويراقب النتيجة.
- يعرض الأخطاء.
- يطلب من النموذج اقتراح إصلاح عند فشل الأمر.
- يطلب موافقة قبل تنفيذ الأوامر غير منخفضة الخطورة.
- يحفظ مفتاح OpenRouter محليًا في `~/.termux-ai/.env` بصلاحية 600.

> لا تضع مفتاح OpenRouter داخل ملفات المشروع أو GitHub.
