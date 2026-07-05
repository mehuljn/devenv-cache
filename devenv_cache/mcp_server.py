import json
import sys
import re
from devenv_cache.database import DatabaseManager

class MCPServer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def start(self):
        """Start the stdio JSON-RPC loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
                response = self.handle_message(message)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                # Basic error JSON-RPC framing
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

    def handle_message(self, message: dict) -> dict | None:
        msg_id = message.get("id")
        method = message.get("method")
        
        # Notifications (no response needed)
        if msg_id is None:
            return None
            
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "devenv-cache",
                        "version": "0.1.0"
                    }
                }
            }
            
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "search_dependency_docs",
                            "description": "Search local package documentation and API descriptions by keyword.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Search keyword or term (e.g. 'FastAPI middleware', 'Pydantic BaseModel')"
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "get_package_docs",
                            "description": "Retrieve full version-specific README and API documentation for a specific package.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "package": {
                                        "type": "string",
                                        "description": "The normalized name of the package (e.g., 'pydantic')"
                                    }
                                },
                                "required": ["package"]
                            }
                        }
                    ]
                }
            }
            
        elif method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            db = DatabaseManager(self.db_path)
            
            # Temporary db connections don't require external files
            if self.db_path != ":memory:":
                db.init_db()
                
            try:
                if tool_name == "search_dependency_docs":
                    query = arguments.get("query", "")
                    results = db.search_packages(query)
                    
                    if not results:
                        text_output = f"No documentation found matching: '{query}'"
                    else:
                        formatted = []
                        for r in results:
                            formatted.append(
                                f"### Package: {r['name']} (v{r['version'] or 'unknown'})\n"
                                f"**Summary:** {r['summary'] or 'N/A'}\n"
                                f"**Documentation:**\n{r['documentation'] or 'N/A'}\n"
                                f"---"
                            )
                        text_output = "\n\n".join(formatted)
                        
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": text_output
                                }
                            ],
                            "isError": False
                        }
                    }
                    
                elif tool_name == "get_package_docs":
                    package = arguments.get("package", "")
                    pkg = db.get_package(package)
                    
                    if not pkg:
                        text_output = f"No documentation found for package: '{package}'"
                        is_error = True
                    else:
                        text_output = (
                            f"# Package: {pkg['name']} (v{pkg['version'] or 'unknown'})\n"
                            f"**Summary:** {pkg['summary'] or 'N/A'}\n\n"
                            f"## Documentation:\n{pkg['documentation'] or 'N/A'}"
                        )
                        is_error = False
                        
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": text_output
                                }
                            ],
                            "isError": is_error
                        }
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {tool_name}"
                        }
                    }
            finally:
                db.close()
                
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
