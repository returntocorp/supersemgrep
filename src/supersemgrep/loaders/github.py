import json
import requests

from pathlib import Path
from . import base


class Loader(base.Loader):
    NEEDS = {
        base.Option(
            name="github_token",
            instructions="Create a personal access token with 'repo' scope at https://github.com/settings/tokens/new.",
            persist=True,
        ),
        base.Option(
            name="github_namespace",
            instructions="Enter a GitHub user or organization.",
        ),
    }

    def create_target(self, directory: Path) -> None:
        repos = []

        url = f"https://api.github.com/orgs/{self.options['github_namespace']}/repos"
        while url:
            response = requests.get(
                url,
                headers={"Authorization": f"token {self.options['github_token']}"},
                timeout=10,
            )
            response.raise_for_status()
            repos.extend(response.json())
            url = response.links["next"]["url"] if "next" in response.links else None

        json_path = directory / f"{self.options['github_namespace']}-repos.json"
        json_path.write_text(json.dumps(repos, indent=2))
