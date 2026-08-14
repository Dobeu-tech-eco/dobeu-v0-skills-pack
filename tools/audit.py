"""Scan session skill sources against v0.app compatibility criteria C1-C4.

Source paths adapted to the current environment:
  - Custom skills: session plugin custom-skills/skills/
  - Make plugin:   session plugin make/skills/
  - Standard paths (synced) are also tried if they exist.

Outputs manifest/audit.csv with columns:
  source_path, skill_name, origin, decision, reason, license
  decision in {include-copy, reference-public, exclude}
"""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import _frontmatter, validate_skill

SESSION_BASE = "/workspaces/default/sessions"
STANDARD_PERSONAL = "/root/.claude/skills/synced"
STANDARD_PLUGINS  = "/root/.claude/plugins/synced"

ALLOWED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
                    "CC0-1.0", "CC-BY-4.0", "Apache 2.0"}

TOOL_MARKERS = re.compile(
    r"(mcp__[a-z0-9_]+|supabase_connect|search_photos|figma logs|figma make verify"
    r"|scripts/[a-zA-Z0-9_./-]+\.(py|sh|js)|browse daemon|Bash\(|npx\s+(?!create-next-app)"
    r"|subagent|Task tool|COMPOSIO_)", re.I)

DOMAIN = re.compile(
    r"(design|ui|ux|frontend|react|next\.?js|tailwind|shadcn|css|component|layout"
    r"|landing|typograph|color|palette|accessib|wcag|aria|brand|logo|hero|dashboard"
    r"|chart|visualiz|web app|website|page|style|theme|figma|motion|animation|icon"
    r"|illustration|image|photo|v0|make)", re.I)

META_SKILLS = {"claude", "dts", "skillspack", "ask_user_question"}


def find_session_plugins():
    if not os.path.isdir(SESSION_BASE):
        return []
    sources = []
    for session_id in os.listdir(SESSION_BASE):
        plugin_base = os.path.join(SESSION_BASE, session_id, "claude", "plugins")
        if os.path.isdir(plugin_base):
            for plugin_name in os.listdir(plugin_base):
                sk = os.path.join(plugin_base, plugin_name, "skills")
                if os.path.isdir(sk):
                    sources.append((plugin_name, sk))
    return sources


def plugin_license(plugin_root):
    for fname in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        p = os.path.join(plugin_root, fname)
        if os.path.isfile(p):
            head = open(p, encoding="utf-8", errors="replace").read(400)
            if "MIT" in head:        return "MIT"
            if "Apache" in head:     return "Apache-2.0"
            if "BSD" in head:        return "BSD-3-Clause"
    return ""


def audit_one(skill_dir, origin, plugin_lic=""):
    md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(md):
        return None
    fm = _frontmatter(md) or {}
    name = str(fm.get("name") or os.path.basename(skill_dir))
    desc = str(fm.get("description") or "")
    body = open(md, encoding="utf-8", errors="replace").read()
    lic  = str(fm.get("license") or plugin_lic or "")

    errs = validate_skill(skill_dir)
    if errs:
        return (skill_dir, name, origin, "exclude",
                "C1 fail: " + "; ".join(errs[:2]), lic)

    if name in META_SKILLS:
        return (skill_dir, name, origin, "exclude",
                "meta artifact not a v0 behavior skill", lic)

    if "dobeu" in origin.lower() or name.startswith("dobeu-"):
        return (skill_dir, name, origin, "include-copy",
                "Dobeu-owned, v0-native instruction skill", "proprietary-dobeu")

    tool_hits = sorted(set(m.group(0)[:40]
                           for m in TOOL_MARKERS.finditer(body)))[:4]
    if tool_hits:
        return (skill_dir, name, origin, "exclude",
                "C2 fail: requires " + "; ".join(tool_hits), lic)

    if not DOMAIN.search(name + " " + desc):
        return (skill_dir, name, origin, "exclude",
                "C3 fail: not v0 design/frontend domain", lic)

    if origin == "personal":
        return (skill_dir, name, origin, "include-copy",
                "personal/instruction-only/domain-fit (Task 3 may reclassify)", lic or "personal")
    if lic in ALLOWED_LICENSES:
        return (skill_dir, name, origin, "include-copy",
                "permissive license", lic)
    return (skill_dir, name, origin, "reference-public",
            "C4: no redistribution license; reference via skills.sh if public, else exclude", lic or "unknown")


def main():
    rows = []

    if os.path.isdir(STANDARD_PERSONAL):
        for entry in sorted(os.listdir(STANDARD_PERSONAL)):
            d = os.path.join(STANDARD_PERSONAL, entry)
            if not os.path.isdir(d): continue
            origin = "dobeu" if entry.startswith("dobeu-") else "personal"
            r = audit_one(d, origin)
            if r: rows.append(r)

    if os.path.isdir(STANDARD_PLUGINS):
        for plugin in sorted(os.listdir(STANDARD_PLUGINS)):
            sk_root = os.path.join(STANDARD_PLUGINS, plugin, "skills")
            if not os.path.isdir(sk_root): continue
            lic = plugin_license(os.path.join(STANDARD_PLUGINS, plugin))
            for entry in sorted(os.listdir(sk_root)):
                d = os.path.join(sk_root, entry)
                if not os.path.isdir(d): continue
                r = audit_one(d, f"plugin:{plugin}", lic)
                if r: rows.append(r)

    seen_names = {r[1] for r in rows}
    for plugin_name, sk_root in find_session_plugins():
        origin_label = ("custom-skills" if plugin_name == "custom-skills"
                        else f"plugin:{plugin_name}")
        for entry in sorted(os.listdir(sk_root)):
            d = os.path.join(sk_root, entry)
            if not os.path.isdir(d): continue
            fm = (_frontmatter(os.path.join(d, "SKILL.md")) or {})
            skill_name = str(fm.get("name") or entry)
            if skill_name in seen_names:
                continue
            eff_origin = ("dobeu" if skill_name.startswith("dobeu-") or
                          skill_name == "figma-make-skills"
                          else origin_label)
            r = audit_one(d, eff_origin)
            if r:
                rows.append(r)
                seen_names.add(r[1])

    os.makedirs("manifest", exist_ok=True)
    with open("manifest/audit.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_path", "skill_name", "origin", "decision", "reason", "license"])
        w.writerows(rows)

    from collections import Counter
    counts = Counter(r[3] for r in rows)
    print("Decision counts:", dict(counts))
    print("\nIncluded skills:")
    for r in rows:
        if r[3] == "include-copy":
            print(f"  {r[1]:30s} [{r[2]}]")
    print(f"\nTotal scanned: {len(rows)}")


if __name__ == "__main__":
    main()
