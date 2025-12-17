"""Status command - show currently selected hosts"""

from .base import BaseCommand


class StatusCommand(BaseCommand):
    """Show currently selected hosts"""

    @property
    def name(self) -> str:
        return "status"

    @property
    def help_text(self) -> str:
        return """Show currently selected hosts
Usage: status"""

    @property
    def log_in_history(self) -> bool:
        return False

    def execute(self, shell, args: str) -> bool:
        if shell.selected_hosts:
            print(f"Currently selected hosts ({len(shell.selected_hosts)}):")
            for host in shell.selected_hosts:
                print(f"  - {host}")
        else:
            print("No hosts currently selected.")

        return False


# vim: set ts=4 sw=4 et:
