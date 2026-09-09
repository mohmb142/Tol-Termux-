import re

# Commands that are never auto-executed by the agent.
BLOCKED_PATTERNS = [
    r"(^|\s)rm\s+-rf\s+/(?:\s|$)",
    r"(^|\s)rm\s+-rf\s+~(?:/|\s|$)",
    r"(^|\s)mkfs(?:\.|\s)",
    r"(^|\s)dd\s+if=",
    r"(^|\s)chmod\s+777\s+/",
    r"(^|\s)chown\s+.*\s+/\s*$",
    r"(^|\s)su\s*$",
]

SENSITIVE_PATTERNS = [
    r"(^|\s)sudo\b",
    r"(^|\s)su\b",
    r"(^|\s)rm\b",
    r"(^|\s)mv\b",
    r"(^|\s)chmod\b",
    r"(^|\s)chown\b",
    r"(^|\s)pkg\s+(install|remove|upgrade)\b",
    r"(^|\s)pip\s+(install|uninstall)\b",
    r"(^|\s)git\s+(clone|pull|reset|clean)\b",
    r"(^|\s)termux-.*\b",
]


def classify(command: str, model_risk: str = "high") -> str:
    command = command.strip()
    if not command:
        return "high"
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "blocked"
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "medium"
    return "low" if model_risk == "low" else "medium"


def is_blocked(command: str) -> bool:
    return classify(command) == "blocked"
