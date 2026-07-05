import pytest
from devenv_cache.parser import parse_requirements_txt, parse_poetry_lock

def test_parse_requirements_txt():
    content = """
    fastapi==0.110.0
    pydantic>=2.6.4
    # This is a comment
    structlog==24.1.0
    requests
    """
    dependencies = parse_requirements_txt(content)
    assert dependencies["fastapi"] == "0.110.0"
    assert dependencies["pydantic"] == "2.6.4"
    assert dependencies["structlog"] == "24.1.0"
    assert dependencies["requests"] == ""

def test_parse_poetry_lock():
    content = """
    [[package]]
    name = "fastapi"
    version = "0.110.0"
    description = "FastAPI framework"
    category = "main"

    [[package]]
    name = "pydantic"
    version = "2.6.4"
    category = "main"
    """
    dependencies = parse_poetry_lock(content)
    assert dependencies["fastapi"] == "0.110.0"
    assert dependencies["pydantic"] == "2.6.4"
