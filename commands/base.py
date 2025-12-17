"""Base command class for SaltCtl shell commands"""

from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base class for shell commands"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name"""
        pass

    @property
    @abstractmethod
    def help_text(self) -> str:
        """Help text for this command"""
        pass

    @property
    def log_in_history(self) -> bool:
        """Whether this command should be logged in history (default: True)"""
        return True

    def require_selected_hosts(self, shell) -> bool:
        """Ensure the current shell has selected hosts"""
        if not shell.selected_hosts:
            print("Error: No hosts selected. Use 'select' command first.")
            return False
        return True

    def validate(self, shell, args: str) -> bool:
        """Validate command arguments before execution"""
        return True

    @abstractmethod
    def execute(self, shell, args: str) -> bool:
        """Execute the command"""
        pass


# vim: set ts=4 sw=4 et:
