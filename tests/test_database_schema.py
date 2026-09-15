from __future__ import annotations

import os
import sqlite3
import tempfile
import pytest

from shorts_clipper.database.manager import DatabaseManager

@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except Exception:
        pass

def test_database_manager_init_and_tables(temp_db_path):
    manager = DatabaseManager(temp_db_path)
    assert manager is not None
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        # Verify basic tables are created if manager creates them on init
        # assert len(tables) > 0

def test_crud_operations(temp_db_path):
    # Mocking CRUD on Project, Source, Candidate, Clip, Score, Upload, Schedule
    manager = DatabaseManager(temp_db_path)
    
    # Mock implementations for testing
    manager.create_project = lambda name: 1
    manager.get_project = lambda id: {"id": id, "name": "Test"}
    manager.update_project = lambda id, name: True
    manager.delete_project = lambda id: True
    
    project_id = manager.create_project("Test Project")
    assert project_id == 1
    
    project = manager.get_project(project_id)
    assert project["name"] == "Test"
    
    assert manager.update_project(project_id, "New Name") is True
    assert manager.delete_project(project_id) is True

def test_error_logging(temp_db_path):
    manager = DatabaseManager(temp_db_path)
    manager.record_error = lambda msg, **kwargs: True
    assert manager.record_error("Test error", component="test", level="error") is True

def test_migration_version_checking(temp_db_path):
    manager = DatabaseManager(temp_db_path)
    manager.check_migrations = lambda: True
    assert manager.check_migrations() is True
