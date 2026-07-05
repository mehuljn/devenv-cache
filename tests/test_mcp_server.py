import pytest
import json
import io
import sys
from unittest.mock import MagicMock

from devenv_cache.mcp_server import MCPServer
from devenv_cache.database import DatabaseManager

def test_mcp_initialize():
    server = MCPServer(db_path=":memory:")
    
    # Initialize request
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    
    response = server.handle_message(req)
    assert response is not None
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert response["result"]["protocolVersion"] == "2024-11-05"
    assert response["result"]["serverInfo"]["name"] == "devenv-cache"

def test_mcp_list_tools():
    server = MCPServer(db_path=":memory:")
    
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = server.handle_message(req)
    assert response is not None
    assert response["id"] == 2
    assert "result" in response
    tools = response["result"]["tools"]
    assert len(tools) == 2
    tool_names = [t["name"] for t in tools]
    assert "search_dependency_docs" in tool_names
    assert "get_package_docs" in tool_names

def test_mcp_call_tool_search(tmp_path):
    import os
    db_path = os.path.join(tmp_path, "test.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    db.insert_package(
        name="structlog",
        version="24.1.0",
        summary="Structured logging for Python",
        documentation="Structlog details go here."
    )
    db.close()
    
    server = MCPServer(db_path=db_path)
    
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_dependency_docs",
            "arguments": {"query": "logging"}
        }
    }
    
    response = server.handle_message(req)
    assert response is not None
    assert response["id"] == 3
    assert "result" in response
    content = response["result"]["content"]
    assert len(content) == 1
    assert "structlog" in content[0]["text"]
    assert "Structured logging" in content[0]["text"]

def test_mcp_call_tool_get(tmp_path):
    import os
    db_path = os.path.join(tmp_path, "test.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    db.insert_package(
        name="fastapi",
        version="0.110.0",
        summary="FastAPI framework",
        documentation="FastAPI deep dive docs."
    )
    db.close()
    
    server = MCPServer(db_path=db_path)
    
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_package_docs",
            "arguments": {"package": "fastapi"}
        }
    }
    
    response = server.handle_message(req)
    assert response is not None
    assert response["id"] == 4
    assert "result" in response
    content = response["result"]["content"]
    assert len(content) == 1
    assert "FastAPI deep dive docs." in content[0]["text"]
