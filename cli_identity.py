"""Identify the installed Antigravity CLI; Argon is unavailable to IDE clients."""
from functools import cache
import platform
import re
import subprocess


@cache
def cli_user_agent():
    try:
        version = subprocess.run(
            ['agy', '--version'], check=True, capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError('Cannot identify agy; install or update Antigravity CLI') from error
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise RuntimeError('Unexpected agy version; update Antigravity CLI')
    machine = platform.machine().lower()
    arch = {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(machine, machine)
    return (
        f'antigravity/cli/{version} (aidev_client; '
        f'os_type={platform.system().lower()}; arch={arch}; auth_method=consumer)'
    )
