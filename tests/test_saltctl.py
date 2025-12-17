"""Tests for saltctl shell module"""

import pytest
from unittest.mock import Mock
from saltctl import SaltCtlShell


def test_build_salt_cmd_with_sudo():
    """Test building salt command with sudo enabled"""
    shell = Mock(spec=SaltCtlShell)
    shell.config = Mock()
    shell.config.use_sudo = True

    cmd = SaltCtlShell.build_salt_cmd(shell, "salt", "--list", "host1", "test.ping")

    assert cmd == ["sudo", "salt", "--list", "host1", "test.ping"]


def test_build_salt_cmd_without_sudo():
    """Test building salt command without sudo"""
    shell = Mock(spec=SaltCtlShell)
    shell.config = Mock()
    shell.config.use_sudo = False

    cmd = SaltCtlShell.build_salt_cmd(shell, "salt", "--list", "host1", "test.ping")

    assert cmd == ["salt", "--list", "host1", "test.ping"]


def test_build_target_list():
    """Test building comma-separated target list"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = ['host1', 'host2', 'host3']

    target = SaltCtlShell.build_target_list(shell)

    assert target == "host1,host2,host3"


def test_build_target_list_empty():
    """Test building target list with no hosts"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = []

    target = SaltCtlShell.build_target_list(shell)

    assert target == ""


def test_build_target_list_single():
    """Test building target list with single host"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = ['host1']

    target = SaltCtlShell.build_target_list(shell)

    assert target == "host1"


def test_update_prompt_with_hosts():
    """Test prompt updates to show selected hosts"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = ['host1', 'host2']

    SaltCtlShell.update_prompt(shell)

    assert shell.prompt == "saltctl [2 host(s)]> "


def test_update_prompt_without_hosts():
    """Test prompt with no hosts selected"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = []

    SaltCtlShell.update_prompt(shell)

    assert shell.prompt == "saltctl> "


# vim: set ts=4 sw=4 et:
