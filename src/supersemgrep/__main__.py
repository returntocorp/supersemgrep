import sys

import click

from .main import main


def error_guard() -> None:
    try:
        main()
    except Exception as ex:
        click.secho(str(ex), fg="red", err=True)
        sys.exit(2)


if __name__ == "__main__":
    error_guard()
