import re
import tomllib

def normalize_package_name(name: str) -> str:
    """Normalize a package name to PEP 503 format."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()

def parse_requirements_txt(content: str) -> dict[str, str]:
    """Parse requirements.txt contents into a mapping of normalized package name -> version."""
    dependencies = {}
    for line in content.splitlines():
        line = line.strip()
        # Ignore comments and empty lines
        if not line or line.startswith("#"):
            continue
        
        # Split by typical specifiers: == or >= or <= or > or < or ~=
        match = re.split(r"(==|>=|<=|>|<|~=)", line)
        if len(match) >= 3:
            name = normalize_package_name(match[0])
            version = match[2].split(";")[0].strip() # Strip environment markers if any
            dependencies[name] = version
        else:
            name = normalize_package_name(line)
            dependencies[name] = ""
            
    return dependencies

def parse_poetry_lock(content: str) -> dict[str, str]:
    """Parse poetry.lock contents into a mapping of normalized package name -> version."""
    data = tomllib.loads(content)
    dependencies = {}
    for package in data.get("package", []):
        name = package.get("name")
        version = package.get("version")
        if name and version:
            dependencies[normalize_package_name(name)] = version.strip()
    return dependencies
