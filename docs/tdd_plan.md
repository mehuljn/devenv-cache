# TDD Development Plan: DevEnv-Cache

This document tracks the tasks, milestones, and testing strategies for building **DevEnv-Cache** in Python using Test-Driven Development (TDD).

---

## 📋 Task List & Status

*   [x] **Phase 1: Project Initialization & Test Setup**
    *   [x] Create project directory structure.
    *   [x] Set up python package configuration (`pyproject.toml`).
    *   [x] Configure `pytest` and verify the test runner executes.
*   [x] **Phase 2: Lockfile Parser (TDD)**
    *   [x] Write unit tests for parsing `poetry.lock`.
    *   [x] Implement `poetry.lock` parser to pass tests.
    *   [x] Write unit tests for parsing `requirements.txt`.
    *   [x] Implement `requirements.txt` parser to pass tests.
*   [x] **Phase 3: SQLite Storage Engine (TDD)**
    *   [x] Write unit tests for DB schema initialization, inserting package metadata, and search queries.
    *   [x] Implement SQLite storage manager using FTS5 (Full-Text Search).
*   [x] **Phase 4: Docs Syncing & Sourcing (TDD)**
    *   [x] Write unit tests for PyPI API client (mocked requests).
    *   [x] Implement PyPI metadata client to fetch READMEs/documentation.
*   [x] **Phase 5: CLI Engine (TDD)**
    *   [x] Write integration/unit tests for CLI commands (`init`, `sync`).
    *   [x] Implement CLI command handling via `argparse`.
*   [x] **Phase 6: MCP Server Integration (TDD)**
    *   [x] Write unit/integration tests for Model Context Protocol command handler and tools.
    *   [x] Implement MCP server handlers using `mcp` SDK or basic standard I/O framing.
*   [x] **Phase 7: Test Bed & Benchmarking (TDD)**
    *   [x] Create mock project structure (`test_bed/sample_project`).
    *   [x] Write unit tests for the benchmark runner (`run_benchmark.py`).
    *   [x] Implement the benchmark script to record latency, token counts, and compilation accuracy.

---

## 📐 Directory Structure

```text
/Users/mehuljani/agycli/devenv-cache/
├── pyproject.toml         # Python packaging config
├── README.md              # Project usage documentation
├── devenv_cache/          # Source directory
│   ├── __init__.py
│   ├── cli.py             # CLI command processing
│   ├── parser.py          # Lockfile & dependency parser
│   ├── cacher.py          # PyPI client and docs puller
│   ├── database.py        # SQLite storage layer
│   └── mcp_server.py      # MCP tool server interface
├── test_bed/              # Performance & Accuracy Test Bed
│   ├── sample_project/    # Tricky target dependencies
│   ├── prompts.json       # Coding task scenarios
│   └── run_benchmark.py   # Benchmark runner
└── tests/                 # Test directory
    ├── __init__.py
    ├── test_parser.py
    ├── test_database.py
    ├── test_cacher.py
    ├── test_cli.py
    ├── test_mcp_server.py
    └── test_benchmark.py  # Test bed runner verification
```

---

## 🧪 TDD Strategy per Phase

1. **Write the Tests:** Create a test file in `tests/` asserting the expected outputs or behavior for a specific module (e.g. parsing `poetry.lock`).
2. **Fail:** Run `pytest` to verify the tests fail due to missing implementation or assertion errors.
3. **Implement Minimum Code:** Write only the code required to make the tests pass in `devenv_cache/`.
4. **Pass:** Re-run `pytest` and verify the test passes.
5. **Refactor:** Clean up code organization, docstrings, and typing without breaking tests.
