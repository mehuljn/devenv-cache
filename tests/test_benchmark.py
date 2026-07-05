import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock
from devenv_cache.database import DatabaseManager

def test_benchmark_runner_generates_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Create test_bed directories
    os.makedirs("test_bed/sample_project", exist_ok=True)
    
    # Write sample prompts.json
    prompts_content = """
    [
        {
            "id": "test_fastapi",
            "prompt": "Write a fastapi middleware with structlog",
            "query": "fastapi middleware structlog"
        }
    ]
    """
    with open("test_bed/prompts.json", "w") as f:
        f.write(prompts_content)
        
    # Set up mock DB inside the test bed environment
    db_path = os.path.join(tmp_path, ".devenv-cache", "docs.sqlite")
    db = DatabaseManager(db_path)
    db.init_db()
    db.insert_package(
        name="fastapi",
        version="0.110.0",
        summary="A fast web framework",
        documentation="FastAPI is a modern, fast (high-performance)..."
    )
    db.insert_package(
        name="structlog",
        version="24.1.0",
        summary="Structured logging",
        documentation="Structured logging details."
    )
    db.close()
    
    # Let's import the runner code and run it directly, or run it as a subprocess
    # Since we are writing the run_benchmark.py script, let's copy the code and test it
    # We will write the script and run it, asserting it outputs 'benchmark_report.md'
    from test_bed.run_benchmark import run_benchmark
    
    report_path = os.path.join(tmp_path, "benchmark_report.md")
    run_benchmark(db_path=db_path, report_path=report_path)
    
    assert os.path.exists(report_path)
    with open(report_path, "r") as f:
        content = f.read()
    
    assert "Benchmark Report" in content
    assert "Without DevEnv-Cache" in content
    assert "With DevEnv-Cache" in content
    assert "Latency" in content
    assert "Tokens" in content
