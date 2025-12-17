"""Select command - select hosts to operate on"""

import fnmatch
from .base import BaseCommand


class SelectCommand(BaseCommand):
    """Select hosts to operate on with wildcard support"""

    @property
    def name(self) -> str:
        return "select"

    @property
    def help_text(self) -> str:
        return """Select hosts to operate on. Supports wildcards.
Usage: select [pattern1] [pattern2] ...
Examples:
    select fw*         - Select all hosts starting with 'fw'
    select web1 web2   - Select specific hosts
    select *.nyc       - Select all hosts ending with '.nyc'
    select             - Clear selection"""

    @property
    def log_in_history(self) -> bool:
        return False

    def execute(self, shell, args: str) -> bool:
        if not args.strip():
            # Clear selection
            shell.selected_hosts = []
            print("Selection cleared.")
        else:
            patterns = args.split()
            matched_hosts = set()
            for pattern in patterns:
                matches = self._match_hosts(shell, pattern)
                if matches:
                    matched_hosts.update(matches)
                else:
                    print(f"Warning: No hosts matched pattern '{pattern}'")

            shell.selected_hosts = sorted(list(matched_hosts))
            if shell.selected_hosts:
                print(f"Selected {len(shell.selected_hosts)} host(s):")
                for host in shell.selected_hosts:
                    print(f"  - {host}")
            else:
                print("No hosts selected.")

        shell.update_prompt()
        return False

    def _match_hosts(self, shell, pattern: str):
        """Match hosts using wildcard pattern"""
        return [host for host in shell.all_minions if fnmatch.fnmatch(host, pattern)]


# vim: set ts=4 sw=4 et:
