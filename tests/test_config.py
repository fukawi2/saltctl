"""Tests for config module"""

import pytest
from config import SaltCtlConfig


def test_config_defaults():
    """Test that default configuration values are set correctly"""
    config = SaltCtlConfig()

    assert config.use_sudo == False  # Default in DEFAULTS
    assert config.history_trim_days == 90


def test_config_file_loading(temp_config_file, monkeypatch):
    """Test loading configuration from file"""
    # Write test config
    with open(temp_config_file, 'w') as f:
        f.write("[salt]\n")
        f.write("use_sudo = true\n")
        f.write("[history]\n")
        f.write("trim_days = 30\n")

    # Mock the config paths to use our temp file
    monkeypatch.setattr('config.os.path.expanduser', lambda x: temp_config_file)

    config = SaltCtlConfig()

    assert config.use_sudo == True
    assert config.history_trim_days == 30


def test_config_boolean_parsing():
    """Test that boolean values are parsed correctly"""
    config = SaltCtlConfig()

    # Test various boolean representations
    config.config.set('salt', 'use_sudo', 'true')
    assert config.use_sudo == True

    config.config.set('salt', 'use_sudo', 'false')
    assert config.use_sudo == False

    config.config.set('salt', 'use_sudo', '1')
    assert config.use_sudo == True

    config.config.set('salt', 'use_sudo', '0')
    assert config.use_sudo == False


def test_config_int_parsing():
    """Test that integer values are parsed correctly"""
    config = SaltCtlConfig()

    config.config.set('history', 'trim_days', '120')
    assert config.history_trim_days == 120

    config.config.set('history', 'trim_days', '7')
    assert config.history_trim_days == 7


def test_config_fallback_on_missing():
    """Test that fallback values are used when config is missing"""
    config = SaltCtlConfig()

    # Remove the section
    config.config.remove_section('history')

    # Should fall back to default
    assert config.history_trim_days == 90


# vim: set ts=4 sw=4 et:
