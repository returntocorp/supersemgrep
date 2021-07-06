from typing import Dict
from .base import Loader
from . import github

LOADERS: Dict[str, Loader] = {"github": github.Loader()}
