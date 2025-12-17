"""Ping command - test connectivity to selected hosts"""

import subprocess
from .base import BaseCommand


class PingCommand(BaseCommand):
    """Test connectivity to selected hosts using test.ping"""

    @property
    def name(self) -> str:
        return "ping"

    @property
    def help_text(self) -> str:
        return """Test connectivity to selected hosts using test.ping
Usage: ping
Example:
    ping                    - Run test.ping on selected hosts"""

    def validate(self, shell, args: str) -> bool:
        return self.require_selected_hosts(shell)

    def execute(self, shell, args: str) -> bool:
        target = shell.build_target_list()
        salt_cmd = shell.build_salt_cmd("salt", "--list", target, "test.ping")
        print(f"Running: {' '.join(salt_cmd)}")
        try:
            result = subprocess.run(
                salt_cmd,
                capture_output=True,
                text=True
            )
            output = result.stdout + result.stderr
            print(output)
            if result.returncode != 0:
                print(f"\nCommand failed with exit code {result.returncode}")

        except FileNotFoundError:
            print("Error: salt command not found. Is Salt installed?")
        except Exception as e:
            print(f"Error running salt command: {e}")

        return False


# vim: set ts=4 sw=4 et:
