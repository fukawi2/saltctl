"""Systemctl command - run systemctl commands on selected hosts"""

import re
import subprocess
from .base import BaseCommand


class SystemctlCommand(BaseCommand):
    """Run systemctl commands on selected hosts using Salt's cmd.run"""

    @property
    def name(self) -> str:
        return "systemctl"

    @property
    def help_text(self) -> str:
        return """Run systemctl commands on selected hosts
Usage: systemctl <action> <service1> [service2] [...]
Examples:
    systemctl restart nginx         - Restart nginx on selected hosts
    systemctl status docker         - Check docker status
    systemctl restart foo bar       - Restart foo and bar services"""

    def validate(self, shell, args: str) -> bool:
        if not self.require_selected_hosts(shell):
            return False

        if not args.strip():
            print("Error: Must specify systemctl command")
            print("Usage: systemctl <action> <service1> [service2] [...]")
            return False

        # Validate that arguments contain only safe characters
        # Allow: alphanumeric, spaces, hyphens, underscores, dots, @, *, ?
        if not re.match(r'^[a-zA-Z0-9\s\-_.@*?]+$', args):
            print("Error: Arguments contain invalid characters")
            print("Allowed: letters, numbers, spaces, hyphens, underscores, dots, @, *, ?")
            return False

        return True

    def execute(self, shell, args: str) -> bool:
        # Build salt command - use cmd.run to execute systemctl
        target = shell.build_target_list()
        systemctl_cmd = f"systemctl {args}"
        salt_cmd = shell.build_salt_cmd("salt", "--list", target, "cmd.run", systemctl_cmd)
        print(f"Running: {' '.join(salt_cmd)}")
        try:
            result = subprocess.run(
                salt_cmd,
                capture_output=True,
                text=True
            )
            output = result.stdout + result.stderr

            if result.returncode != 0:
                content = f"{output}\n\nCommand failed with exit code {result.returncode}"
            else:
                content = output

            self._display_with_pager(content)

        except FileNotFoundError:
            print("Error: salt command not found. Is Salt installed?")
        except Exception as e:
            print(f"Error running salt command: {e}")

        return False


# vim: set ts=4 sw=4 et:
