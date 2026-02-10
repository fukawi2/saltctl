"""Base command class for SaltCtl shell commands"""

import os
import subprocess
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

    def _display_with_pager(self, content: str) -> None:
        """Display content through a pager if available"""
        # Check for SALTCTL_PAGER first, then fall back to PAGER
        pager = os.environ.get('SALTCTL_PAGER')
        if pager is None:
            pager = os.environ.get('PAGER')

        # If either is explicitly set to empty string, skip paging
        if pager == '':
            print(content)
            return

        # Use pager if set, otherwise default to 'less -RFX'
        # -R: preserve ANSI color codes
        # -F: exit if content fits on one screen
        # -X: don't clear screen on exit
        if pager is None:
            pager = 'less -RFX'

        try:
            # Try to pipe content through pager
            process = subprocess.Popen(
                pager,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=None,  # Use parent's stdout
                stderr=None   # Use parent's stderr
            )
            process.communicate(input=content.encode('utf-8'))
            process.wait()
        except (OSError, subprocess.SubprocessError):
            # If pager fails, fall back to regular print
            print(content)

    @abstractmethod
    def execute(self, shell, args: str) -> bool:
        """Execute the command"""
        pass


# vim: set ts=4 sw=4 et:
