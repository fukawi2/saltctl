"""Tests for select command"""

import pytest
from commands.select import SelectCommand


def test_select_command_name():
    """Test select command has correct name"""
    cmd = SelectCommand()
    assert cmd.name == "select"


def test_select_not_logged():
    """Test select command is not logged to history"""
    cmd = SelectCommand()
    assert cmd.log_in_history == False


def test_select_single_host(mock_shell):
    """Test selecting a single host with partial match"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['host1', 'host2', 'host3']

    cmd.execute(mock_shell, 'host1')

    assert mock_shell.selected_hosts == ['host1']
    mock_shell.update_prompt.assert_called_once()


def test_select_partial_match(mock_shell):
    """Test selecting hosts with partial match (no wildcards)"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['web-server1', 'web-server2', 'db-server1', 'db-server2']

    cmd.execute(mock_shell, 'web')

    assert set(mock_shell.selected_hosts) == {'web-server1', 'web-server2'}


def test_select_partial_match_middle(mock_shell):
    """Test selecting hosts where pattern matches middle of hostname"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['prod-web-01', 'prod-db-01', 'test-web-01']

    cmd.execute(mock_shell, 'web')

    assert set(mock_shell.selected_hosts) == {'prod-web-01', 'test-web-01'}


def test_select_wildcard(mock_shell):
    """Test selecting hosts with explicit wildcard pattern"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['web1', 'web2', 'db1', 'db2', 'myweb']

    cmd.execute(mock_shell, 'web*')

    # Explicit wildcard should only match hosts starting with 'web'
    assert set(mock_shell.selected_hosts) == {'web1', 'web2'}


def test_select_multiple_patterns(mock_shell):
    """Test selecting hosts with multiple patterns"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['web1', 'web2', 'db1', 'db2']

    cmd.execute(mock_shell, 'web1 db*')

    assert set(mock_shell.selected_hosts) == {'web1', 'db1', 'db2'}


def test_select_clear_selection(mock_shell):
    """Test clearing selection with no arguments"""
    cmd = SelectCommand()
    mock_shell.selected_hosts = ['host1', 'host2']

    cmd.execute(mock_shell, '')

    assert mock_shell.selected_hosts == []
    mock_shell.update_prompt.assert_called_once()


def test_select_no_matches(mock_shell):
    """Test selecting with pattern that matches nothing"""
    cmd = SelectCommand()
    mock_shell.all_minions = ['host1', 'host2']

    cmd.execute(mock_shell, 'nonexistent*')

    assert mock_shell.selected_hosts == []


# vim: set ts=4 sw=4 et:
