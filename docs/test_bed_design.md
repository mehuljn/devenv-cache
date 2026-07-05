# Design Specification: Performance & Accuracy Test Bed

The **Test Bed** is a benchmarking tool designed to measure and compare developer/agent efficiency when writing code **with** and **without** `DevEnv-Cache`. It provides a scientific comparison of latency, token usage, and code correctness.

---

## 📐 Test Bed Architecture

The test bed resides in a dedicated directory:
```text
/Users/mehuljani/agycli/test_bed/
├── sample_project/           # A mock project with specific package version constraints
│   ├── pyproject.toml        # Pinning specific versions (e.g. pydantic v2.6, fastapi v0.110)
│   └── poetry.lock           # Lockfile to be parsed
├── prompts.json              # Evaluated prompts (e.g. "Create FastAPI middleware with structlog")
└── run_benchmark.py          # The automated benchmark execution script
```

---

## 📊 Benchmark Metrics & Comparison

For every test prompt, the benchmark runner simulates two scenarios:

### Scenario A: Without `DevEnv-Cache`
1. The agent is given the prompt from `prompts.json`.
2. The agent is forced to either:
   * Rely entirely on its pre-trained knowledge base (high risk of version mismatch/hallucination).
   * Perform a simulated web search or documentation scrape (high latency and token cost).
3. **Recorded Metrics:** Time to generate code (seconds), total tokens consumed, and whether the code compiled/run successfully on the first try.

### Scenario B: With `DevEnv-Cache`
1. The agent is given the same prompt.
2. The agent is provided access to the `DevEnv-Cache` MCP server (or local SQLite mock query tool).
3. The agent retrieves exact package versions and Markdown-formatted documentation/API signatures.
4. **Recorded Metrics:** Time to generate code, total tokens consumed, and first-run compile/execution success rate.

---

## 🎛️ Expected Output Format

The `run_benchmark.py` script will output a comparison report to stdout and save a JSON log. Example output:

| Metric | Without DevEnv-Cache (Web / Default) | With DevEnv-Cache (Local MCP) | Delta / Improvement |
| :--- | :--- | :--- | :--- |
| **Lookup Latency** | ~3.8 seconds (Web search/scrape) | ~0.005 seconds (SQLite Query) | **99.8% Faster** |
| **Total Prompt Tokens** | ~6,500 tokens (Raw HTML scraped) | ~1,200 tokens (Pruned MD docs) | **81.5% Cheaper** |
| **First-Run Execution** | FAILED (ImportError / mixed API version) | PASSED (Correct version import) | **Fixed Hallucination** |
| **Agent Completion Time**| ~18.2 seconds | ~4.5 seconds | **75% Shorter Cycle** |

---

## 🛠️ Implementation Plan
1. **Mock Project Setup:** Set up `sample_project/` with intentionally tricky versions (e.g., Pydantic v2 which has breaking syntax changes from v1, to trigger common hallucinations).
2. **Benchmark Runner Script:** A script that mocks the agent's query process, recording timing stats.
3. **Integration with pytest:** Create integration tests that verify the benchmark output formats correctly.
