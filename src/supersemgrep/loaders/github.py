from pathlib import Path
from . import base


class Loader(base.Loader):
    NEEDS_SECRETS = {
        base.Secret(
            name="github_token",
            instructions="Create with 'repo' scope at https://github.com/settings/tokens/new.",
        )
    }

    def create_target(self, directory: Path) -> None:
        print(self.SECRETS["github_token"])
