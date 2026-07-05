import pytest
import os
import sqlite3
from devenv_cache.database import DatabaseManager

def test_init_db(tmp_path):
    db_path = os.path.join(tmp_path, "test.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    
    # Verify tables exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    assert "packages" in tables
    assert "packages_fts" in tables
    db.close()

def test_insert_and_get_package(tmp_path):
    db_path = os.path.join(tmp_path, "test.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    
    db.insert_package(
        name="fastapi",
        version="0.110.0",
        summary="FastAPI framework",
        documentation="FastAPI is a modern web framework..."
    )
    
    pkg = db.get_package("fastapi")
    assert pkg is not None
    assert pkg["name"] == "fastapi"
    assert pkg["version"] == "0.110.0"
    assert pkg["summary"] == "FastAPI framework"
    assert pkg["documentation"] == "FastAPI is a modern web framework..."
    
    # Test case insensitivity/normalization
    pkg2 = db.get_package("FastAPI")
    assert pkg2 is not None
    assert pkg2["name"] == "fastapi"
    
    db.close()

def test_search_packages(tmp_path):
    db_path = os.path.join(tmp_path, "test.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    
    db.insert_package(
        name="fastapi",
        version="0.110.0",
        summary="FastAPI framework",
        documentation="High performance web framework."
    )
    
    db.insert_package(
        name="structlog",
        version="24.1.0",
        summary="Structured logging",
        documentation="Structured logging for Python applications."
    )
    
    # Search for keyword "logging"
    results = db.search_packages("logging")
    assert len(results) == 1
    assert results[0]["name"] == "structlog"
    
    # Search for keyword "performance"
    results2 = db.search_packages("performance")
    assert len(results2) == 1
    assert results2[0]["name"] == "fastapi"
    
    db.close()
