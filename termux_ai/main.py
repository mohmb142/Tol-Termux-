#!/usr/bin/env python3
import json
from rich.console import Console
from rich.prompt import Prompt
from .ai import ask_ai
from .executor import run_command

console = Console()


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
            plan = ask_ai(request)
            command = plan.get("command", "").strip()
            console.print(f"[yellow]🧠 {plan.get('explanation', '')}[/yellow]")
            if not command:
                console.print("[yellow]لم يتم إنشاء أمر للتنفيذ.[/yellow]")
                continue
            console.print(f"\n[bold]الأمر:[/bold] {command}")
            risk = plan.get("risk", "high")
            if risk != "low":
                answer = Prompt.ask("تنفيذ هذا الأمر؟", choices=["y", "n"], default="n")
                if answer != "y":
                    console.print("تم الإلغاء.")
                    continue
            code, stdout, stderr = run_command(command)
            if stdout:
                console.print(stdout)
            if code == 0:
                console.print("[green]✓ تم التنفيذ بنجاح[/green]")
                continue
            console.print(f"[red]✗ فشل الأمر (code={code})[/red]")
            if stderr:
                console.print(stderr)
            fix_context = json.dumps({"command": command, "exit_code": code, "stderr": stderr, "stdout": stdout}, ensure_ascii=False)
            fix = ask_ai("حل المشكلة وأعطني أمر الإصلاح فقط ضمن JSON.", fix_context)
            fix_command = fix.get("command", "").strip()
            if fix_command:
                console.print(f"[magenta]🔧 اقتراح الإصلاح:[/magenta] {fix_command}")
                answer = Prompt.ask("تطبيق الإصلاح؟", choices=["y", "n"], default="n")
                if answer == "y":
                    c2, o2, e2 = run_command(fix_command)
                    if o2: console.print(o2)
                    if c2 == 0: console.print("[green]✓ تم الإصلاح بنجاح[/green]")
                    elif e2: console.print(f"[red]{e2}[/red]")
        except Exception as exc:
            console.print(f"[red]خطأ: {exc}[/red]")


if __name__ == "__main__":
    main()
