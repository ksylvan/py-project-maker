"""Main module for the pyhatchery package."""

import click

from pyhatchery import __version__


def main():
    """Main function to execute the script."""
    styled_version = click.style(__version__, fg="green", bold=True)
    click.echo(f"Hello from pyhatchery! Version {styled_version}.")


if __name__ == "__main__":
    main()
