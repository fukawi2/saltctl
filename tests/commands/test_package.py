"""Tests for package command"""

import pytest
from commands.package import PackageCommand


def test_package_command_name():
    """Test package command has correct name"""
    cmd = PackageCommand()
    assert cmd.name == "package"


def test_package_logged_to_history():
    """Test package command is logged to history"""
    cmd = PackageCommand()
    assert cmd.log_in_history == True


def test_package_validate_requires_hosts(mock_shell):
    """Test package validation requires selected hosts"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = []

    result = cmd.validate(mock_shell, 'upgrade')

    assert result == False


def test_package_validate_requires_subcommand(mock_shell):
    """Test package validation requires a subcommand"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    # No subcommand provided
    result = cmd.validate(mock_shell, '')
    assert result == False


def test_package_validate_rejects_invalid_subcommand(mock_shell):
    """Test package validation rejects invalid subcommands"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'invalid')
    assert result == False


def test_package_validate_accepts_upgrade(mock_shell):
    """Test package validation accepts 'upgrade' action"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'upgrade')

    assert result == True


def test_package_validate_accepts_install_with_package(mock_shell):
    """Test package validation accepts 'install' with package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'install nginx')

    assert result == True


def test_package_validate_rejects_install_without_package(mock_shell):
    """Test package validation rejects 'install' without package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'install')

    assert result == False


def test_package_validate_accepts_reinstall_with_package(mock_shell):
    """Test package validation accepts 'reinstall' with package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'reinstall nginx')

    assert result == True


def test_package_validate_rejects_reinstall_without_package(mock_shell):
    """Test package validation rejects 'reinstall' without package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'reinstall')

    assert result == False


def test_package_validate_accepts_remove_with_package(mock_shell):
    """Test package validation accepts 'remove' with package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'remove apache2')

    assert result == True


def test_package_validate_rejects_remove_without_package(mock_shell):
    """Test package validation rejects 'remove' without package name"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'remove')

    assert result == False


def test_package_builds_correct_command_for_upgrade(mock_shell, mock_subprocess):
    """Test package builds correct salt command for upgrade"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1', 'host2']

    cmd.execute(mock_shell, 'upgrade')

    # Verify subprocess was called with correct command
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    executed_cmd = call_args[0][0]

    assert 'salt' in executed_cmd
    assert '--list' in executed_cmd
    assert 'host1,host2' in executed_cmd
    assert 'pkg.upgrade' in executed_cmd


def test_package_builds_correct_command_for_install(mock_shell, mock_subprocess):
    """Test package builds correct salt command for install"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1', 'host2']

    cmd.execute(mock_shell, 'install nginx redis')

    # Verify subprocess was called with correct command
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    executed_cmd = call_args[0][0]

    assert 'salt' in executed_cmd
    assert '--list' in executed_cmd
    assert 'host1,host2' in executed_cmd
    assert 'pkg.install' in executed_cmd
    assert 'nginx redis' in executed_cmd


def test_package_builds_correct_command_for_reinstall(mock_shell, mock_subprocess):
    """Test package builds correct salt command for reinstall"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1', 'host2']

    cmd.execute(mock_shell, 'reinstall nginx')

    # Verify subprocess was called with correct command
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    executed_cmd = call_args[0][0]

    assert 'salt' in executed_cmd
    assert '--list' in executed_cmd
    assert 'host1,host2' in executed_cmd
    assert 'pkg.install' in executed_cmd
    assert 'nginx' in executed_cmd
    assert 'reinstall=True' in executed_cmd


def test_package_builds_correct_command_for_remove(mock_shell, mock_subprocess):
    """Test package builds correct salt command for remove"""
    cmd = PackageCommand()
    mock_shell.selected_hosts = ['host1', 'host2']

    cmd.execute(mock_shell, 'remove apache2')

    # Verify subprocess was called with correct command
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    executed_cmd = call_args[0][0]

    assert 'salt' in executed_cmd
    assert '--list' in executed_cmd
    assert 'host1,host2' in executed_cmd
    assert 'pkg.remove' in executed_cmd
    assert 'apache2' in executed_cmd


# vim: set ts=4 sw=4 et:
