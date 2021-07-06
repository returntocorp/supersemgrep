from pathlib import Path
import tempfile

from contextlib import contextmanager
from typing import Iterator, List, Optional

from semgrep.config_resolver import Config as SemgrepConfig
from semgrep.rule import Rule

from .loaders import LOADERS
from .loaders.base import Loader


def get_loader_of_rule(rule: Rule) -> Optional[Loader]:
    loader_key = rule.metadata.get("supersemgrep.loader")
    if not isinstance(loader_key, str):
        return None
    return LOADERS.get(loader_key)


def yield_loaders(config_args: List[str], rewrite_rule_ids: bool) -> Iterator[Loader]:
    config, _ = SemgrepConfig.from_config_list(config_args)
    loaders = set()
    for rule in config.get_rules(no_rewrite_rule_ids=not rewrite_rule_ids):
        loader = get_loader_of_rule(rule)
        if loader is None:
            continue
        loaders.add(loader)
    yield from loaders


@contextmanager
def make_target(config_args: List[str], rewrite_rule_ids: bool) -> Iterator[Path]:
    """
    Create a target file from a Semgrep config.
    """
    with tempfile.TemporaryDirectory() as path_string:
        path = Path(path_string)
        for loader in yield_loaders(config_args, rewrite_rule_ids):
            loader.run(path)
        yield path
