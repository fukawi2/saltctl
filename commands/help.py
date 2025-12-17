"""Help command - show available commands"""

from .base import BaseCommand


class HelpCommand(BaseCommand):
    """Show available commands"""

    @property
    def name(self) -> str:
        return "help"

    @property
    def help_text(self) -> str:
        return """Show available commands
Usage: help [command]"""

    @property
    def log_in_history(self) -> bool:
        return False

    def execute(self, shell, args: str) -> bool:
        if args.strip():
            # Show help for specific command
            cmd_name = args.strip()
            if cmd_name in ('exit', 'quit'):
                print("\nExit the shell\nUsage: exit\n")
            elif cmd_name in shell.commands:
                cmd = shell.commands[cmd_name]
                print(f"\n{cmd.help_text}\n")
            else:
                print(f"Unknown command: {cmd_name}")
        else:
            # Show all commands
            print("\nAvailable commands:")
            for cmd_name in sorted(shell.commands.keys()):
                cmd = shell.commands[cmd_name]

                # Get first line of help text
                first_line = cmd.help_text.split('\n')[0]
                print(f"  {cmd_name:<15} - {first_line}")

            # Add built-in commands
            print(f"  {'exit':<15} - Exit the shell")

            print("\nCommands support shortest unique prefix matching.")
            print("Type 'help <command>' for detailed help on a specific command.\n")

        return False


# vim: set ts=4 sw=4 et:
