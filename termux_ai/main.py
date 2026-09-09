#!/usr/bin/env python3
import json
from rich.console import Console
from rich.prompt import Prompt
from .ai import ask_ai
from .executor import run_command
from .permissions import classify
from .history import record
from .termux_tools import local_plan, missing_command_message
from .arabic import display

console = Console()


def out(text="", **kwargs):
    console.print(display(str(text)), **kwargs)


def approve(message):
    return Prompt.ask(display(message), choices=["y", "n"], default="n") == "y"


def execute_checked(request, command, model_risk):
    risk = classify(command, model_risk)
    out(f"مستوى الأمان: {risk}", style="dim")
    if risk == "blocked":
        out("⛔ تم حظر هذا الأمر تلقائيًا لأنه قد يسبب ضررًا واسعًا للنظام أو البيانات.", style="red")
        record("blocked", {"request": request, "command": command, "risk": risk})
        return None
    if risk == "medium" and not approve("⚠️ الأمر يحتاج موافقة. تنفيذه؟"):
        out("تم الإلغاء.")
        record("denied", {"request": request, "command": command, "risk": risk})
        return None
    code, stdout, stderr = run_command(command)
    record("execute", {"request": request, "command": command, "risk": risk, "exit_code": code, "stdout": stdout, "stderr": stderr})
    if stdout:
        out(stdout)
    return code, stdout, stderr


def main():
    out("🤖 Tol-Termux AI Agent", style="bold")
    out("اكتب ما تريد تنفيذه. اكتب exit للخروج.\n")
    while True:
        try:
            request = Prompt.ask(display("[cyan]أنت[/cyan]"))
        except (EOFError, KeyboardInterrupt):
            break
        if request.strip().lower() in {"exit", "quit", "خروج"}:
            break
        if not request.strip():
            continue
        try:
            plan = local_plan(request) or ask_ai(request)
            command = plan.get("command", "").strip()
            out(f"🧠 {plan.get('explanation', '')}", style="yellow")
            if not command:
                out("لم يتم إنشاء أمر للتنفيذ.", style="yellow")
                continue
            out(f"الأمر: {command}", style="bold")

            missing_message = missing_command_message(command)
            if missing_message:
                out(f"📱 {missing_message}", style="yellow")
                if approve("تثبيت حزمة Termux:API الآن؟"):
                    install_result = execute_checked(
                        "تثبيت Termux:API لإصلاح الأمر: " + request,
                        "pkg install termux-api -y",
                        "medium",
                    )
                    if install_result and install_result[0] == 0:
                        out("🔄 تمت محاولة التثبيت. أعد المحاولة بعد التأكد من تطبيق Termux:API والأذونات.", style="cyan")
                continue

            result = execute_checked(request, command, plan.get("risk", "high"))
            if result is None:
                continue
            code, stdout, stderr = result
            if code == 0:
                out("✓ تم التنفيذ بنجاح", style="green")
                continue
            out(f"✗ فشل الأمر (code={code})", style="red")
            if stderr:
                out(stderr, style="red")

            local_error = missing_command_message(command)
            if local_error:
                out(f"📱 {local_error}", style="yellow")
                continue

            fix_context = json.dumps({"command": command, "exit_code": code, "stderr": stderr, "stdout": stdout}, ensure_ascii=False)
            out("🔍 تحليل الخطأ واقتراح إصلاح...", style="cyan")
            fix = ask_ai("حل المشكلة. أعطني أمر إصلاح واحدًا فقط ضمن JSON، وتجنب الأوامر الخطرة. اشرح بالعربية.", fix_context)
            fix_command = fix.get("command", "").strip()
            if not fix_command:
                out("لم يتم العثور على إصلاح آمن تلقائيًا.", style="yellow")
                continue
            out(f"🔧 اقتراح الإصلاح: {fix_command}", style="magenta")
            repair_result = execute_checked("إصلاح: " + request, fix_command, fix.get("risk", "high"))
            if repair_result is None:
                continue
            c2, o2, e2 = repair_result
            if c2 == 0:
                out("✓ تم تنفيذ الإصلاح بنجاح.", style="green")
                out("🔄 إعادة المحاولة للتحقق...", style="cyan")
                verify = execute_checked("التحقق بعد الإصلاح: " + request, command, plan.get("risk", "high"))
                if verify and verify[0] == 0:
                    out("✓ نجح الأمر الأصلي بعد الإصلاح.", style="green")
                elif verify:
                    out("⚠️ ما زال الأمر الأصلي يفشل؛ لم أكرر الإصلاح تلقائيًا.", style="yellow")
            elif e2:
                out(f"فشل الإصلاح: {e2}", style="red")
        except Exception as exc:
            out(f"خطأ: {exc}", style="red")


if __name__ == "__main__":
    main()
