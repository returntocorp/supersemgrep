from pathlib import Path
import subprocess
import sys
from typing import NoReturn


def scan(target_path: Path, extra_args) -> NoReturn:
    result = subprocess.run(
        ["semgrep", *extra_args, target_path],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    sys.exit(result.returncode)
