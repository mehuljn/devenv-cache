import pytest
import os
from unittest.mock import patch, MagicMock
from devenv_cache.cli import main
from devenv_cache.database import DatabaseManager

def test_cli_init(tmp_path, monkeypatch):
    # Change working directory to tmp_path
    monkeypatch.chdir(tmp_path)
    
    # Run CLI init
    with pytest.raises(SystemExit) as excinfo:
        main(["init"])
    assert excinfo.value.code == 0
    
    db_path = os.path.join(tmp_path, ".devenv-cache", "docs.sqlite")
    assert os.path.exists(db_path)
    
    # Verify DB is initialized and tables exist
    db = DatabaseManager(db_path)
    pkg = db.get_package("nonexistent")
    assert pkg is None
    db.close()

@patch("urllib.request.urlopen")
def test_cli_sync(mock_urlopen, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Setup mock poetry.lock file
    lockfile_path = os.path.join(tmp_path, "poetry.lock")
    with open(lockfile_path, "w") as f:
        f.write("""
        [[package]]
        name = "fastapi"
        version = "0.110.0"
        """)
        
    # Mock PyPI JSON response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"info": {"summary": "A fast framework", "description": "FastAPI doc content"}}'
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response
    
    # Run CLI init first
    with pytest.raises(SystemExit) as excinfo:
        main(["init"])
    assert excinfo.value.code == 0
    
    # Run CLI sync
    with pytest.raises(SystemExit) as excinfo:
        main(["sync"])
    assert excinfo.value.code == 0
    
    # Verify package is synced into DB
    db_path = os.path.join(tmp_path, ".devenv-cache", "docs.sqlite")
    db = DatabaseManager(db_path)
    pkg = db.get_package("fastapi")
    assert pkg is not None
    assert pkg["version"] == "0.110.0"
    assert pkg["summary"] == "A fast framework"
    assert pkg["documentation"] == "FastAPI doc content"
    db.close()
