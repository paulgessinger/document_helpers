#! /usr/bin/env python3

from __future__ import print_function
import argparse
import glob
import os
from datetime import date
import shutil
import sys
import subprocess

import logging

import click

from .log import get_logger
from .filename import parse_filename, format_filename
from .tags import get_tags, set_tags


def quote(s):
    if sys.version_info < (3, 3):
        import pipes

        return pipes.quote(s)
    else:
        import shlex

        return shlex.quote(s)


level = logging.DEBUG
logger = get_logger("sort", level)


def move(f, basedir, dr=False):
    if not os.path.exists(f):
        logger.error("%s not found", f)
        return

    logger.info(f)

    name_info = parse_filename(os.path.basename(f))

    if name_info.dt is not None:
        month = name_info.dt.month
        year = name_info.dt.year
    else:
        mtime = date.fromtimestamp(os.path.getmtime(f))
        month = mtime.month
        year = mtime.year
        name_info.dt = mtime

    root, ext = os.path.splitext(os.path.basename(f))

    destdir = os.path.join(basedir, str(year), "{:02d}".format(month))
    if not dr:
        os.system('mkdir -p "{}"'.format(destdir))

    # fname = "{}-{}".format(mtime.strftime("%Y-%m-%d"), root)
    # dest = os.path.join(destdir, fname + ext)
    tags = get_tags(f) | name_info.tags
    dest = os.path.join(
        destdir, format_filename(name_info.name, name_info.dt, tags=tags)
    )

    logger.info("=> %s", dest)
    logger.debug("Setting finder tags to: %s", ", ".join(tags))
    if not dr:
        cmd = "mv {} {}".format(quote(f), quote(dest))
        os.system(cmd)
        set_tags(dest, tags)


@click.command("sort_docs")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--outputdir",
    envvar="DOCUMENT_HELPERS_SORT_OUTPUT_DIR",
    required=True,
    type=click.Path(exists=True, writable=True, file_okay=False, dir_okay=True),
)
@click.option("--dry-run", "-s", is_flag=True)
def main(files, outputdir, dry_run):
    try:
        if len(files) == 0:
            print("No files given, do nothing")
        if len(files) == 1 and files[0] == "-":
            # read from stdin
            files = sys.stdin.read().strip().split("\n")

        logger.debug("Destination: %s", outputdir)
        for f in files:
            move(f, outputdir, dr=dry_run)

    except Exception as e:
        print("blub")
        logger.error("Caught exception: %s" % str(e), exc_info=True)


if __name__ == "__main__":
    main()
