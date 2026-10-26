"""Refresh the generated XML snapshot from a local plugin checkout."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sync(plugin: Path, api_path: Path) -> None:
    manifest_path = ROOT / "classref/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    revision = subprocess.check_output(["git", "-c", f"safe.directory={plugin.as_posix()}", "-C", str(plugin), "rev-parse", "HEAD"], text=True).strip()
    checksums = {}
    for name in manifest["classes"]:
        source = plugin / "doc_classes" / (name + ".xml")
        data = source.read_bytes().replace(b"\r\n", b"\n")
        destination = ROOT / "classref/xml" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        checksums[source.name] = hashlib.sha256(data).hexdigest()
    api = json.loads(api_path.read_text(encoding="utf-8"))
    for name in manifest["classes"]:
        for method in api[name]["methods"]:
            method.pop("id", None)
            for index, argument in enumerate(method["args"]):
                key = f"{name}.{method['name']}.{index}"
                if not argument["name"] or argument["name"].startswith("_unnamed_arg"):
                    argument["binding_name"] = argument["name"]
                    argument["name"] = manifest["unnamed_arguments"][key]
    (ROOT / "classref/api.json").write_text(json.dumps(api, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest["plugin_revision"] = revision
    manifest["xml_sha256"] = checksums
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", required=True, type=Path)
    parser.add_argument("--api", required=True, type=Path, help="ClassDB export from the same plugin build")
    args = parser.parse_args()
    sync(args.plugin_root.resolve(), args.api.resolve())
