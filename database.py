"""Database module for SaltCtl command history and salt outputs"""

import sqlite3
import os
import json
from typing import List, Optional
from datetime import datetime
from contextlib import contextmanager


class SaltCtlDatabase:
    """Handle SQLite database operations for SaltCtl"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.saltctl.db")
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self):
        """Initialize database and create tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create command_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    username TEXT NOT NULL,
                    selected_hosts TEXT,
                    command TEXT NOT NULL,
                    duration REAL
                )
            ''')

            # Create salt_outputs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS salt_outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id INTEGER NOT NULL,
                    salt_command TEXT NOT NULL,
                    output TEXT,
                    return_code INTEGER,
                    FOREIGN KEY (command_id) REFERENCES command_history (id)
                )
            ''')

    def log_command(self, username: str, selected_hosts: List[str],
                    command: str, duration: float) -> int:
        """
        Log a command to the database

        Args:
            username: Username of the user running the command
            selected_hosts: List of currently selected hosts
            command: The command line that was executed
            duration: Duration in seconds the command took

        Returns:
            The ID of the inserted row
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()
            hosts_json = json.dumps(selected_hosts)

            cursor.execute('''
                INSERT INTO command_history (timestamp, username, selected_hosts, command, duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, username, hosts_json, command, duration))

            return cursor.lastrowid

    def log_salt_output(self, command_id: int, salt_command: str,
                        output: str, return_code: int):
        """
        Log salt command output to the database

        Args:
            command_id: ID of the command in command_history table
            salt_command: Type of salt command ("test" or "apply")
            output: Full output from the salt command
            return_code: Return code from the salt command
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO salt_outputs (command_id, salt_command, output, return_code)
                VALUES (?, ?, ?, ?)
            ''', (command_id, salt_command, output, return_code))

    def update_command_duration(self, command_id: int, duration: float):
        """
        Update the duration of a command after execution

        Args:
            command_id: ID of the command in command_history table
            duration: Duration in seconds the command took
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE command_history
                SET duration = ?
                WHERE id = ?
            ''', (duration, command_id))

    def get_command_by_id(self, command_id: int) -> Optional[tuple]:
        """
        Get command information by ID

        Args:
            command_id: ID of the command

        Returns:
            Tuple of (id, command, timestamp) or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, command, timestamp
                FROM command_history
                WHERE id = ?
            ''', (command_id,))

            return cursor.fetchone()

    def get_most_recent_command(self) -> Optional[tuple]:
        """
        Get the most recent command from history

        Returns:
            Tuple of (id, command, timestamp) or None if no history
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, command, timestamp
                FROM command_history
                ORDER BY id DESC
                LIMIT 1
            ''')

            return cursor.fetchone()

    def get_salt_output(self, command_id: int) -> Optional[tuple]:
        """
        Get salt output for a command

        Args:
            command_id: ID of the command

        Returns:
            Tuple of (salt_command, output, return_code) or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT salt_command, output, return_code
                FROM salt_outputs
                WHERE command_id = ?
            ''', (command_id,))

            return cursor.fetchone()

    def get_command_history(self, selected_hosts: Optional[List[str]] = None,
                           limit: int = 50) -> List[tuple]:
        """
        Get command history, optionally filtered by selected hosts

        Args:
            selected_hosts: List of hosts to filter by, or None for all commands
            limit: Maximum number of commands to return

        Returns:
            List of tuples (id, timestamp, username, selected_hosts_json, command, duration)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if selected_hosts:
                selected_json = json.dumps(selected_hosts)
                cursor.execute('''
                    SELECT id, timestamp, username, selected_hosts, command, duration
                    FROM command_history
                    WHERE selected_hosts = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (selected_json, limit))
            else:
                cursor.execute('''
                    SELECT id, timestamp, username, selected_hosts, command, duration
                    FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

            return cursor.fetchall()

    def trim_old_history(self, cutoff_iso: str) -> tuple:
        """
        Delete history entries older than cutoff date

        Args:
            cutoff_iso: ISO format date string for cutoff

        Returns:
            Tuple of (command_count, salt_output_count) deleted
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Count entries to delete
            cursor.execute('''
                SELECT COUNT(*) FROM command_history
                WHERE timestamp < ?
            ''', (cutoff_iso,))
            command_count = cursor.fetchone()[0]

            if command_count == 0:
                return (0, 0)

            # Delete salt_outputs first (foreign key constraint)
            cursor.execute('''
                DELETE FROM salt_outputs
                WHERE command_id IN (
                    SELECT id FROM command_history
                    WHERE timestamp < ?
                )
            ''', (cutoff_iso,))
            salt_output_count = cursor.rowcount

            # Delete command_history entries
            cursor.execute('''
                DELETE FROM command_history
                WHERE timestamp < ?
            ''', (cutoff_iso,))

            return (command_count, salt_output_count)


# vim: set ts=4 sw=4 et:
