"""Shared pytest fixtures for saltctl tests"""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock
from database import SaltCtlDatabase
from config import SaltCtlConfig
from saltctl import SaltCtlShell


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name

    db = SaltCtlDatabase(db_path)
    yield db

    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.conf') as f:
        yield f.name

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def mock_shell():
    """Create a mock shell for testing commands"""
    shell = Mock(spec=SaltCtlShell)
    shell.selected_hosts = []
    shell.all_minions = ['host1', 'host2', 'host3']
    shell.db = Mock()
    shell.config = Mock()
    shell.config.use_sudo = True
    shell.config.history_trim_days = 90
    shell.last_command_id = None

    # Add helper methods
    def build_salt_cmd(*args):
        cmd = list(args)
        if shell.config.use_sudo:
            cmd.insert(0, "sudo")
        return cmd

    def build_target_list():
        return ','.join(shell.selected_hosts)

    shell.build_salt_cmd = build_salt_cmd
    shell.build_target_list = build_target_list

    return shell


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess.run to avoid actual command execution"""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mock_run = Mock(return_value=mock_result)
    monkeypatch.setattr('subprocess.run', mock_run)

    return mock_run


# vim: set ts=4 sw=4 et:
