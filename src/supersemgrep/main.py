from typing import List, NoReturn
import click
from . import scans, targets


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--config", "-c", multiple=True, hidden=True)
@click.argument("semgrep_args", nargs=-1, type=click.UNPROCESSED)
def main(config: List[str], semgrep_args: List[str]) -> NoReturn:
    """
    A command line interface for the supersemgrep package.
    """
    with targets.make_target(config) as target_path:
        scans.scan(target_path, semgrep_args)
