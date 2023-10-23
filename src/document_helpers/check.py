import typer
import requests

app = typer.Typer()


@app.command()
def main(url: str, token: str):
    documents_url = f"{url}/api/documents/?page_size=100000"

    r = requests.get(
        documents_url,
        headers={"Authorization": f"Token {token}"},
    )

    # print(r.json())

    broken = []
    for doc in r.json()["results"]:
        # if not doc["id"] == 2209: continue
        print(doc["id"], doc["title"])
        doc_url = f"{url}/api/documents/{doc['id']}/download/"
        print("->", doc_url)
        r = requests.get(doc_url, headers={"Authorization": f"Token {token}"}, stream=True)
        if r.status_code == 200:
            print("OK")
        else: 
            print("Not OK")
            broken.append(doc["id"])

    print("---")
    print(broken)