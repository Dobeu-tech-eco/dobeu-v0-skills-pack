"""Copy include-copy skills from audit.csv into skills/, with attribution."""
import csv, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import validate_skill, _frontmatter, NAME_RE

DEST = "skills"


def compliant_name(raw):
    n = re.sub(r"[^a-z0-9-]+", "-", raw.lower()).strip("-")
    n = re.sub(r"-{2,}", "-", n)
    return n if NAME_RE.match(n) else None


def copy_skill(src, origin, license_str):
    fm = _frontmatter(os.path.join(src, "SKILL.md")) or {}
    raw_name = str(fm.get("name") or os.path.basename(src))
    name = compliant_name(raw_name)
    if not name:
        return f"SKIP {src}: cannot derive compliant name from '{raw_name}'"
    dst = os.path.join(DEST, name)
    if os.path.exists(dst):
        return f"SKIP {src}: duplicate name '{name}'"

    shutil.copytree(src, dst)

    md_path = os.path.join(dst, "SKILL.md")
    text = open(md_path, encoding="utf-8").read()
    if f"name: {name}" not in text:
        text = re.sub(r"^(name:\s*).*$", f"name: {name}", text, count=1, flags=re.M)

    if origin not in ("dobeu",) and "<!-- Source:" not in text:
        close = text.index("---", 3) + 3
        attrib = (f"\n<!-- Source: {origin}/{os.path.basename(src)}; "
                  f"license: {license_str or 'see origin'}; "
                  f"repackaged for Dobeu Tech Solutions pack 2026-08-13 -->")
        text = text[:close] + attrib + text[close:]

    open(md_path, "w", encoding="utf-8").write(text)

    scripts = os.path.join(dst, "scripts")
    if os.path.isdir(scripts):
        shutil.rmtree(scripts)

    errs = validate_skill(dst)
    return f"OK {name}" if not errs else f"INVALID {name}: {errs}"


os.makedirs(DEST, exist_ok=True)
results = []
for row in list(csv.reader(open("manifest/audit.csv")))[1:]:
    src_path, skill_name, origin, decision, reason, lic = row
    if decision == "include-copy":
        results.append(copy_skill(src_path, origin, lic))

for r in results:
    print(r)

ok = sum(1 for r in results if r.startswith("OK"))
print(f"\n{ok} packaged, {len(results) - ok} problems")
