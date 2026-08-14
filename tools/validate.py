"""SKILL.md validator - no external deps; uses stdlib re only."""
import os, re, sys

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_BYTES = 2 * 1024 * 1024

def _frontmatter(path):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        return None
    block = m.group(1)
    result = {}
    for line in block.splitlines():
        kv = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
                val = val[1:-1]
            result[key] = val
    return result

def validate_skill(skill_dir):
    errors = []
    folder = os.path.basename(skill_dir.rstrip("/\\"))
    md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(md):
        return [f"{folder}: missing SKILL.md"]
    fm = _frontmatter(md)
    if fm is None:
        return [f"{folder}: missing or unparsable YAML frontmatter"]
    name = fm.get("name")
    desc = fm.get("description")
    if not isinstance(name, str) or not name:
        errors.append(f"{folder}: frontmatter 'name' missing")
    else:
        if not NAME_RE.match(name):
            errors.append(f"{folder}: name '{name}' fails lowercase-hyphen regex")
        if name != folder:
            errors.append(f"{folder}: name '{name}' does not match folder name '{folder}'")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{folder}: frontmatter 'description' missing or empty")
    for root, _dirs, files in os.walk(skill_dir):
        for f in files:
            p = os.path.join(root, f)
            size = os.path.getsize(p)
            if size > MAX_BYTES:
                errors.append(f"{folder}: {f} exceeds 2 MB ({size} bytes)")
            with open(p, "rb") as fh:
                if b"\x00" in fh.read(8192):
                    errors.append(f"{folder}: {f} appears binary (null bytes)")
    return errors

def main(skills_root):
    if not os.path.isdir(skills_root):
        print(f"ERROR: {skills_root} is not a directory")
        return 1
    entries = sorted(e for e in os.listdir(skills_root)
                     if os.path.isdir(os.path.join(skills_root, e)))
    all_errors = []
    for entry in entries:
        all_errors += validate_skill(os.path.join(skills_root, entry))
    for e in all_errors:
        print("ERROR:", e)
    print(f"Checked {len(entries)} folders, {len(all_errors)} errors")
    return 1 if all_errors else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "skills"))
