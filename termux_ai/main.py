#!/usr/bin/env python3
import json
from rich.console import Console
from rich.prompt import Prompt
from .ai import ask_ai
from .executor import run_command
from .permissions import classify
from .history import record
from .termux_tools import local_plan, missing_command_message

console = Console()


def approve(message):
    return Prompt.ask(message, choices=["y", "n"], default="n") == "y"


def execute_checked(request, command, model_risk):
    risk = classify(command, model_risk)
    console.print(f"[dim]مستوى الأمان: {risk}[/dim]")
    if risk == "blocked":
        console.print("[red]⛔ تم حظر هذا الأمر تلقائيًا لأنه قد يسبب ضررًا واسعًا للنظام أو البيانات.[/red]")
        record("blocked", {"request": request, "command": command, "risk": risk})
        return None
    if risk == "medium" and not approve("⚠️ الأمر يحتاج موافقة. تنفيذه؟"):
        console.print("تم الإلغاء.")
        record("denied", {"request": request, "command": command, "risk": risk})
        return None
    code, stdout, stderr = run_command(command)
    record("execute", {"request": request, "command": command, "risk": risk, "exit_code": code, "stdout": stdout, "stderr": stderr})
    if stdout:
        console.print(stdout)
    return code, stdout, stderr


def main():
    console.print("[bold]🤖 Tol-Termux AI Agent[/bold]")
    console.print("اكتب ما تريد تنفيذه. اكتب exit للخروج.\n")
    while True:
        try:
            request = Prompt.ask("[cyan]أنت[/cyan]")
        except (EOFError, KeyboardInterrupt):
            break
        if request.strip().lower() in {"exit", "quit", "خروج"}:
            break
        if not request.strip():
            continue
        try:
            # الطلبات الواضحة الخاصة بالهاتف تُنفّذ بقواعد محلية موثوقة قبل AI.
            plan = local_plan(request) or ask_ai(request)
            command = plan.get("command", "").strip()
            console.print(f"[yellow]🧠 {plan.get('explanation', '')}[/yellow]")
            if not command:
                console.print("[yellow]لم يتم إنشاء أمر للتنفيذ.[/yellow]")
                continue
            console.print(f"\n[bold]الأمر:[/bold] {command}")

            missing_message = missing_command_message(command)
            if missing_message:
                console.print(f"[yellow]📱 {missing_message}[/yellow]")
                if approve("تثبيت حزمة Termux:API الآن؟"):
                    install_result = execute_checked(
                        "تثبيت Termux:API لإصلاح الأمر: " + request,
                        "pkg install termux-api -y",
                        "medium",
                    )
                    if install_result and install_result[0] == 0:
                        console.print("[cyan]🔄 تمت محاولة التثبيت. أعد المحاولة الآن بعد التأكد من تطبيق Termux:API والأذونات.[/cyan]")
                continue

            result = execute_checked(request, command, plan.get("risk", "high"))
            if result is None:
                continue
            code, stdout, stderr = result
            if code == 0:
                console.print("[green]✓ تم التنفيذ بنجاح[/green]")
                continue
            console.print(f"[red]✗ فشل الأمر (code={code})[/red]")
            if stderr:
                console.print(stderr)

            # تشخيص محلي قبل استدعاء AI لمنع إصلاحات Termux API العشوائية.
            local_error = missing_command_message(command)
            if local_error:
                console.print(f"[yellow]📱 {local_error}[/yellow]")
                continue

            fix_context = json.dumps({"command": command, "exit_code": code, "stderr": stderr, "stdout": stdout}, ensure_ascii=False)
            console.print("[cyan]🔍 تحليل الخطأ واقتراح إصلاح...[/cyan]")
            fix = ask_ai("حل المشكلة. أعطني أمر إصلاح واحدًا فقط ضمن JSON، وتجنب الأوامر الخطرة.", fix_context)
            fix_command = fix.get("command", "").strip()
            if not fix_command:
                console.print("[yellow]لم يتم العثور على إصلاح آمن تلقائيًا.[/yellow]")
                continue
            console.print(f"[magenta]🔧 اقتراح الإصلاح:[/magenta] {fix_command}")
            repair_result = execute_checked("إصلاح: " + request, fix_command, fix.get("risk", "high"))
            if repair_result is None:
                continue
            c2, o2, e2 = repair_result
            if c2 == 0:
                console.print("[green]✓ تم تنفيذ الإصلاح بنجاح.[/green]")
                console.print("[cyan]🔄 إعادة المحاولة للتحقق...[/cyan]")
                verify = execute_checked("التحقق بعد الإصلاح: " + request, command, plan.get("risk", "high"))
                if verify and verify[0] == 0:
                    console.print("[green]✓ نجح الأمر الأصلي بعد الإصلاح.[/green]")
                elif verify:
                    console.print("[yellow]⚠️ ما زال الأمر الأصلي يفشل؛ لم أكرر الإصلاح تلقائيًا.[/yellow]")
            elif e2:
                console.print(f"[red]فشل الإصلاح: {e2}[/red]")
        except Exception as exc:
            console.print(f"[red]خطأ: {exc}[/red]")


if __name__ == "__main__":
    main()
