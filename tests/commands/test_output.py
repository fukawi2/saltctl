"""Tests for output command"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from commands.output import OutputCommand


def test_output_command_name():
    """Test output command has correct name"""
    cmd = OutputCommand()
    assert cmd.name == "output"


def test_output_not_logged():
    """Test output command is not logged to history"""
    cmd = OutputCommand()
    assert cmd.log_in_history == False


def test_display_with_pager_uses_saltctl_pager(capsys):
    """Test that SALTCTL_PAGER takes precedence over PAGER"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {'SALTCTL_PAGER': 'cat', 'PAGER': 'less'}):
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_popen.return_value = mock_process

            cmd._display_with_pager(content)

            mock_popen.assert_called_once()
            # Verify it used SALTCTL_PAGER (cat) not PAGER (less)
            assert mock_popen.call_args[0][0] == 'cat'


def test_display_with_pager_falls_back_to_pager(capsys):
    """Test that PAGER is used when SALTCTL_PAGER is not set"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {'PAGER': 'more'}, clear=True):
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_popen.return_value = mock_process

            cmd._display_with_pager(content)

            mock_popen.assert_called_once()
            assert mock_popen.call_args[0][0] == 'more'


def test_display_with_pager_uses_default_when_neither_set(capsys):
    """Test that 'less -RFX' is used when neither SALTCTL_PAGER nor PAGER is set"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {}, clear=True):
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_popen.return_value = mock_process

            cmd._display_with_pager(content)

            mock_popen.assert_called_once()
            assert mock_popen.call_args[0][0] == 'less -RFX'


def test_display_with_pager_empty_saltctl_pager_disables_paging(capsys):
    """Test that empty SALTCTL_PAGER disables paging"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {'SALTCTL_PAGER': '', 'PAGER': 'less'}):
        with patch('subprocess.Popen') as mock_popen:
            cmd._display_with_pager(content)

            # Should not call pager
            mock_popen.assert_not_called()

            # Should print directly
            captured = capsys.readouterr()
            assert "test output" in captured.out


def test_display_with_pager_empty_pager_disables_paging(capsys):
    """Test that empty PAGER disables paging when SALTCTL_PAGER is not set"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {'PAGER': ''}, clear=True):
        with patch('subprocess.Popen') as mock_popen:
            cmd._display_with_pager(content)

            # Should not call pager
            mock_popen.assert_not_called()

            # Should print directly
            captured = capsys.readouterr()
            assert "test output" in captured.out


def test_display_with_pager_fallback_on_error(capsys):
    """Test that pager falls back to print when subprocess fails"""
    cmd = OutputCommand()
    content = "test output"

    with patch.dict('os.environ', {'PAGER': 'nonexistent-pager'}):
        with patch('subprocess.Popen', side_effect=OSError("Pager not found")):
            cmd._display_with_pager(content)

            # Should fall back to print
            captured = capsys.readouterr()
            assert "test output" in captured.out


def test_execute_invalid_command_id(mock_shell, capsys):
    """Test executing with invalid (non-numeric) command ID"""
    cmd = OutputCommand()

    result = cmd.execute(mock_shell, 'invalid')

    assert result == False
    captured = capsys.readouterr()
    assert "Error: Command ID must be a number" in captured.out


def test_execute_command_not_found(mock_shell, capsys):
    """Test executing with command ID that doesn't exist"""
    cmd = OutputCommand()
    mock_shell.db.get_command_by_id.return_value = None

    result = cmd.execute(mock_shell, '999')

    assert result == False
    captured = capsys.readouterr()
    assert "No command found with ID 999" in captured.out


def test_execute_no_command_history(mock_shell, capsys):
    """Test executing when no command history exists"""
    cmd = OutputCommand()
    mock_shell.db.get_most_recent_command.return_value = None

    result = cmd.execute(mock_shell, '')

    assert result == False
    captured = capsys.readouterr()
    assert "No command history found" in captured.out


def test_execute_no_output_available(mock_shell, capsys):
    """Test executing when command has no stored output"""
    cmd = OutputCommand()
    mock_shell.db.get_most_recent_command.return_value = (1, 'push test', '2025-01-01 12:00:00')
    mock_shell.db.get_salt_output.return_value = None

    result = cmd.execute(mock_shell, '')

    assert result == False
    captured = capsys.readouterr()
    assert "No output available" in captured.out


def test_execute_displays_output_with_pager(mock_shell):
    """Test executing displays output through pager"""
    cmd = OutputCommand()
    mock_shell.db.get_most_recent_command.return_value = (1, 'push test', '2025-01-01 12:00:00')
    mock_shell.db.get_salt_output.return_value = (
        'salt --list host1 state.test',
        'Salt output here\nMultiple lines',
        0
    )

    with patch.object(cmd, '_display_with_pager') as mock_display:
        with patch('shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value = Mock(columns=80)

            result = cmd.execute(mock_shell, '')

            assert result == False
            mock_display.assert_called_once()

            # Verify content includes all expected parts
            content = mock_display.call_args[0][0]
            assert 'Command ID: 1' in content
            assert 'Command: push test' in content
            assert 'Timestamp: 2025-01-01 12:00:00' in content
            assert 'Return code: 0' in content
            assert 'Salt output here' in content
            assert '=' * 80 in content


def test_execute_with_specific_command_id(mock_shell):
    """Test executing with specific command ID"""
    cmd = OutputCommand()
    mock_shell.db.get_command_by_id.return_value = (5, 'push apply', '2025-01-02 14:30:00')
    mock_shell.db.get_salt_output.return_value = (
        'salt --list host2 state.apply',
        'Applied successfully',
        0
    )

    with patch.object(cmd, '_display_with_pager') as mock_display:
        with patch('shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value = Mock(columns=120)

            result = cmd.execute(mock_shell, '5')

            assert result == False
            mock_shell.db.get_command_by_id.assert_called_once_with(5)

            # Verify it used the right command ID
            content = mock_display.call_args[0][0]
            assert 'Command ID: 5' in content
            assert 'Command: push apply' in content


def test_execute_respects_terminal_width(mock_shell):
    """Test that separator respects terminal width"""
    cmd = OutputCommand()
    mock_shell.db.get_most_recent_command.return_value = (1, 'test', '2025-01-01 12:00:00')
    mock_shell.db.get_salt_output.return_value = ('cmd', 'output', 0)

    with patch.object(cmd, '_display_with_pager') as mock_display:
        with patch('shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value = Mock(columns=100)

            cmd.execute(mock_shell, '')

            content = mock_display.call_args[0][0]
            # Should have separator of length 100
            assert '=' * 100 in content


# vim: set ts=4 sw=4 et:
