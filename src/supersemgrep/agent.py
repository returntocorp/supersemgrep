from contextlib import contextmanager
import os
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

setattr(semgrep_agent.semgrep, "semgrep_exec", supersemgrep_exec)
setattr(semgrep_agent.semgrep, "chunked_iter", lambda *x, **y: [[]])

from semgrep_agent.__main__ import error_guard
