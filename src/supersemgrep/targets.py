from pathlib import Path
import tempfile

from contextlib import contextmanager
from typing import Iterator, List

from semgrep.config_resolver import Config as SemgrepConfig

from .loaders.base import Loader


def get_loader_of_rule(rule):
    return None


def yield_loaders(config_args: List[str]) -> Iterator[Loader]:
    rules = SemgrepConfig.from_config_list(config_args)
    loaders = set()
    for rule in rules:
        loader = get_loader_of_rule(rule)
        if loader is None:
            continue
        loaders.add(loader)
    yield from loaders


@contextmanager
def make_target(config_args: List[str]) -> Iterator[Path]:
    """
    Create a target file from a Semgrep config.
    """
    with tempfile.TemporaryDirectory() as path_string:
        path = Path(path_string)
        for loader in yield_loaders(config_args):
            loader.create_target(path)
        yield path
