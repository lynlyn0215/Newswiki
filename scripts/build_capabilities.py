from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path


DEFAULT_CLI_TOOLS = [
    "git",
    "python",
    "node",
    "npm",
    "rg",
    "curl",
    "gh",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def words(value: str) -> list[str]:
    return sorted({w.lower() for w in re.findall(r"[a-zA-Z0-9_-]{3,}", value)})


def capability(item_id: str, name: str, description: str, tags: list[str], path: str | None = None) -> dict:
    data = {
        "id": item_id,
        "name": name,
        "description": description,
        "tags": tags[:12],
    }
    if path:
        data["path"] = path
    return data


def scan_skills(root: Path) -> list[dict]:
    results: list[dict] = []
    if not root.exists():
        return results
    for skill_file in sorted(root.rglob("SKILL.md")):
        text = read_text(skill_file)
        fm = parse_frontmatter(text)
        name = fm.get("name") or skill_file.parent.name
        description = fm.get("description") or first_heading_or_line(text)
        tags = ["skill", *words(f"{name} {description}")[:8]]
        rel = str(skill_file)
        results.append(capability(f"skill.{slug(name)}", name, description[:240], tags, rel))
    return results


def first_heading_or_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip().lstrip("#").strip()
        if clean and clean != "---":
            return clean
    return ""


def slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return clean or "unknown"


def scan_mcp_config(config_path: Path) -> list[dict]:
    if not config_path.exists():
        return []
    text = read_text(config_path)
    names = re.findall(r"\[mcp_servers\.([^\]]+)\]", text)
    return [
        capability(
            f"mcp.{slug(name)}",
            name,
            "MCP server configured in local agent config.",
            ["mcp", *words(name)[:8]],
            str(config_path),
        )
        for name in names
    ]


def scan_cli_tools(tool_names: list[str]) -> list[dict]:
    results: list[dict] = []
    for name in tool_names:
        path = shutil.which(name)
        if not path:
            continue
        results.append(
            capability(
                f"cli.{slug(name)}",
                name,
                "CLI tool available on PATH.",
                ["cli", name.lower()],
                path,
            )
        )
    return results


def build_chains(items: list[dict]) -> list[dict]:
    ids = {item["id"] for item in items}
    chains = [
        {
            "id": "startup.default",
            "name": "Default Newswiki Startup",
            "intents": ["plan", "work", "research", "architecture"],
            "steps": ["Capability MCP", "Wiki MCP", "Newsfeed MCP when current information matters"],
        }
    ]
    if any(item_id.startswith("mcp.") and "wiki" in item_id for item_id in ids):
        chains.append(
            {
                "id": "wiki.memory",
                "name": "Wiki Memory",
                "intents": ["wiki", "memory", "past", "knowledge"],
                "steps": ["Wiki MCP", "write back durable learning when useful"],
            }
        )
    if any(item_id.startswith("mcp.") and "news" in item_id for item_id in ids):
        chains.append(
            {
                "id": "news.context",
                "name": "Recent News Context",
                "intents": ["news", "current", "trend", "research"],
                "steps": ["Newsfeed MCP", "Wiki MCP for durable follow-up"],
            }
        )
    return chains


def default_skill_roots() -> list[Path]:
    roots: list[Path] = []
    env = os.environ.get("NEWSWIKI_SKILL_ROOTS")
    if env:
        roots.extend(Path(part).expanduser() for part in env.split(os.pathsep) if part.strip())
    home = Path.home()
    roots.extend([home / ".codex" / "skills", home / ".agents" / "skills", home / ".claude" / "skills"])
    return roots


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local capability catalog for Newswiki Capability MCP.")
    parser.add_argument("--output", default="capabilities.json")
    parser.add_argument("--skill-root", action="append", default=[])
    parser.add_argument("--mcp-config", action="append", default=[])
    parser.add_argument("--cli", action="append", default=[])
    args = parser.parse_args()

    skill_roots = [Path(p).expanduser() for p in args.skill_root] or default_skill_roots()
    mcp_configs = [Path(p).expanduser() for p in args.mcp_config] or [Path.home() / ".codex" / "config.toml"]
    cli_tools = args.cli or DEFAULT_CLI_TOOLS

    capabilities: list[dict] = []
    for root in skill_roots:
        capabilities.extend(scan_skills(root))
    for config_path in mcp_configs:
        capabilities.extend(scan_mcp_config(config_path))
    capabilities.extend(scan_cli_tools(cli_tools))

    seen: set[str] = set()
    unique: list[dict] = []
    for item in capabilities:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)

    catalog = {
        "generated_by": "Newswiki scripts/build_capabilities.py",
        "capabilities": unique,
        "chains": build_chains(unique),
    }
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {output} ({len(unique)} capabilities)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
