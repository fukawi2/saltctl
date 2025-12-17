"""Tests for push command"""

import pytest
from commands.push import PushCommand


def test_push_command_name():
    """Test push command has correct name"""
    cmd = PushCommand()
    assert cmd.name == "push"


def test_push_logged_to_history():
    """Test push command is logged to history"""
    cmd = PushCommand()
    assert cmd.log_in_history == True


def test_push_validate_requires_hosts(mock_shell):
    """Test push validation requires selected hosts"""
    cmd = PushCommand()
    mock_shell.selected_hosts = []

    result = cmd.validate(mock_shell, 'test')

    assert result == False


def test_push_validate_requires_action(mock_shell):
    """Test push validation requires test or apply"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']

    # No action provided
    result = cmd.validate(mock_shell, '')
    assert result == False

    # Invalid action
    result = cmd.validate(mock_shell, 'invalid')
    assert result == False


def test_push_validate_accepts_test(mock_shell):
    """Test push validation accepts 'test' action"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'test')

    assert result == True


def test_push_validate_accepts_apply(mock_shell):
    """Test push validation accepts 'apply' action"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']

    result = cmd.validate(mock_shell, 'apply')

    assert result == True


def test_push_builds_correct_command(mock_shell, mock_subprocess):
    """Test push builds correct salt command"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1', 'host2']
    mock_shell.last_command_id = 1

    cmd.execute(mock_shell, 'test')

    # Verify subprocess was called with correct command
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args
    executed_cmd = call_args[0][0]

    assert 'salt' in executed_cmd
    assert '--list' in executed_cmd
    assert 'host1,host2' in executed_cmd
    assert 'state.test' in executed_cmd


# vim: set ts=4 sw=4 et:
