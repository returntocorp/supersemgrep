from pathlib import Path
import attr


@attr.s(slots=True)
class Loader:
    def create_target(self, directory: Path) -> None:
        return
