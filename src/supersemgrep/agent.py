from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
from typing import Optional, Sequence, TextIO
import click
import sh

import semgrep_agent.targets


class FakeTargetFileManager(semgrep_agent.targets.TargetFileManager):
    @contextmanager
    def baseline_paths(self):
        yield []

    @contextmanager
    def current_paths(self):
        yield []

    @property
    def searched_paths(self):
        return []


setattr(semgrep_agent.targets, "TargetFileManager", FakeTargetFileManager)


import semgrep_agent.semgrep

supersemgrep_exec = sh.supersemgrep.bake(
    _ok_code={0, 1},
    _tty_out=False,
    _env={"SEMGREP_USER_AGENT_APPEND": "(Supersemgrep Agent)", **os.environ},
)


def get_findings(
    config_specifier: Sequence[str],
    committed_datetime: Optional[datetime],
    base_commit_ref: Optional[str],
    head_ref: Optional[str],
    semgrep_ignore: TextIO,
    rewrite_rule_ids: bool,
    enable_metrics: bool,
    *,
    timeout: Optional[int],
):
    config_args = []
    local_configs = set()  # Keep track of which config specifiers are local files/dirs
    for conf in config_specifier:
        if Path(conf).exists():
            local_configs.add(conf)
        config_args.extend(["--config", conf])
    rewrite_args = [] if rewrite_rule_ids else ["--no-rewrite-rule-ids"]
    metrics_args = ["--enable-metrics"] if enable_metrics else []
    findings = semgrep_agent.semgrep.FindingSets(searched_paths=set())

    args = [
        "--json",
        *metrics_args,
        *rewrite_args,
        *config_args,
    ]
    semgrep_results = semgrep_agent.semgrep.invoke_semgrep(args, [], timeout=timeout)[
        "results"
    ]
    click.echo(semgrep_agent.semgrep.invoke_semgrep(["--help"], [], timeout=timeout))

    findings.current.update_findings(
        semgrep_agent.semgrep.Finding.from_semgrep_result(result, committed_datetime)
        for result in semgrep_results
        if not result["extra"].get("is_ignored")
    )
    findings.ignored.update_findings(
        semgrep_agent.semgrep.Finding.from_semgrep_result(result, committed_datetime)
        for result in semgrep_results
        if result["extra"].get("is_ignored")
    )
    return findings


setattr(semgrep_agent.semgrep, "semgrep_exec", supersemgrep_exec)
setattr(semgrep_agent.semgrep, "get_findings", get_findings)

from semgrep_agent.__main__ import error_guard
