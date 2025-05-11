"""Main module for the pyhatchery package."""

import click

from pyhatchery import __version__


def main():
    """Main function to execute the script."""
    click.echo(f"Hello from pyhatchery! Version {click.style(__version__, fg='green', bold=True)}.")


if __name__ == "__main__":
    main()
