import json
from pathlib import Path
from typing import Collection, Dict, Optional

import attr
import click

SECRET_STORE_PATH = Path.home() / ".local" / "supersemgrep" / "secrets.json"


class SecretStore(Dict[str, str]):
    PATH = SECRET_STORE_PATH

    def __init__(self):
        self.PATH.parent.mkdir(parents=True, exist_ok=True)
        if self.PATH.exists():
            self.update(json.loads(self.PATH.read_text()), skip_save=True)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.PATH.write_text(json.dumps(self, indent=2))

    def __delitem__(self, key):
        super().__delitem__(key)
        self.PATH.write_text(json.dumps(self, indent=2))

    def update(self, other, skip_save=False):
        super().update(other)
        if skip_save:
            return
        self.PATH.write_text(json.dumps(self, indent=2))


SECRETS = SecretStore()


@attr.s(frozen=True)
class Secret:
    name: str = attr.ib()
    instructions: str = attr.ib()

    def ensure_value(self):
        if SECRETS.get(self.name) is None:
            SECRETS[self.name] = self.prompt_for_value()

    def prompt_for_value(self):
        return click.prompt(
            click.style(f"Supersemgrep needs a value for {self.name}", bold=True)
            + "\n\n"
            + click.style(f"Instructions", bold=True)
            + ": "
            + click.style(self.instructions)
            + " "
            + click.style(f"The value you enter will be saved to {SECRET_STORE_PATH}.")
            + "\n\ntype here",
            type=click.STRING,
        )


class Loader:

    NEEDS_SECRETS: Collection[Secret] = set()
    SECRETS = SECRETS

    def ensure_secrets(self):
        for secret in self.NEEDS_SECRETS:
            secret.ensure_value()

    def run(self, directory: Path) -> None:
        self.ensure_secrets()
        self.create_target(directory)

    def create_target(self, directory: Path) -> None:
        raise NotImplementedError()
