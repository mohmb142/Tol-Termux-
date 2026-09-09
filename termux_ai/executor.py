import subprocess


def run_command(command: str, timeout: int = 300):
    try:
        p = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            executable="/data/data/com.termux/files/usr/bin/bash",
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", "Command timed out."
