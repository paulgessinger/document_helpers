#! /usr/bin/env python3

from __future__ import print_function
import argparse
import glob
import os
from datetime import date, datetime
from pathlib import Path
import requests
import shutil
import sys
import subprocess

import logging

import click

from .log import get_logger
from .filename import dataclass, parse_filename, format_filename
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


#  def ensure_tag(tag, url, token):
#  existing = {}

#  page = 1
#  next_url = f"{url}/api/tags/?page_size=100000"

#  while True:

#  r = requests.get(next_url,
#  headers={"Authorization": f"Token {token}"},
#  )

#  r.raise_for_status()

#  data = r.json()

#  for result in data["results"]:
#  existing[result["name"]] = result["id"]

#  if data["next"] is None:
#  break
#  next_url = data["next"]

#  if tag in existing:
#  return existing[tag] # id

#  print("posting tag:", tag)
#  r = requests.post(next_url,
#  headers={"Authorization": f"Token {token}"},
#  data={"name": tag},
#  )

#  r.raise_for_status()
#  data = r.json()
#  return data["id"]


def create_tag(url, token, tag):
    r = requests.post(
        f"{url}/api/tags/",
        headers={"Authorization": f"Token {token}"},
        data={"name": tag},
    )

    r.raise_for_status()
    data = r.json()
    return data["id"]


def create_correspondent(url, token, correspondent):
    print("posting correspondent:", correspondent)
    r = requests.post(
        f"{url}/api/correspondents/",
        headers={"Authorization": f"Token {token}"},
        data={
            "name": correspondent,
            "match": "",
            "matching_algorithm": 6,
            "is_sensitive": False,
        },
    )

    try:
        r.raise_for_status()
    except:
        print(r.text)
        raise
    data = r.json()
    return data["id"]


def get_all_tags(url, token):
    url = f"{url}/api/tags/?page_size=100000"

    r = requests.get(
        url,
        headers={"Authorization": f"Token {token}"},
    )

    r.raise_for_status()

    data = r.json()

    return {c["name"]: c["id"] for c in data["results"]}


def get_correspondents(url, token):
    url = f"{url}/api/correspondents/?page_size=100000"

    r = requests.get(
        url,
        headers={"Authorization": f"Token {token}"},
    )

    r.raise_for_status()

    data = r.json()

    return {c["name"]: c["id"] for c in data["results"]}


def create_document_type(url, token, name):
    r = requests.post(
        f"{url}/api/document_types/",
        headers={"Authorization": f"Token {token}"},
        data={"name": name},
    )

    r.raise_for_status()
    data = r.json()
    return data["id"]


def get_document_types(url, token):
    url = f"{url}/api/document_types/?page_size=100000"

    r = requests.get(
        url,
        headers={"Authorization": f"Token {token}"},
    )

    r.raise_for_status()

    data = r.json()

    return {c["name"]: c["id"] for c in data["results"]}


@click.command("ingest")
@click.argument(
    "source",
    nargs=1,
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=True),
)
@click.option("--url", required=True)
@click.option("--token", required=True)
@click.option("--dry-run", "-s", is_flag=True)
@click.option("--failed", type=Path)
def main(source, dry_run, url, token, failed):
    if failed is not None:
        failed = failed.resolve()

    tags_seen = set()
    tag_filterlist = set(
        [
            "Red",
            "A",
            "m",
            "16-34-13",
            "241B4924-D924-4FAF-8A5A-033910B7D5FD",
            "2020-12-28",
            "1",
            "2019",
            "v03",
            "ESt",
        ]
    )

    tag_map = {
        "gewerbe": "Gewerbe",
        "cern": "CERN",
        "DOCT JGU": "DOCT",
        "JGU DOCT": "DOCT",
        "hetzner": "Hetzner",
    }

    correspondents = get_correspondents(url, token)
    document_types = get_document_types(url, token)
    tags_to_ids = get_all_tags(url, token)

    tag_to_correspondent_map = {
        "ing": "ING",
        "ubs": "UBS",
        "UBS": "UBS",
        "mvb": "MVB",
        "MVB": "MVB",
        "DRV": "DRV",
        "comdirect": "comdirect",
        "JGU": "JGU Mainz",
        "DPG": "DPG",
        "edf": "EDF",
        "Uniqa": "Uniqa",
        "google": "Google",
        "Hetzner": "Hetzner",
        "apple": "Apple",
        "axa": "AXA",
        "union investment": "Union Investment",
        "strato": "Strato",
        "congstar": "congstar",
        "tk": "TK",
        "orange": "Orange",
    }

    tag_to_document_type_map = {
        "receipt": "Receipt",
        "paper": "Paper",
        "invoice": "Invoice",
    }

    for correspondent in tag_to_correspondent_map.values():
        if correspondent not in correspondents:
            if not dry_run:
                correspondents[correspondent] = create_correspondent(
                    url, token, correspondent
                )
            else:
                correspondents[correspondent] = f"{correspondent} (NEW)"

    for document_type in tag_to_document_type_map.values():
        if document_type not in document_types:
            if not dry_run:
                document_types[document_type] = create_document_type(
                    url, token, document_type
                )
            else:
                document_types[document_type] = f"{document_type} (NEW)"

    try:
        files = []

        if os.path.isfile(source):
            files.append(Path(source).resolve())
        else:
            for dirpath, _, filenames in os.walk(source):
                for file in filenames:
                    if file.startswith("."):
                        continue

                    path = (Path(dirpath) / file).resolve()
                    files.append(path)

        for path in files:
            tags = get_tags(path)
            try:
                info = parse_filename(path.name)
            except RuntimeError:
                info = dataclass(dt=None, name=None, tags=set())

            data = []

            tags |= info.tags
            tags = {tag.strip() for tag in tags if tag.strip() != ""}

            tags = {tag_map.get(tag, tag) for tag in tags}

            for tag, correspondent in tag_to_correspondent_map.items():
                if tag in tags:
                    data.append(("correspondent", correspondents[correspondent]))
                    tags.remove(tag)

            for tag, document_type in tag_to_document_type_map.items():
                if tag in tags:
                    data.append(("document_type", document_types[document_type]))
                    tags.remove(tag)

            tags -= tag_filterlist

            tags_seen |= tags

            tags.add("ingest")

            print(path)
            print(tags)

            for tag in tags:
                if tag.strip() == "":
                    continue
                if dry_run:
                    data.append(("tags", f"{tag} (NEW)"))
                else:
                    if tag == "":
                        continue
                    if not tag in tags_to_ids:
                        tags_to_ids[tag] = create_tag(url, token, tag)
                    data.append(("tags", tags_to_ids[tag]))

            if info.name is not None:
                name, _ = os.path.splitext(info.name)
                data.append(("title", name))

            date = info.dt
            if date is None:
                stat = os.stat(path)
                #  print("date from stat", stat)
                date = datetime.fromtimestamp(stat.st_mtime)

            date = date.date()

            data.append(("created", str(date)))

            #  print("-", path)
            #  print("  name:", info.name)
            #  print("  tags:", tags)
            #  print("  date:", date)
            #  print("  info:", info)

            full_url = f"{url}/api/documents/post_document/"

            print(data)

            if not dry_run:
                with open(path, "rb") as fh:
                    r = requests.post(
                        full_url,
                        headers={"Authorization": f"Token {token}"},
                        files={"document": fh},
                        data=data,
                    )
                    result = r.json()
                    try:
                        r.raise_for_status()
                    except requests.exceptions.HTTPError:
                        print("Failed:", path)
                        print(*r.json()["document"])
                        if failed is not None:
                            Path(failed).mkdir(exist_ok=True, parents=True)
                            dest = failed / Path(path).name
                            print(dest, " exists?", dest.exists())
                            if not dest.exists() and not dest.is_symlink():
                                subprocess.check_call(["ln", "-s", path, str(dest)])
                        continue

                    pass
            print()

        print("All tags seen:", tags_seen)

    except Exception as e:
        logger.error("Caught exception: %s" % str(e), exc_info=True)


if __name__ == "__main__":
    main()
