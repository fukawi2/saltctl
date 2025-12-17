"""List command - show all available minions"""

from .base import BaseCommand


class ListCommand(BaseCommand):
    """List all available minions"""

    @property
    def name(self) -> str:
        return "hosts"

    @property
    def help_text(self) -> str:
        return """List all available minions
Usage: hosts"""

    @property
    def log_in_history(self) -> bool:
        return False

    def execute(self, shell, args: str) -> bool:
        if shell.all_minions:
            print(f"Available minions ({len(shell.all_minions)}):")
            for minion in shell.all_minions:
                marker = " *" if minion in shell.selected_hosts else ""
                print(f"  {minion}{marker}")
        else:
            print("No minions found.")

        return False


# vim: set ts=4 sw=4 et:
