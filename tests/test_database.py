"""Tests for database module"""

import pytest
from datetime import datetime, timedelta
from database import SaltCtlDatabase


def test_database_initialization(temp_db):
    """Test that database tables are created correctly"""
    # Tables should exist after initialization
    with temp_db._get_connection() as conn:
        cursor = conn.cursor()

        # Check command_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='command_history'")
        assert cursor.fetchone() is not None

        # Check salt_outputs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salt_outputs'")
        assert cursor.fetchone() is not None


def test_log_command(temp_db):
    """Test logging a command to database"""
    command_id = temp_db.log_command(
        username='testuser',
        selected_hosts=['host1', 'host2'],
        command='push test',
        duration=1.5
    )

    assert command_id is not None
    assert command_id > 0

    # Verify it was stored
    row = temp_db.get_command_by_id(command_id)
    assert row is not None
    assert row[1] == 'push test'  # command


def test_update_command_duration(temp_db):
    """Test updating command duration"""
    command_id = temp_db.log_command(
        username='testuser',
        selected_hosts=['host1'],
        command='test command',
        duration=0.0
    )

    temp_db.update_command_duration(command_id, 2.5)

    row = temp_db.get_command_by_id(command_id)
    assert row is not None


def test_log_salt_output(temp_db):
    """Test logging salt output"""
    command_id = temp_db.log_command(
        username='testuser',
        selected_hosts=['host1'],
        command='push test',
        duration=1.0
    )

    temp_db.log_salt_output(
        command_id=command_id,
        salt_command='test',
        output='Salt output here',
        return_code=0
    )

    output = temp_db.get_salt_output(command_id)
    assert output is not None
    assert output[0] == 'test'  # salt_command
    assert output[1] == 'Salt output here'  # output
    assert output[2] == 0  # return_code


def test_get_command_by_id(temp_db):
    """Test retrieving command by ID"""
    command_id = temp_db.log_command(
        username='testuser',
        selected_hosts=['host1', 'host2'],
        command='push apply',
        duration=3.0
    )

    row = temp_db.get_command_by_id(command_id)
    assert row is not None
    assert row[0] == command_id
    assert row[1] == 'push apply'


def test_get_command_by_id_not_found(temp_db):
    """Test retrieving non-existent command returns None"""
    row = temp_db.get_command_by_id(99999)
    assert row is None


def test_get_most_recent_command(temp_db):
    """Test retrieving most recent command"""
    # Log multiple commands
    temp_db.log_command('user1', ['host1'], 'command1', 1.0)
    temp_db.log_command('user1', ['host2'], 'command2', 1.0)
    id3 = temp_db.log_command('user1', ['host3'], 'command3', 1.0)

    row = temp_db.get_most_recent_command()
    assert row is not None
    assert row[0] == id3
    assert row[1] == 'command3'


def test_get_most_recent_command_empty(temp_db):
    """Test retrieving most recent command when history is empty"""
    row = temp_db.get_most_recent_command()
    assert row is None


def test_get_command_history_all(temp_db):
    """Test retrieving all command history"""
    # Log some commands
    temp_db.log_command('user1', ['host1'], 'command1', 1.0)
    temp_db.log_command('user1', ['host2'], 'command2', 1.0)
    temp_db.log_command('user1', ['host3'], 'command3', 1.0)

    rows = temp_db.get_command_history(selected_hosts=None, limit=50)
    assert len(rows) == 3


def test_get_command_history_filtered(temp_db):
    """Test retrieving filtered command history"""
    # Log commands with different hosts
    temp_db.log_command('user1', ['host1', 'host2'], 'command1', 1.0)
    temp_db.log_command('user1', ['host3'], 'command2', 1.0)
    temp_db.log_command('user1', ['host1', 'host2'], 'command3', 1.0)

    # Get only commands for host1 and host2
    rows = temp_db.get_command_history(selected_hosts=['host1', 'host2'], limit=50)
    assert len(rows) == 2


def test_get_command_history_limit(temp_db):
    """Test that limit parameter works"""
    # Log many commands
    for i in range(10):
        temp_db.log_command('user1', ['host1'], f'command{i}', 1.0)

    rows = temp_db.get_command_history(selected_hosts=None, limit=5)
    assert len(rows) == 5


def test_trim_old_history(temp_db):
    """Test trimming old history entries"""
    # Create an old command (100 days ago)
    old_date = (datetime.now() - timedelta(days=100)).isoformat()
    recent_date = datetime.now().isoformat()

    with temp_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO command_history (timestamp, username, selected_hosts, command, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (old_date, 'user1', '[]', 'old_command', 1.0))

        cursor.execute('''
            INSERT INTO command_history (timestamp, username, selected_hosts, command, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (recent_date, 'user1', '[]', 'recent_command', 1.0))

    # Trim entries older than 90 days
    cutoff = (datetime.now() - timedelta(days=90)).isoformat()
    command_count, salt_output_count = temp_db.trim_old_history(cutoff)

    assert command_count == 1
    assert salt_output_count == 0

    # Verify only recent command remains
    rows = temp_db.get_command_history(selected_hosts=None, limit=50)
    assert len(rows) == 1
    assert rows[0][4] == 'recent_command'  # command column


def test_trim_old_history_with_outputs(temp_db):
    """Test that trimming also removes associated salt outputs"""
    # Create old command with output
    old_date = (datetime.now() - timedelta(days=100)).isoformat()

    with temp_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO command_history (timestamp, username, selected_hosts, command, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (old_date, 'user1', '[]', 'old_command', 1.0))
        old_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO salt_outputs (command_id, salt_command, output, return_code)
            VALUES (?, ?, ?, ?)
        ''', (old_id, 'test', 'output', 0))

    # Trim
    cutoff = (datetime.now() - timedelta(days=90)).isoformat()
    command_count, salt_output_count = temp_db.trim_old_history(cutoff)

    assert command_count == 1
    assert salt_output_count == 1


# vim: set ts=4 sw=4 et:
