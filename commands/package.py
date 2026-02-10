"""Package command - manage packages on selected hosts"""

import subprocess
from .base import BaseCommand

class PackageCommand(BaseCommand):
    """Manage packages on selected hosts"""

    @property
    def name(self) -> str:
        return "package"

    @property
    def help_text(self) -> str:
        return """Manage packages on selected hosts
Usage: package <upgrade|install|reinstall|remove> [package...]
Examples:
    package upgrade                 - Upgrade all packages on selected hosts
    package install nginx           - Install nginx package
    package install nginx redis     - Install multiple packages
    package reinstall nginx         - Reinstall nginx package
    package remove apache2          - Remove apache2 package"""

    def validate(self, shell, args: str) -> bool:
        if not self.require_selected_hosts(shell):
            return False

        args_list = args.split()
        if not args_list:
            print("Error: Must specify a subcommand (upgrade, install, reinstall, or remove)")
            print("Usage: package <upgrade|install|reinstall|remove> [package...]")
            return False

        subcommand = args_list[0]
        if subcommand not in ['upgrade', 'install', 'reinstall', 'remove']:
            print(f"Error: Unknown subcommand '{subcommand}'")
            print("Valid subcommands: upgrade, install, reinstall, remove")
            return False

        # install, reinstall, and remove require at least one package name
        if subcommand in ['install', 'reinstall', 'remove'] and len(args_list) < 2:
            print(f"Error: '{subcommand}' requires at least one package name")
            print(f"Usage: package {subcommand} <package> [package...]")
            return False

        return True

    def execute(self, shell, args: str) -> bool:
        args_list = args.split()
        subcommand = args_list[0]

        # Build salt command based on subcommand
        target = shell.build_target_list()

        if subcommand == 'upgrade':
            salt_cmd = shell.build_salt_cmd("salt", "--list", target, "pkg.upgrade")
        elif subcommand == 'reinstall':
            packages = ' '.join(args_list[1:])
            salt_cmd = shell.build_salt_cmd("salt", "--list", target, "pkg.install", packages, "reinstall=True")
        else:  # install or remove
            packages = ' '.join(args_list[1:])
            salt_cmd = shell.build_salt_cmd("salt", "--list", target, f"pkg.{subcommand}", packages)

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
