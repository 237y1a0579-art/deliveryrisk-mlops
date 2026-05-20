from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def service_matches(entry: dict[str, Any], service: str) -> bool:
    for key in ("name", "newName"):
        value = str(entry.get(key, ""))
        if value == service or value.endswith(f"/{service}"):
            return True
    return False


def update_image(path: Path, service: str, new_name: str, new_tag: str) -> bool:
    with path.open("r", encoding="utf-8") as f:
        document = yaml.safe_load(f)

    images = document.setdefault("images", [])
    changed = False
    for entry in images:
        if service_matches(entry, service):
            if entry.get("newName") != new_name:
                entry["newName"] = new_name
                changed = True
            if entry.get("newTag") != new_tag:
                entry["newTag"] = new_tag
                changed = True
            break
    else:
        images.append({"name": new_name, "newName": new_name, "newTag": new_tag})
        changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(document, f, sort_keys=False)

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a Kubernetes kustomization image tag.")
    parser.add_argument("--file", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--new-name", required=True)
    parser.add_argument("--new-tag", required=True)
    args = parser.parse_args()

    changed = update_image(
        path=Path(args.file),
        service=args.service,
        new_name=args.new_name,
        new_tag=args.new_tag,
    )
    print("updated" if changed else "unchanged")


if __name__ == "__main__":
    main()

