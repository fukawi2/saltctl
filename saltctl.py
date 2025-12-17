#!/usr/bin/python3
"""
Interactive shell for managing Salt minions - Main script.
"""

import sys
import os
import time
import subprocess
import json
import readline
from typing import List, Dict
from commands import load_commands
from commands.base import BaseCommand
from database import SaltCtlDatabase
from config import SaltCtlConfig

class SaltCtlShell:
    def __init__(self):
        self.selected_hosts: List[str] = []
        self.all_minions: List[str] = []
        self.db = SaltCtlDatabase()
        self.config = SaltCtlConfig()
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
        self.commands: Dict[str, BaseCommand] = load_commands()
        self.running = True
        self.last_command_id = None
        self.readline_history_file = os.path.expanduser("~/.saltctl_history")
        self._setup_readline()
        self.refresh_minions()
        self.update_prompt()

    def update_prompt(self):
        """Update prompt to show selected hosts"""
        if self.selected_hosts:
            host_summary = f"{len(self.selected_hosts)} host(s)"
            self.prompt = f"saltctl [{host_summary}]> "
        else:
            self.prompt = "saltctl> "

    def build_salt_cmd(self, *args):
        """Build salt command with sudo if configured"""
        cmd = list(args)
        if self.config.use_sudo:
            cmd.insert(0, "sudo")
        return cmd

    def build_target_list(self):
        """Build comma-separated list of selected hosts for salt --list"""
        return ','.join(self.selected_hosts)

    def refresh_minions(self):
        """Refresh the list of available minions from salt-key"""
        try:
            cmd = self.build_salt_cmd("salt-key", "--list=accepted", "--out=json")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            if 'minions' in data:
                self.all_minions = data['minions']
            else:
                print(f"Error: Unexpected salt-key output format - missing 'minions' key")
                sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to get minion list: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Error: salt-key command not found. Is Salt installed?")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse minion list JSON: {e}")
            sys.exit(1)
        except KeyError as e:
            print(f"Error: Unexpected salt-key output structure: {e}")
            sys.exit(1)

    def _setup_readline(self):
        """Configure readline for command history and editing"""
        # Load history file
        try:
            readline.read_history_file(self.readline_history_file)
        except FileNotFoundError:
            # History file doesn't exist yet
            pass

        # Set maximum history length
        readline.set_history_length(1000)

        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self._completer)

    def _completer(self, text, state):
        """Tab completion for commands"""
        options = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        return None

    def run_command(self, cmdLine: str) -> bool:
        """
        Parse and execute a command line

        Returns:
            True to exit the shell, False to continue
        """
        cmdLine = line.strip()
        if not cmdLine:
            return False

        # Split into command and arguments
        parts = cmdLine.split(None, 1)
        cmdInput = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Handle built-in exit command
        if cmdInput in ('exit', 'quit'):
            print("Goodbye!")
            return True

        start_time = time.time()
        result = False
        executed_command = None

        # Check for exact match first
        if cmdInput in self.commands:
            executed_command = self.commands[cmdInput]
        else:
            # Try shortest unique prefix matching
            matches = [name for name in self.commands.keys() if name.startswith(cmdInput)]
            if len(matches) == 1:
                # Unique match found
                executed_command = self.commands[matches[0]]
            elif len(matches) > 1:
                print(f"Ambiguous command '{cmdInput}'. Matches: {', '.join(sorted(set(matches)))}")
                return False
            else:
                print(f"Unknown command: {cmdInput}")
                print("Type 'help' for available commands.")
                return False

        # Validate command before logging/execution
        if not executed_command.validate(self, args):
            return False

        # Log to database BEFORE execution (when required)
        if executed_command.log_in_history:
            command_id = self.db.log_command(
                self.username,
                self.selected_hosts,
                line,
                0.0  # Duration will be updated after execution
            )
            self.last_command_id = command_id

        # Execute the command
        result = executed_command.execute(self, args)

        # Update duration if command was logged
        if executed_command.log_in_history:
            duration = time.time() - start_time
            self.db.update_command_duration(command_id, duration)

        return result

    def mainInputLoop(self):
        """The main command user input loop"""
        print("SaltCtl - Salt Minion Management")
        print("Type 'help' for available commands.\n")

        try:
            while self.running:
                try:
                    line = input(self.prompt)
                    should_exit = self.run_command(line)
                    if should_exit:
                        break
                except EOFError:
                    # Ctrl-D
                    print()
                    print("Goodbye!")
                    break
                except KeyboardInterrupt:
                    # Ctrl-C
                    print()
                    print("Adios!")
                    break
        finally:
            # Save readline history on exit
            readline.write_history_file(self.readline_history_file)


def main():
    """Main entry point"""
    try:
        shell = SaltCtlShell()
        shell.mainInputLoop()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()


# vim: set ts=4 sw=4 et:
