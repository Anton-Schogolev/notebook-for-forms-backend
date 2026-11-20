import subprocess


def test() -> int:
    return subprocess.call(["bash", "scripts/test", "-q"])


def dev() -> int:
    return subprocess.call(["uv", "run", "fastapi", "dev"])
