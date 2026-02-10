"""Output command - show output from executed commands"""

import os
import shutil
import subprocess
from .base import BaseCommand


class OutputCommand(BaseCommand):
    """Show output from executed commands"""

    @property
    def name(self) -> str:
        return "output"

    @property
    def help_text(self) -> str:
        return """Show output from executed commands
Usage: output [command_id]
    output          - Show output from last executed command
    output 123      - Show output from command with ID 123"""

    @property
    def log_in_history(self) -> bool:
        return False

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

    def execute(self, shell, args: str) -> bool:
        command_id = None
        if args.strip():
            try:
                command_id = int(args.strip())
            except ValueError:
                print("Error: Command ID must be a number")
                return False

        # Get the command
        if command_id:
            row = shell.db.get_command_by_id(command_id)
        else:
            row = shell.db.get_most_recent_command()
        if not row:
            if command_id:
                print(f"No command found with ID {command_id}")
            else:
                print("No command history found.")
            return False

        command_id, command, timestamp = row

        # Get salt output for this command
        output_row = shell.db.get_salt_output(command_id)

        if not output_row:
            print(f"Command ID: {command_id}")
            print(f"Command: {command}")
            print(f"Timestamp: {timestamp}")
            print("\nNo output available (command did not produce stored output)")
            return False

        salt_command, output, return_code = output_row

        # Get terminal width for separator line
        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns

        # Build the complete output
        content = f"""Command ID: {command_id}
Command: {command}
Timestamp: {timestamp}
Return code: {return_code}

{'='*terminal_width}
{output}
{'='*terminal_width}
"""

        # Display through pager
        self._display_with_pager(content)

        return False


# vim: set ts=4 sw=4 et:
