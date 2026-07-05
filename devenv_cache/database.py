import sqlite3
import os
import re

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        # Ensure parent directories exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def init_db(self):
        cursor = self.conn.cursor()
        
        # Core metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                version TEXT,
                summary TEXT,
                documentation TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # FTS5 search index table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts USING fts5(
                name,
                summary,
                documentation
            )
        """)
        self.conn.commit()

    def insert_package(self, name: str, version: str, summary: str, documentation: str):
        normalized_name = re.sub(r"[-_.]+", "-", name).strip().lower()
        cursor = self.conn.cursor()
        
        # Insert or replace in metadata table
        cursor.execute("""
            INSERT OR REPLACE INTO packages (name, version, summary, documentation, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (normalized_name, version, summary, documentation))
        
        # Clean up existing search index for this package name to prevent duplicates
        cursor.execute("DELETE FROM packages_fts WHERE name = ?", (normalized_name,))
        
        # Insert into search index
        cursor.execute("""
            INSERT INTO packages_fts (name, summary, documentation)
            VALUES (?, ?, ?)
        """, (normalized_name, summary, documentation))
        
        self.conn.commit()

    def get_package(self, name: str) -> dict | None:
        normalized_name = re.sub(r"[-_.]+", "-", name).strip().lower()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, version, summary, documentation, updated_at 
            FROM packages 
            WHERE name = ?
        """, (normalized_name,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def search_packages(self, query: str, limit: int = 5) -> list[dict]:
        if not query.strip():
            return []
            
        cursor = self.conn.cursor()
        # Clean the query slightly for FTS5 (avoid syntax errors with simple inputs)
        sanitized_query = re.sub(r'[^\w\s*]', ' ', query).strip()
        if not sanitized_query:
            return []
            
        try:
            cursor.execute("""
                SELECT p.name, p.version, p.summary, p.documentation
                FROM packages p
                JOIN packages_fts f ON p.name = f.name
                WHERE packages_fts MATCH ?
                LIMIT ?
            """, (sanitized_query, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.OperationalError:
            # Fallback to simple LIKE search if FTS5 syntax fails
            like_query = f"%{query}%"
            cursor.execute("""
                SELECT name, version, summary, documentation
                FROM packages
                WHERE name LIKE ? OR summary LIKE ? OR documentation LIKE ?
                LIMIT ?
            """, (like_query, like_query, like_query, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
