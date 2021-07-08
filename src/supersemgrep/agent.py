from contextlib import contextmanager
from datetime import datetime
import json
import os
import tempfile
from typing import Any, Dict, List, Optional
import sh

import semgrep_agent.semgrep

supersemgrep_exec = sh.supersemgrep.bake(
    _ok_code={0, 1},
    _tty_out=False,
    _env={"SEMGREP_USER_AGENT_APPEND": "(Supersemgrep Agent)", **os.environ},
)


def invoke_supersemgrep(
    semgrep_args: List[str], _: List[str], *, timeout: Optional[int]
) -> Dict[str, List[Any]]:
    output: Dict[str, List[Any]] = {"results": [], "errors": []}

    with tempfile.NamedTemporaryFile("w") as output_json_file:
        args = semgrep_args.copy()
        if semgrep_agent.semgrep.is_debug():
            args.extend(["--debug"])
        args.extend(
            [
                "-o",
                output_json_file.name,  # nosem: python.lang.correctness.tempfile.flush.tempfile-without-flush
            ]
        )

        _ = supersemgrep_exec(
            *args, _timeout=timeout, _err=semgrep_agent.semgrep.debug_echo
        )

        with open(
            output_json_file.name  # nosem: python.lang.correctness.tempfile.flush.tempfile-without-flush
        ) as f:
            parsed_output = json.load(f)

        output["results"].extend(parsed_output["results"])
        output["errors"].extend(parsed_output["errors"])

    return output


setattr(semgrep_agent.semgrep, "invoke_semgrep", invoke_supersemgrep)

from semgrep_agent.__main__ import error_guard
