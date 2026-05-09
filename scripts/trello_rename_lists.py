"""Trelloリストをリネーム（UTF-8対応）"""
import os
import json
import urllib.parse
import urllib.request


def load_env(path: str = ".env") -> None:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)


def rename_list(list_id: str, new_name: str) -> None:
    key = os.environ["TRELLO_API_KEY"]
    token = os.environ["TRELLO_TOKEN"]
    data = urllib.parse.urlencode({"name": new_name}).encode("utf-8")
    url = f"https://api.trello.com/1/lists/{list_id}?key={key}&token={token}"
    req = urllib.request.Request(url, data=data, method="PUT")
    with urllib.request.urlopen(req) as r:
        body = json.loads(r.read())
        print(f"  status={r.status} id={body['id']} name={body['name']!r}")


if __name__ == "__main__":
    load_env()
    print("=== Rename 5ffe5b3fa17b04881f2c4fc3 -> 5月 ===")
    rename_list("5ffe5b3fa17b04881f2c4fc3", "5月")
    print("=== Rename 5ffe5b3fa17b04881f2c4fc4 -> 6月 ===")
    rename_list("5ffe5b3fa17b04881f2c4fc4", "6月")
