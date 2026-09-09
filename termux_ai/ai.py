import requests
from .config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_URL

SYSTEM_PROMPT = """أنت وكيل Termux ذكي. حوّل طلب المستخدم إلى أوامر Bash مناسبة لـ Termux.\nأعد JSON فقط بالشكل:\n{\"explanation\":\"...\",\"command\":\"...\",\"risk\":\"low|medium|high\"}\nلا تستخدم أوامر تدميرية أو خطرة دون طلب موافقة المستخدم. إذا كان الطلب غير واضح، اجعل command فارغًا."""


def ask_ai(user_text: str, error_context: str = "") -> dict:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY غير مضبوط")
    prompt = user_text
    if error_context:
        prompt += "\n\nنتيجة تنفيذ سابقة/خطأ:\n" + error_context
    r = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/mohmb142/Tol-Termux-",
            "X-Title": "Tol-Termux AI Agent",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        },
        timeout=60,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    import json
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start:end + 1])
        raise RuntimeError("لم يرجع النموذج JSON صالحًا")
