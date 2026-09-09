import re
import shutil
import subprocess

# أوامر Termux:API التي تستخدم الحزمة المشتركة termux-api.
TERMUX_API_COMMANDS = {
    "termux-battery-status": "حالة البطارية",
    "termux-camera-info": "معلومات الكاميرا",
    "termux-camera-photo": "التقاط صورة بالكاميرا",
    "termux-toast": "إظهار رسالة على الشاشة",
    "termux-vibrate": "اهتزاز الهاتف",
    "termux-notification": "إرسال إشعار",
    "termux-notification-remove": "حذف إشعار",
    "termux-location": "الحصول على الموقع",
    "termux-clipboard-get": "قراءة الحافظة",
    "termux-clipboard-set": "تعديل الحافظة",
    "termux-brightness": "تغيير سطوع الشاشة",
    "termux-volume": "قراءة أو تغيير مستوى الصوت",
    "termux-torch": "تشغيل أو إطفاء المصباح",
    "termux-wifi-connectioninfo": "معلومات اتصال Wi-Fi",
    "termux-wifi-scaninfo": "فحص شبكات Wi-Fi",
    "termux-media-player": "التحكم بمشغل الوسائط",
    "termux-telephony-deviceinfo": "معلومات الهاتف والشبكة",
}


def is_termux_api_command(command: str) -> bool:
    return bool(re.search(r"(?:^|[;&|]\s*)termux-[a-z0-9-]+", command))


def find_missing_termux_commands(command: str):
    missing = []
    for name in re.findall(r"(?<![\w/-])(termux-[a-z0-9-]+)", command):
        if name in TERMUX_API_COMMANDS and shutil.which(name) is None:
            missing.append(name)
    return missing


def api_package_installed() -> bool:
    try:
        result = subprocess.run(
            ["dpkg", "-s", "termux-api"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def local_plan(request: str):
    """يعالج الطلبات الواضحة محليًا قبل إرسالها إلى النموذج."""
    text = request.strip().lower()
    if any(x in text for x in ["افتح الكاميرا", "فتح الكاميرا", "شغل الكاميرا", "التقاط صورة", "التقط صورة"]):
        return {
            "explanation": "سأستخدم Termux:API لالتقاط صورة من الكاميرا.",
            "command": "termux-camera-photo -c 0 ~/tol-termux-photo.jpg",
            "risk": "medium",
        }
    if any(x in text for x in ["حالة البطارية", "نسبة البطارية", "البطارية"]):
        return {
            "explanation": "سأقرأ حالة البطارية عبر Termux:API.",
            "command": "termux-battery-status",
            "risk": "low",
        }
    if any(x in text for x in ["اختبار الإشعار", "اختبر الإشعار", "اعرض إشعار", "أرسل إشعار"]):
        return {
            "explanation": "سأرسل إشعارًا محليًا باستخدام Termux:API.",
            "command": "termux-notification --title 'Tol-Termux' --content 'اختبار الإشعار'",
            "risk": "low",
        }
    return None


def missing_command_message(command: str):
    missing = find_missing_termux_commands(command)
    if not missing:
        return None
    names = ", ".join(missing)
    return (
        f"الأمر {names} تابع لـ Termux:API لكنه غير موجود حاليًا. "
        "ثبّت حزمة Termux API بالأمر: pkg install termux-api -y، "
        "وتأكد أيضًا من تثبيت تطبيق Termux:API ومنحه الأذونات المطلوبة."
    )
