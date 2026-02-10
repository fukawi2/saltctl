"""Tests for push command"""

import pytest
from unittest.mock import Mock, patch
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


def test_push_error_uses_pager(mock_shell, mock_subprocess):
    """Test that push displays errors through pager"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']
    mock_shell.last_command_id = 1

    # Mock failed command
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = "Error output from salt"
    mock_result.stderr = "Additional error info"
    mock_subprocess.return_value = mock_result

    with patch.object(cmd, '_display_with_pager') as mock_display:
        with patch('shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value = Mock(columns=80)

            cmd.execute(mock_shell, 'test')

            # Verify pager was called
            mock_display.assert_called_once()

            # Verify content includes error information
            content = mock_display.call_args[0][0]
            assert 'Errors detected' in content
            assert 'Return code: 1' in content
            assert 'Error output from salt' in content
            assert 'Additional error info' in content
            assert '=' * 80 in content


def test_push_error_respects_terminal_width(mock_shell, mock_subprocess):
    """Test that error output separator respects terminal width"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']
    mock_shell.last_command_id = 1

    # Mock failed command
    mock_result = Mock()
    mock_result.returncode = 2
    mock_result.stdout = "Error"
    mock_result.stderr = ""
    mock_subprocess.return_value = mock_result

    with patch.object(cmd, '_display_with_pager') as mock_display:
        with patch('shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value = Mock(columns=120)

            cmd.execute(mock_shell, 'test')

            content = mock_display.call_args[0][0]
            # Should have separator of length 120
            assert '=' * 120 in content


def test_push_success_no_pager(mock_shell, mock_subprocess, capsys):
    """Test that successful push doesn't use pager"""
    cmd = PushCommand()
    mock_shell.selected_hosts = ['host1']
    mock_shell.last_command_id = 1

    # Mock successful command
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "Success output"
    mock_result.stderr = ""
    mock_subprocess.return_value = mock_result

    with patch.object(cmd, '_display_with_pager') as mock_display:
        cmd.execute(mock_shell, 'test')

        # Verify pager was NOT called
        mock_display.assert_not_called()

        # Verify success message was printed
        captured = capsys.readouterr()
        assert "Command completed successfully" in captured.out


# vim: set ts=4 sw=4 et:
