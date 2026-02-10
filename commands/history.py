"""History command - show command history"""

import json
from datetime import datetime, timedelta
from .base import BaseCommand


class HistoryCommand(BaseCommand):
    """Show command history"""

    @property
    def name(self) -> str:
        return "history"

    @property
    def help_text(self) -> str:
        return """Show command history
Usage: history [full|trim]
    history       - Show commands for currently selected hosts
    history full  - Show all command history
    history trim  - Delete old entries (configurable via history.trim_days)"""

    @property
    def log_in_history(self) -> bool:
        return False

    def execute(self, shell, args: str) -> bool:
        arg = args.strip().lower()

        # Handle trim command
        if arg == "trim":
            return self._trim_history(shell)

        # Get command history from database
        # Default to 'full' if no hosts selected
        show_all = arg == "full" or not shell.selected_hosts
        if show_all:
            rows = shell.db.get_command_history(selected_hosts=None, limit=50)
            header = "Command history (last 50):"
        else:
            rows = shell.db.get_command_history(selected_hosts=shell.selected_hosts, limit=50)
            header = f"Command history for selected hosts (last 50):"

        if not rows:
            print("  No history found.")
            return False

        # Build output
        lines = [header]

        # Display results in chronological order (oldest to newest)
        for row in reversed(rows):
            cmd_id, timestamp, username, selected_hosts_json, command, duration = row
            hosts = json.loads(selected_hosts_json) if selected_hosts_json else []

            # Format timestamp (remove microseconds)
            ts = timestamp.split('.')[0] if '.' in timestamp else timestamp

            # Format duration
            if duration is not None:
                duration_str = f"{duration:.3f}s"
            else:
                duration_str = "N/A"

            # Format hosts
            if hosts:
                hosts_str = ', '.join(hosts)
            else:
                hosts_str = "(none)"

            lines.append(f"\n[ID: {cmd_id}] [{ts}] {username} ({duration_str}) - Hosts: {hosts_str}")
            lines.append(f"  Command: {command}")

        content = '\n'.join(lines)
        self._display_with_pager(content)

        return False

    def _trim_history(self, shell) -> bool:
        """Delete history entries older than configured trim_days"""
        # Calculate cutoff date
        trim_days = shell.config.history_trim_days
        cutoff_date = datetime.now() - timedelta(days=trim_days)
        cutoff_iso = cutoff_date.isoformat()

        # Trim old history using database method
        command_count, salt_output_count = shell.db.trim_old_history(cutoff_iso)
        if command_count == 0:
            print(f"No entries older than {trim_days} days found.")
            return False

        print(f"Deleted {command_count} command history entries older than {trim_days} days.")
        if salt_output_count > 0:
            print(f"Deleted {salt_output_count} associated salt output entries.")

        return False


# vim: set ts=4 sw=4 et:
