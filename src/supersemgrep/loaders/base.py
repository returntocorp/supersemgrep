from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Collection, Dict, Optional

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


@dataclass(frozen=True)
class Option:
    name: str
    instructions: str
    persist: bool = False

    @property
    def envvar(self):
        return f"SUPERSEMGREP_OPTION__{self.name}"

    @property
    def env_value(self):
        return os.getenv(self.envvar)

    @property
    def secrets_file_value(self):
        return SECRETS.get(self.name)

    @property
    def value(self):
        return self.env_value or self.secrets_file_value or self.prompt_for_value()

    def prompt_for_value(self):
        result = click.prompt(
            click.style(f"Supersemgrep needs a value for {self.name}", bold=True)
            + "\n\n"
            + click.style(f"Instructions", bold=True)
            + ": "
            + click.style(self.instructions)
            + (
                f" The value you enter will be saved to {SECRET_STORE_PATH}."
                if self.persist
                else ""
            )
            + f"\n\n{self.name}",
            type=click.STRING,
        )
        if self.persist:
            SECRETS[self.name] = result
        return result


class Loader:

    NEEDS: Collection[Option] = set()

    def __init__(self) -> None:
        self.options: Dict[str, str] = {}

    def ensure_options(self):
        for option in self.NEEDS:
            self.options[option.name] = option.value

    def run(self, directory: Path) -> None:
        self.ensure_options()
        self.create_target(directory)

    def create_target(self, directory: Path) -> None:
        raise NotImplementedError()
