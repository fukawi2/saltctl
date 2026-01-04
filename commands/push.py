"""Push command - run salt test or apply on selected hosts"""

import subprocess
from .base import BaseCommand


class PushCommand(BaseCommand):
    """Run salt test or apply on selected hosts"""

    @property
    def name(self) -> str:
        return "push"

    @property
    def help_text(self) -> str:
        return """Run salt test or apply on selected hosts.
Usage: push <test|apply>
Examples:
    push test               - Run state.test on selected hosts
    push apply              - Run state.apply on selected hosts"""

    def validate(self, shell, args: str) -> bool:
        if not self.require_selected_hosts(shell):
            return False

        args_list = args.split()
        if not args_list or args_list[0] not in ['test', 'apply']:
            print("Error: Must specify 'test' or 'apply'")
            print("Usage: push <test|apply>")
            return False

        return True

    def execute(self, shell, args: str) -> bool:
        args_list = args.split()
        action = args_list[0]

        # Build salt command
        target = shell.build_target_list()
        salt_cmd = shell.build_salt_cmd("salt", "--list", target, "--state-output=changes", f"state.{action}")
        print(f"Running: {' '.join(salt_cmd)}")
        try:
            result = subprocess.run(
                salt_cmd,
                capture_output=True,
                text=True
            )
            output = result.stdout + result.stderr

            # Log salt output to database
            shell.db.log_salt_output(
                shell.last_command_id,
                action,
                output,
                result.returncode
            )

            # Only show errors to user
            if result.returncode != 0:
                print("Errors detected:")
                print(output)
            else:
                print("Command completed successfully. Run 'output' to show results.")

        except FileNotFoundError:
            print("Error: salt command not found. Is Salt installed?")
        except Exception as e:
            print(f"Error running salt command: {e}")

        return False


# vim: set ts=4 sw=4 et:
