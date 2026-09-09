import re

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    arabic_reshaper = None
    get_display = None

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def display(text: str) -> str:
    """تهيئة النص العربي للعرض الصحيح في الطرفية.

    لا نغيّر الأوامر أو المسارات؛ الدالة مخصصة للنصوص المعروضة للمستخدم.
    """
    if not text or not ARABIC_RE.search(text):
        return text
    if arabic_reshaper is None or get_display is None:
        return text
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text
