#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


FORBIDDEN_PRIVATE_REPOSITORY = "ORESoftware" + "/" + "project-registry"
SAFE_PRIVATE_REGISTRY = "approved-private-registry"


def contains_forbidden_reference(text: str) -> bool:
    return FORBIDDEN_PRIVATE_REPOSITORY in text


def tracked_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [root / raw.decode() for raw in result.stdout.split(b"\0") if raw]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for path in tracked_paths(root):
        relative = path.relative_to(root).as_posix()
        try:
            if path.is_symlink():
                text = path.readlink().as_posix()
            else:
                text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if contains_forbidden_reference(text):
            errors.append(f"private repository reference in {relative}")

        if path.name == "repository-relationships.json":
            try:
                graph = json.loads(text)
            except json.JSONDecodeError:
                continue
            if graph.get("audience") != "public":
                continue
            managed_by = (graph.get("generated") or {}).get("managed_by")
            if managed_by != "ore-repository-relationship-rollout":
                continue
            locator = (graph.get("private_registry") or {}).get("repository")
            if locator != SAFE_PRIVATE_REGISTRY:
                errors.append(f"non-opaque private registry locator in {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert contains_forbidden_reference(
            "ORESoftware" + "/" + "project-registry"
        )
        assert not contains_forbidden_reference(SAFE_PRIVATE_REGISTRY)
        print("Public privacy validator self-test passed.")
        return 0
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Public privacy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
