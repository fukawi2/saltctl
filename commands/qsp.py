"""QSP command - run pkg.upgrade on selected hosts"""

import subprocess
from .base import BaseCommand


class QspCommand(BaseCommand):
    """Run pkg.upgrade on selected hosts"""

    @property
    def name(self) -> str:
        return "qsp"

    @property
    def help_text(self) -> str:
        return """Run pkg.upgrade on selected hosts
Usage: qsp
Example:
    qsp                     - Upgrade packages on selected hosts"""

    def validate(self, shell, args: str) -> bool:
        return self.require_selected_hosts(shell)

    def execute(self, shell, args: str) -> bool:
        # Build salt command
        target = shell.build_target_list()
        salt_cmd = shell.build_salt_cmd("salt", "--list", target, "pkg.upgrade")

        print(f"Running: {' '.join(salt_cmd)}")

        try:
            result = subprocess.run(
                salt_cmd,
                capture_output=True,
                text=True
            )

            output = result.stdout + result.stderr

            # Display output
            if result.returncode != 0:
                content = f"Errors detected:\n{output}"
            else:
                content = output

            self._display_with_pager(content)

        except FileNotFoundError:
            print("Error: salt command not found. Is Salt installed?")
        except Exception as e:
            print(f"Error running salt command: {e}")

        return False


# vim: set ts=4 sw=4 et:
