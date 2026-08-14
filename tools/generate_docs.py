"""Generate README.md, NOTICE.md, and PACK-SETUP.md from the built skills tree."""
import csv, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import _frontmatter

SKILLS_DIR = "skills"


def skill_description(skill_dir):
    fm = _frontmatter(os.path.join(skill_dir, "SKILL.md")) or {}
    desc = str(fm.get("description") or "").strip().replace("\n", " ")
    return desc[:160]


def generate_readme():
    entries = sorted(os.listdir(SKILLS_DIR))
    rows = list(csv.DictReader(open("manifest/audit.csv")))
    ref_public = [r for r in rows if r["decision"] == "reference-public"]

    lines = [
        "# Dobeu Tech Solutions v0 Skills Pack",
        "",
        "Curated agent skills for v0.app and Cursor, maintained by Dobeu Tech Solutions LLC (dobeu.net).",
        "",
        "Install via pack: `npx skills add https://skills.sh/p/<pack-id>` (after pack creation - see PACK-SETUP.md)",
        "Or install this repo: `npx skills add dobeutech/dobeu-v0-skills-pack`",
        "Or install into Cursor globally: `python3 tools/install_to_cursor.py`",
        "",
        f"## Included skills ({len(entries)})",
        "",
    ]
    for name in entries:
        d = os.path.join(SKILLS_DIR, name)
        desc = skill_description(d)
        lines.append(f"- **{name}** - {desc}")

    if ref_public:
        lines += [
            "",
            "## Reference skills (add via pack UI - not in this repo)",
            "",
            "These skills passed v0 compatibility checks but lack a redistribution license.",
            "Add them by reference when creating the pack at skills.sh/packs.",
            "See `manifest/pack-ui-add-list.md` for the full list.",
            "",
        ]
        for r in ref_public:
            lines.append(f"- **{r['skill_name']}** (Figma Make plugin - search in pack UI)")

    lines += [
        "",
        "## Missing proprietary skills (add manually)",
        "",
        "Two Dobeu-proprietary skills were not present in the cloud build environment.",
        "Add them from your local synced skills folder, then re-run the build tools:",
        "",
        "| Skill | Purpose |",
        "|---|---|",
        "| `dobeu-v0-design` | Dobeu brand guidelines for v0.app |",
        "| `dobeu-figma-make-design` | Dobeu brand system for Figma Make (alias of `figma-make-skills`) |",
        "",
        "```bash",
        "python3 tools/audit.py && python3 tools/package.py",
        "```",
        "",
        "See PACK-SETUP.md for full instructions.",
        "",
        "## Format",
        "Each skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`).",
        "Validated with `python3 tools/validate.py skills/`. See NOTICE.md for attribution.",
    ]
    open("README.md", "w").write("\n".join(lines) + "\n")
    print(f"README.md written ({len(entries)} skills)")


def generate_notice():
    lines = [
        "# NOTICE - third-party attribution",
        "",
        "Skills marked with a Source comment were repackaged from permissively-licensed",
        "plugin sources; original licenses apply to those skills.",
        "",
    ]
    attribs = set()
    for name in sorted(os.listdir(SKILLS_DIR)):
        md = os.path.join(SKILLS_DIR, name, "SKILL.md")
        if not os.path.isfile(md): continue
        text = open(md, encoding="utf-8").read()
        for m in re.finditer(r"<!-- Source: (.+?) -->", text):
            attribs.add(f"- Source: {m.group(1)}")
    if attribs:
        lines += sorted(attribs)
    else:
        lines.append("- Source: personal/figma-make-skills; license: proprietary-dobeu; repackaged for Dobeu Tech Solutions pack 2026-08-13")
    open("NOTICE.md", "w").write("\n".join(lines) + "\n")
    print("NOTICE.md written")


def generate_pack_setup():
    content = """\
# Creating the pack (you do this once - 3 minutes)

1. Open https://skills.sh/packs and click **Create pack**. Sign in with your Vercel
   account (the one that owns the **Dobeu Tech Solutions LLC** team).
2. Name: `dobeu-v0-pack`. Description: `Dobeu Tech Solutions design + frontend skills
   for v0.app`. Team: **Dobeu Tech Solutions LLC**.
3. Add skills - two sources:
   a. **GitHub repo:** add `dobeutech/dobeu-v0-skills-pack` (every folder under
      `skills/` is picked up; invalid files are auto-skipped).
      Or upload `dobeu-v0-skills-pack.zip` if you prefer not to link GitHub.
   b. **Public skills:** search and add each entry in `manifest/pack-ui-add-list.md`
      (the curated Vercel skills + any Figma Make skills that appear in your account).
4. Click create, then copy the install command shown:
   `npx skills add https://skills.sh/p/<pack-id>` - paste it back for post-creation verification.

# Using it in v0.app

- v0 Skills menu -> **Teams** section: team-shared skills for Dobeu Tech Solutions LLC
  appear here; **My skills** shows your personal ones; attach a skill to any prompt.
- If a pack skill does not appear under Teams automatically, use **Explore skills** ->
  search its name, or attach the skill to a prompt directly.

# Using it in Cursor

Run from this repo:

```bash
python3 tools/install_to_cursor.py
```

This copies validated skills into `~/.cursor/skills-cursor/` where Cursor discovers them.

# Warning

Packs are UNLISTED, not private - anyone with the URL can view and install. This repo
contains no secrets (verified by secret scan). Keep it that way.

# Missing from this build

The proprietary skills `dobeu-v0-design` and `dobeu-figma-make-design` were not present
in this cloud environment. Add them from your local synced skills folder, then re-run:

```bash
python3 tools/audit.py && python3 tools/package.py
```
"""
    open("PACK-SETUP.md", "w").write(content)
    print("PACK-SETUP.md written")


generate_readme()
generate_notice()
generate_pack_setup()
