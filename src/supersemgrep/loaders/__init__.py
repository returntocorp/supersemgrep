from typing import Dict
from .base import Loader
from . import github_repos

LOADERS: Dict[str, Loader] = {"github_repos": github_repos.Loader()}
