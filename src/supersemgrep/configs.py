from pathlib import Path
import tempfile

from contextlib import contextmanager
from typing import Any, Dict, List, Tuple

from semgrep.config_resolver import Config as SemgrepConfig
from semgrep.rule import Rule
from semgrep.rule_yaml import YamlTree



@contextmanager
def make_config(config_args: List[str]) -> Path:
    """
    Change supersemgrep config to a semgrep-compatible config.
    """
    SemgrepConfig(config_args)
    with tempfile.TemporaryDirectory() as path:
        yield path
