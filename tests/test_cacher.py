import pytest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
import json

from devenv_cache.cacher import PyPIClient

@patch("urllib.request.urlopen")
def test_fetch_metadata_success(mock_urlopen):
    # Mock PyPI JSON response
    mock_response = MagicMock()
    mock_data = {
        "info": {
            "summary": "A fast web framework.",
            "description": "FastAPI is a modern, fast (high-performance)..."
        }
    }
    mock_response.read.return_value = json.dumps(mock_data).encode("utf-8")
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    client = PyPIClient()
    metadata = client.fetch_metadata("fastapi", "0.110.0")
    
    assert metadata["summary"] == "A fast web framework."
    assert metadata["description"] == "FastAPI is a modern, fast (high-performance)..."
    
    # Assert correct URL was called
    called_args, called_kwargs = mock_urlopen.call_args
    req = called_args[0]
    assert req.full_url == "https://pypi.org/pypi/fastapi/0.110.0/json"
    assert called_kwargs["timeout"] == 10

@patch("urllib.request.urlopen")
def test_fetch_metadata_version_fallback(mock_urlopen):
    # First call: version specific returns 404
    # Second call: fallback returns 200
    mock_response_fallback = MagicMock()
    mock_data = {
        "info": {
            "summary": "FastAPI latest summary",
            "description": "FastAPI description"
        }
    }
    mock_response_fallback.read.return_value = json.dumps(mock_data).encode("utf-8")
    mock_response_fallback.status = 200
    
    # Configure urlopen side_effect
    # HTTPError expects: url, code, msg, hdrs, fp
    err = HTTPError("https://pypi.org/pypi/fastapi/0.110.0/json", 404, "Not Found", {}, None)
    
    def side_effect(url, *args, **kwargs):
        url_str = url.full_url if hasattr(url, "full_url") else url
        if "0.110.0" in url_str:
            raise err
        # Mock Context Manager enter/exit
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_response_fallback
        return mock_ctx

    mock_urlopen.side_effect = side_effect

    client = PyPIClient()
    metadata = client.fetch_metadata("fastapi", "0.110.0")
    
    assert metadata["summary"] == "FastAPI latest summary"
    assert metadata["description"] == "FastAPI description"

@patch("urllib.request.urlopen")
def test_fetch_metadata_not_found(mock_urlopen):
    # Simulate a package that doesn't exist on PyPI at all (404 on both calls)
    err = HTTPError("https://pypi.org/pypi/nonexistent/json", 404, "Not Found", {}, None)
    mock_urlopen.side_effect = err

    client = PyPIClient()
    metadata = client.fetch_metadata("nonexistent")
    
    # Should not crash; returns empty strings for robustness
    assert metadata["summary"] == ""
    assert metadata["description"] == ""
