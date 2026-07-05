# Available MCP Servers & Plugins

Here is a curated list of popular Model Context Protocol (MCP) servers and plugins that you can install in Google Antigravity.

You can configure these globally in [mcp_config.json](file:///Users/mehuljani/.gemini/config/mcp_config.json) or locally inside your workspace root in `.agents/mcp_config.json`.

---

## 1. Puppeteer (Web Browser Automation & Scrape)
Allows the agent to open a headless Chrome browser, take screenshots, navigate pages, click elements, and inspect web content.

* **Prerequisites:** Node.js installed on your system.
* **Config Template:**
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    }
  }
}
```

---

## 2. GitHub
Allows the agent to search code, view and create pull requests, read or file issues, and commit files directly to GitHub.

* **Prerequisites:** A GitHub Personal Access Token (`GH_TOKEN`).
* **Config Template:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    }
  }
}
```

---

## 3. PostgreSQL
Allows the agent to query database tables, view schemas, and inspect PostgreSQL database instances.

* **Prerequisites:** A running PostgreSQL database.
* **Config Template:**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://username:password@localhost:5432/database_name"
      ]
    }
  }
}
```

---

## 4. SQLite
Allows the agent to create, read, and write local SQLite database files.

* **Prerequisites:** Node.js installed.
* **Config Template:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "--db-path",
        "/absolute/path/to/your/database.db"
      ]
    }
  }
}
```

---

## 5. Memory / Knowledge Graph
Implements a persistent knowledge graph where the agent can store, recall, and link facts across multiple chat sessions.

* **Prerequisites:** Node.js installed.
* **Config Template:**
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  }
}
```

---

## 6. Brave Search
Allows the agent to search the web using Brave's search API.

* **Prerequisites:** A Brave Search API Key.
* **Config Template:**
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY_HERE"
      }
    }
  }
}
```

---

## How to Install/Activate
To activate any of these:
1. Select the configuration snippet above.
2. Edit your global [mcp_config.json](file:///Users/mehuljani/.gemini/config/mcp_config.json) (or local `.agents/mcp_config.json` inside your project directory).
3. Save the file and restart the agent/CLI.
