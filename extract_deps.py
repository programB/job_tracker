import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    sys.exit(
        (
            "You need tomllib to use this script. "
            "It's a std library module as of Python 3.11"
        )
    )

if len(sys.argv) != 2:
    sys.exit("Usage: extract_deps.py path_to_pyproject.toml")

pyproject_f = Path(sys.argv[1]).resolve()

if not (pyproject_f.is_file() and pyproject_f.name == "pyproject.toml"):
    sys.exit(f"pyproject.toml not found in {pyproject_f.parent}")

working_dir = pyproject_f.parent

with pyproject_f.open("rb") as f:
    print(f"Parsing pyproject.toml (in {working_dir})")
    data = tomllib.load(f)

if "project" not in data:
    raise ValueError("No project's metadata in pyproject.toml !")
# if "dependencies" in data["project"].get("dynamic", []):
#     raise ValueError("Dependencies cannot be dynamic")


def write_req_file(section_name: str, packages: list):
    base_n = f"requirements-{section_name}" if section_name else "requirements"
    req_file = working_dir.joinpath(base_n + ".txt")
    with req_file.open("w", encoding="UTF-8") as rf:
        print(f"{req_file.name} (in {working_dir})")
        for package in packages:
            rf.write(package + "\n")


# deps = data["project"].get("dependencies")
opt_deps = data["project"].get("optional-dependencies")

# if deps:
#     print("Writing normal dependencies: ", end="")
#     write_req_file("", deps)

if opt_deps:
    for opt_dep_group, opt_list in opt_deps.items():
        print(rf"Writing optional '{opt_dep_group}' dependencies: ", end="")
        write_req_file(f"{opt_dep_group}", opt_list)
