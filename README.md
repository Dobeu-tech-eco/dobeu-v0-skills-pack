# Dobeu Tech Solutions — v0 Skills Pack

Curated agent skills for v0.app and Cursor, maintained by Dobeu Tech Solutions LLC (dobeu.net).

Install via pack: `npx skills add https://skills.sh/p/<pack-id>` (after pack creation — see PACK-SETUP.md)
Or install this repo: `npx skills add dobeutech/dobeu-v0-skills-pack`
Or install into Cursor globally: `python3 tools/install_to_cursor.py`

## Included skills (1)

- **figma-make-skills** — Dobeu Tech Solutions brand system for Figma Make — indigo/amber palette, Nunito typography, dark-first tokens, and design psychology principles. Use when building any Dobeu-branded React + Tailwind UI in Figma Make.

## Reference skills (add via pack UI — not in this repo)

These skills passed v0 compatibility checks but lack a redistribution license.
Add them by reference when creating the pack at skills.sh/packs.
See `manifest/pack-ui-add-list.md` for the full list.

- **aesthetic-stance** (Figma Make plugin — search in pack UI)
- **design-imports** (Figma Make plugin — search in pack UI)
- **icon-illustration** (Figma Make plugin — search in pack UI)
- **image-attachments** (Figma Make plugin — search in pack UI)
- **make-kit** (Figma Make plugin — search in pack UI)
- **motion-context** (Figma Make plugin — search in pack UI)
- **react-router** (Figma Make plugin — search in pack UI)

## Missing proprietary skills (add manually)

Two Dobeu-proprietary skills were not present in the cloud build environment.
Add them from your local synced skills folder, then re-run the build tools:

| Skill | Purpose |
|---|---|
| `dobeu-v0-design` | Dobeu brand guidelines for v0.app |
| `dobeu-figma-make-design` | Dobeu brand system for Figma Make (alias of `figma-make-skills`) |

```bash
python3 tools/audit.py && python3 tools/package.py
```

See PACK-SETUP.md for full instructions.

## Format
Each skill is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description`).
Validated with `python3 tools/validate.py skills/`. See NOTICE.md for attribution.
