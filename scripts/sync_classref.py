"""Refresh the generated XML snapshot from a local plugin checkout."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil

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
    translations = plugin / 'addons/fmod_player/translations/documentation'
    translation_checksums = {}
    output = ROOT / 'classref/translations'
    output.mkdir(parents=True, exist_ok=True)
    for source in sorted(translations.glob('*.po')):
        data = source.read_bytes().replace(b'\r\n', b'\n')
        (output / source.name).write_bytes(data)
        translation_checksums[source.name] = hashlib.sha256(data).hexdigest()
    if not translation_checksums:
        raise ValueError('Plugin documentation PO files are missing')
    for stale in output.glob('*.po'):
        if stale.name not in translation_checksums:
            stale.unlink()
    helper = plugin / 'tools/documentation_translations.py'
    if helper.is_file():
        shutil.copy2(helper, ROOT / 'scripts/documentation_translations.py')
    else:
        # Newer plugin checkouts keep this maintenance tool in the docs repository.
        helper = ROOT / 'scripts/documentation_translations.py'
    manifest['translation_sha256'] = translation_checksums
    manifest['localization_tool_sha256'] = hashlib.sha256(helper.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", required=True, type=Path)
    parser.add_argument("--api", required=True, type=Path, help="ClassDB export from the same plugin build")
    args = parser.parse_args()
    sync(args.plugin_root.resolve(), args.api.resolve())
