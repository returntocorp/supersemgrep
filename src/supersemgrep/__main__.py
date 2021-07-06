import sys
import traceback

import click

from .main import main


def error_guard() -> None:
    try:
        main()
    except Exception as ex:
        click.secho(
            f"Supersemgrep error:\n\n{traceback.format_exc()}", fg="red", err=True
        )
        sys.exit(2)


if __name__ == "__main__":
    error_guard()
