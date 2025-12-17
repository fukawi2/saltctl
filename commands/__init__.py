"""Command registry and loader for SaltCtl shell"""

import os
import importlib
import inspect
from typing import Dict
from .base import BaseCommand


def load_commands() -> Dict[str, BaseCommand]:
    """
    Dynamically load all command classes from the commands directory

    Returns:
        Dictionary mapping command names to command instances
    """
    commands = {}
    current_dir = os.path.dirname(__file__)

    # Get all Python files in the commands directory
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base.py']:
            module_name = filename[:-3]  # Remove .py extension

            # Import the module
            try:
                module = importlib.import_module(f'.{module_name}', package='commands')

                # Find all classes that inherit from BaseCommand
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseCommand) and obj is not BaseCommand:
                        # Instantiate the command
                        cmd_instance = obj()

                        # Register command by its name
                        commands[cmd_instance.name] = cmd_instance

            except Exception as e:
                print(f"Warning: Failed to load command module '{module_name}': {e}")

    return commands


# vim: set ts=4 sw=4 et:
