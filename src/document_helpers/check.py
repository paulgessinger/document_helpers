import typer
import requests
import rich.console

from pathlib import Path
from typing import Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


console = rich.console.Console()

app = typer.Typer()


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

        status.update(f"[bold green]Checking {len(docs)} documents...")
        with ThreadPoolExecutor(max_workers=10) as executor:

            broken = []

            if False:
                futures = []

                for doc in docs:
                    futures.append(executor.submit(check_document, doc))

                for future in as_completed(futures):
                    doc, ok = future.result()

                    print(doc["id"], doc["title"])

                    print("->", "OK" if ok else "BROKEN")

                    if not ok:
                        broken.append(doc['id'])


                print("---")

                print(broken)

            broken = [2067, 2069, 2096, 2115, 2201, 2206, 2207, 2208, 2209]

            status.update(f"[bold green]Getting metadata for {len(broken)} broken documents!")

            broken_meta = list(executor.map(get_meta, broken))

            for doc_id, meta in zip(broken, broken_meta):
                original = originals / meta["original_filename"]
                media = archive / meta["media_filename"]
                print(type(media), media, media.exists())


        print("---")
        c = archive / "2021"/"03"/"2021-03-19--Letter_Anschreiben Vorsitz Gessinger-Befurt (ausgefüllt)__DOCT.pdf"
        print(type(c), c, (c).exists())