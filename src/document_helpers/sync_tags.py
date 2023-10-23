#! /usr/bin/env python3

import argparse
import logging
import os
import sys
from datetime import datetime

import click

from .log import get_logger
from .tags import get_tags, set_tags
from .filename import parse_filename, format_filename


logger = get_logger("sync_tags", level=logging.DEBUG)


def sync(file, dr, tags_exe):
    logger.info(file)
    finder_tags = get_tags(file, tags_exe=tags_exe)
    logger.debug("Finder tags: %s", ", ".join(finder_tags))
    name_info = parse_filename(os.path.basename(file))
    logger.debug(name_info)
    logger.debug("Filename tags: %s", ", ".join(name_info.tags))
    name_tags = name_info.tags

    total_tags = name_tags | finder_tags
    logger.debug("Combined tags: %s", ", ".join(total_tags))

    if name_info.dt is None:
        name_info.dt = datetime.fromtimestamp(os.path.getmtime(file))

    new_filename = format_filename(name_info.name, name_info.dt, sorted(total_tags))
    logger.debug("New filename: %s", new_filename)

    if not dr:
        dest = os.path.join(os.path.dirname(file), new_filename)
        logger.info("%s => %s", file, dest)
        os.rename(file, dest)

        set_tags(dest, total_tags, tags_exe=tags_exe)


@click.command("sync_tags")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
)
@click.option("--tags", type=click.Path(exists=True, dir_okay=False, executable=True))
@click.option("--dry-run", "-s", is_flag=True)
def main(files, dry_run, tags):
    logger.debug(files)
    try:
        if len(files) == 0:
            print("No files given, do nothing.")

        if len(files) == 1 and files[0] == "-":
            # read from stdin
            files = sys.stdin.read().strip().split("\n")


        logger.debug(files)
        for file in files:
            assert os.path.exists(file), "File %s does not exist" % file
            sync(file, dry_run, tags)
    except:
        logger.error("Exception occurred", exc_info=True)


if "__main__" == __name__:
    main()
