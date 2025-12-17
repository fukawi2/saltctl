"""Tests for history command"""

import pytest
from datetime import datetime, timedelta
from commands.history import HistoryCommand


def test_history_command_name():
    """Test history command has correct name"""
    cmd = HistoryCommand()
    assert cmd.name == "history"


def test_history_not_logged():
    """Test history command is not logged to history"""
    cmd = HistoryCommand()
    assert cmd.log_in_history == False


def test_history_show_all(mock_shell):
    """Test showing all command history"""
    cmd = HistoryCommand()
    mock_shell.selected_hosts = []
    mock_shell.db.get_command_history.return_value = [
        (1, '2024-01-01T10:00:00', 'user1', '["host1"]', 'push test', 1.5)
    ]

    cmd.execute(mock_shell, 'full')

    mock_shell.db.get_command_history.assert_called_once_with(selected_hosts=None, limit=50)


def test_history_show_filtered(mock_shell):
    """Test showing filtered command history"""
    cmd = HistoryCommand()
    mock_shell.selected_hosts = ['host1', 'host2']
    mock_shell.db.get_command_history.return_value = []

    cmd.execute(mock_shell, '')

    mock_shell.db.get_command_history.assert_called_once_with(
        selected_hosts=['host1', 'host2'],
        limit=50
    )


def test_history_trim(mock_shell):
    """Test trimming old history"""
    cmd = HistoryCommand()
    mock_shell.config.history_trim_days = 90
    mock_shell.db.trim_old_history.return_value = (10, 5)

    result = cmd.execute(mock_shell, 'trim')

    assert result == False
    mock_shell.db.trim_old_history.assert_called_once()


def test_history_trim_nothing_to_delete(mock_shell):
    """Test trimming when nothing old enough to delete"""
    cmd = HistoryCommand()
    mock_shell.config.history_trim_days = 90
    mock_shell.db.trim_old_history.return_value = (0, 0)

    result = cmd.execute(mock_shell, 'trim')

    assert result == False


# vim: set ts=4 sw=4 et:
