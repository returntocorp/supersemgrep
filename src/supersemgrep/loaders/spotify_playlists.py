import json
from pathlib import Path
from . import base


class Loader(base.Loader):
    NEEDS = {
        base.Option(
            name="spotify_client_id",
            instructions="Create an app https://developer.spotify.com/dashboard/applications.",
            persist=True,
        ),
        base.Option(
            name="spotify_client_secret",
            instructions="Create an app https://developer.spotify.com/dashboard/applications.",
            persist=True,
        ),
        base.Option(
            name="spotify_playlist_id",
            instructions="Enter a Spotify playlist ID.",
        ),
    }

    def create_target(self, directory: Path) -> None:
        session = base.CachedRequestsSession()

        r = session.post(
            "https://accounts.spotify.com/api/token",
            auth=(
                self.options["spotify_client_id"],
                self.options["spotify_client_secret"],
            ),
            data={"grant_type": "client_credentials"},
        )
        r.raise_for_status()
        access_token = r.json()["access_token"]
        session.headers["Authorization"] = f"Bearer {access_token}"

        r = session.get(
            f"https://api.spotify.com/v1/playlists/{self.options['spotify_playlist_id']}"
        )
        r.raise_for_status()
        playlist = r.json()
        track_ids = [track["track"]["id"] for track in playlist["tracks"]["items"]]

        r = session.get(
            "https://api.spotify.com/v1/audio-features",
            params={"ids": ",".join(track_ids)},
        )
        r.raise_for_status()

        playlist["tracks"]["items"] = [
            {**track, "analysis": analysis}
            for track, analysis in zip(
                playlist["tracks"]["items"], r.json()["audio_features"]
            )
        ]
        json_path = directory / f"{self.options['spotify_playlist_id']}-playlist.json"
        json_path.write_text(json.dumps(playlist, indent=2))
