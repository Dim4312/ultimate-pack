#!/usr/bin/env python3
"""Collect the real IDs (items, blocks, entities, structures, biomes and their tags) from every mod in the pack.

Run from the repo root:  python3 tools/mod_ids.py
Downloads each mod jar (and the vanilla 1.21.1 client jar) once into ~/.cache/ultimate-pack/jars,
then writes tools/.ids.json. gen_quests.py uses it to refuse quests that point at IDs that don't exist.
CurseForge-only mods have no direct download URL; their namespaces are listed under "unchecked".
"""
import io
import json
import re
import tomllib
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/ultimate-pack/jars"
OUT = ROOT / "tools/.ids.json"
VANILLA = "1.21.1"

LANG_KEY = re.compile(r"^(item|block|entity)\.([a-z0-9_.-]+)\.([a-z0-9_/.-]+)$")
DATA_FILE = re.compile(r"^(?:.*/)?data/([a-z0-9_.-]+)/(worldgen/structure|worldgen/biome|tags/worldgen/structure|tags/worldgen/biome|tags/items?|tags/blocks?)/(.+)\.json$")


def fetch(url, dest):
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "ultimate-pack-tools"})
        with urllib.request.urlopen(req) as r:
            dest.write_bytes(r.read())
    return dest


def vanilla_jar():
    manifest = json.load(urllib.request.urlopen("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"))
    url = next(v["url"] for v in manifest["versions"] if v["id"] == VANILLA)
    client = json.load(urllib.request.urlopen(url))["downloads"]["client"]["url"]
    return fetch(client, CACHE / f"minecraft-{VANILLA}-client.jar")


def scan(jar, ids):
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if name.startswith("META-INF/jarjar/") and name.endswith(".jar"):
                scan(io.BytesIO(z.read(name)), ids)  # bundled mods (e.g. Aeronautics ships Simulated)
                continue
            # Some mods use shared translation keys for whole families of blocks.
            # Their crafting results still name each registered item individually.
            if "/recipe/" in name and name.endswith(".json"):
                try:
                    recipe = json.loads(z.read(name))
                    result = recipe.get("result", {})
                    if recipe.get("type", "").startswith("minecraft:crafting_") and isinstance(result, dict) and "id" in result:
                        ids["item"].add(result["id"])
                except (ValueError, AttributeError):
                    pass
            if name.endswith("lang/en_us.json") and "/assets/" in "/" + name:
                try:
                    lang = json.loads(z.read(name).decode("utf-8", "replace"))
                except ValueError:
                    continue
                for key in lang:
                    m = LANG_KEY.match(key)
                    if m and "." not in m.group(3):
                        kind = "entity" if m.group(1) == "entity" else "item"
                        ids[kind].add(f"{m.group(2)}:{m.group(3)}")
                continue
            m = DATA_FILE.match(name)
            if m:
                ns, kind, path = m.groups()
                key = {
                    "worldgen/structure": "structure", "worldgen/biome": "biome",
                    "tags/worldgen/structure": "structure", "tags/worldgen/biome": "biome",
                }.get(kind, "item")
                prefix = "#" if kind.startswith("tags/") else ""
                ids[key].add(f"{prefix}{ns}:{path}")


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    ids = {k: set() for k in ("item", "entity", "structure", "biome")}
    unchecked = []
    scan(vanilla_jar(), ids)
    for meta in sorted((ROOT / "mods").glob("*.pw.toml")):
        data = tomllib.loads(meta.read_text())
        url = data.get("download", {}).get("url")
        if not url:
            unchecked.append(meta.name.removesuffix(".pw.toml"))
            continue
        scan(fetch(url, CACHE / data["filename"]), ids)
    out = {k: sorted(v) for k, v in ids.items()}
    out["unchecked"] = unchecked
    OUT.write_text(json.dumps(out, indent=0))
    print(f"{OUT.relative_to(ROOT)}: " + ", ".join(f"{len(v)} {k}" for k, v in out.items()))


if __name__ == "__main__":
    main()
