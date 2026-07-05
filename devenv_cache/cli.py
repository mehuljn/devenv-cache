import argparse
import sys
import os
from devenv_cache.database import DatabaseManager
from devenv_cache.parser import parse_poetry_lock, parse_requirements_txt
from devenv_cache.cacher import PyPIClient

def main(args=None):
    parser = argparse.ArgumentParser(description="DevEnv-Cache CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    init_parser = subparsers.add_parser("init", help="Initialize database")
    sync_parser = subparsers.add_parser("sync", help="Sync project dependencies to local cache")
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP stdio server")
    
    parsed_args = parser.parse_args(args)
    
    db_dir = ".devenv-cache"
    db_path = os.path.join(db_dir, "docs.sqlite")
    
    if parsed_args.command == "init":
        os.makedirs(db_dir, exist_ok=True)
        db = DatabaseManager(db_path)
        db.init_db()
        db.close()
        print(f"Initialized empty DevEnv-Cache database at {db_path}")
        sys.exit(0)
        
    elif parsed_args.command == "sync":
        if not os.path.exists(db_path):
            print(f"Error: Database not found at {db_path}. Run 'devenv-cache init' first.", file=sys.stderr)
            sys.exit(1)
            
        dependencies = {}
        # Parse poetry.lock if it exists
        if os.path.exists("poetry.lock"):
            print("Found poetry.lock, parsing...")
            with open("poetry.lock", "r", encoding="utf-8") as f:
                dependencies.update(parse_poetry_lock(f.read()))
        # Otherwise parse requirements.txt if it exists
        elif os.path.exists("requirements.txt"):
            print("Found requirements.txt, parsing...")
            with open("requirements.txt", "r", encoding="utf-8") as f:
                dependencies.update(parse_requirements_txt(f.read()))
        else:
            print("Error: No poetry.lock or requirements.txt found in current directory.", file=sys.stderr)
            sys.exit(1)
            
        if not dependencies:
            print("No dependencies found to sync.")
            sys.exit(0)
            
        print(f"Syncing {len(dependencies)} dependencies...")
        db = DatabaseManager(db_path)
        client = PyPIClient()
        
        for pkg, ver in dependencies.items():
            print(f"Fetching docs for {pkg} ({ver or 'latest'})...")
            meta = client.fetch_metadata(pkg, ver)
            db.insert_package(pkg, ver, meta["summary"], meta["description"])
            
        db.close()
        print(f"Successfully synced {len(dependencies)} dependencies into {db_path}")
        sys.exit(0)
        
    elif parsed_args.command == "mcp":
        from devenv_cache.mcp_server import MCPServer
        server = MCPServer(db_path)
        server.start()
        sys.exit(0)

if __name__ == "__main__":
    main()
