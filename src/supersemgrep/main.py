from typing import List, NoReturn
import click
from . import scans, targets


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("--config", "-c", multiple=True, hidden=True)
@click.option("--rewrite-rule-ids", type=click.BOOL, hidden=True)
@click.argument("semgrep_args", nargs=-1, type=click.UNPROCESSED)
def main(
    config: List[str], rewrite_rule_ids: bool, semgrep_args: List[str]
) -> NoReturn:  # mypy: ignore (https://github.com/python/mypy/issues/8401)
    """
    A command line interface for the supersemgrep package.
    """
    with targets.make_target(config, rewrite_rule_ids) as target_path:
        scans.scan(target_path, config, rewrite_rule_ids, semgrep_args)
