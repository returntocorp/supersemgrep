from typing import Dict
from .base import Loader
from . import github_repos
from . import images
from . import spotify_playlists

LOADERS: Dict[str, Loader] = {
    "images": images.Loader(),
    "github_repos": github_repos.Loader(),
    "spotify_playlists": spotify_playlists.Loader(),
}
