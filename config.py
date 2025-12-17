"""Configuration management for SaltCtl"""

import os
import configparser
from typing import Optional


class SaltCtlConfig:
    """Handle configuration file loading and parsing"""

    # Default configuration values
    DEFAULTS = {
        'salt': {
            'use_sudo': 'false'
        },
        'history': {
            'trim_days': '90'
        }
    }

    def __init__(self):
        self.config = configparser.ConfigParser()

        # Set defaults
        for section, options in self.DEFAULTS.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)

        # Load configuration files in order (later files override earlier ones)
        config_paths = [
            '/etc/saltctl.conf',
            os.path.expanduser('~/.config/saltctl.conf')
        ]
        for path in config_paths:
            if os.path.exists(path):
                try:
                    self.config.read(path)
                except Exception as e:
                    print(f"Warning: Failed to read config file {path}: {e}")

    def get_bool(self, section: str, option: str, fallback: bool = False) -> bool:
        """Get a boolean configuration value"""
        try:
            return self.config.getboolean(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback

    def get_str(self, section: str, option: str, fallback: str = '') -> str:
        """Get a string configuration value"""
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    @property
    def use_sudo(self) -> bool:
        """Whether to use sudo when running salt commands"""
        default = self.DEFAULTS['salt']['use_sudo'] == 'true'
        return self.get_bool('salt', 'use_sudo', fallback=default)

    @property
    def history_trim_days(self) -> int:
        """Number of days to keep in command history before trimming"""
        default = int(self.DEFAULTS['history']['trim_days'])
        try:
            return self.config.getint('history', 'trim_days')
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default


# vim: set ts=4 sw=4 et:
