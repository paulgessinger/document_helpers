import typer
import requests
import rich.console
import rich.panel
import rich.table
import rich.progress

import shutil
from pathlib import Path
from typing import Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


console = rich.console.Console()

app = typer.Typer()

def get_all_tags(url, token):
    url = f"{url}/api/tags/?page_size=100000"

    r = requests.get(
        url,
        headers={"Authorization": f"Token {token}"},
    )

    r.raise_for_status()

    data = r.json()

    return {c["name"]: c["id"] for c in data["results"]}

@app.command()
def main(
    url: str,
    token: str,
    originals: Optional[Path] = typer.Option(None, exists=True, file_okay=False),
    archive: Optional[Path] = typer.Option(None, exists=True, file_okay=False),
    output: Optional[Path] = typer.Option(None, exists=True, file_okay=False),
    recover: bool = False,
):
    documents_url = f"{url}/api/documents/?page_size=100000"


    paths = [originals, archive, output]
    assert all([p is not None for p in paths]) or not any(
        [p is not None for p in paths]
    ), "Either all or none of the paths must be specified"

    with console.status("Getting 'broken' tags") as status:
        tags = get_all_tags(url, token)
        broken_tag = tags["broken"]


    with console.status("[bold green]Getting all documents") as status:
        r = requests.get(
            documents_url,
            headers={"Authorization": f"Token {token}"},
        )

        # print(r.json())

        def check_document(doc: dict[str, Any]) -> tuple[dict[str, Any], bool]:
            doc_url = f"{url}/api/documents/{doc['id']}/download/"

            r = requests.get(
                doc_url, headers={"Authorization": f"Token {token}"}, stream=True
            )

            if r.status_code == 200:
                return doc, True

            else:
                return doc, False

        def get_meta(doc_id: int) -> dict[str, Any]:
            return requests.get(
                f"{url}/api/documents/{doc_id}/metadata/",
                headers={"Authorization": f"Token {token}"},
            ).json()

        docs = r.json()["results"]
        print("Have", len(docs), "documents")

    with ThreadPoolExecutor(max_workers=10) as executor:
        broken = []

        futures = []

        for doc in docs:
            futures.append(executor.submit(check_document, doc))

        for future in rich.progress.track(
            as_completed(futures),
            description=f"[bold green]Checking {len(docs)} documents...",
            console=console,
            total=len(docs),
        ):
            doc, ok = future.result()

            #  print(doc["id"], doc["title"])

            #  print("->", "OK" if ok else "BROKEN")

            if not ok:
                broken.append(doc)

        #  broken = [2067, 2069, 2096, 2115, 2201, 2206, 2207, 2208, 2209]

        status.update(
            f"[bold green]Getting metadata for {len(broken)} broken documents!"
        )

        broken_meta = list(executor.map(get_meta, broken))

        for doc_id, meta in zip(broken, broken_meta):
            table = rich.table.Table()
            table.add_row("Original filename", meta["original_filename"])
            table.add_row("Media filename", meta["media_filename"])
            table.add_row(
                "URL", f"https://paperless.gessinger.dev/documents/{doc_id}/"
            )

            path_prefix = Path(meta["media_filename"]).parent

            original = (
                originals / path_prefix / meta["original_filename"]
                if originals is not None
                else None
            )
            media = (
                archive / meta["media_filename"] if archive is not None else None
            )

            table.add_row("Original path", str(original) if original else "N/A")
            table.add_row("Media path", str(media) if media else "N/A")

            table.add_row(
                "Original found?",
                str(original.exists()) if original is not None else "N/A",
            )
            table.add_row(
                "Media found?", str(media.exists()) if media is not None else "N/A"
            )

            rich.print(rich.panel.Panel(table, title=f"Document #{doc_id}"))

            #  print(media, media.exists())
            if output.exists() :
                if media.exists():
                    shutil.copy(media, output / Path(meta["media_filename"]).name)
                else:
                    rich.print("[red bold]Media file not found!")

        #  print("---")
        #  c = archive / "2021"/"03"/"2021-03-19--Letter_Anschreiben Vorsitz Gessinger-Befurt (ausgefüllt)__DOCT.pdf"
        #  print(type(c), c, (c).exists())
