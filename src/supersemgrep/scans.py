from pathlib import Path
import subprocess
import sys
from typing import List, NoReturn


def yield_config_args(configs: List[str]):
    for config in configs:
        yield "--config"
        yield config


def yield_rewrite_args(rewrite_rule_ids: bool):
    if not rewrite_rule_ids:
        yield "--no-rewrite-rule-ids"


def scan(
    target_path: Path, configs: List[str], rewrite_rule_ids: bool, extra_args: List[str]
) -> NoReturn:
    result = subprocess.run(
        [
            "semgrep",
            *yield_config_args(configs),
            *yield_rewrite_args(rewrite_rule_ids),
            *extra_args,
            target_path,
        ],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    sys.exit(result.returncode)
