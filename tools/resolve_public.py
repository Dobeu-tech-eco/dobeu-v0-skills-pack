"""Resolve reference-public skills against skills.sh public registry.

If a skill is found publicly, leave it as reference-public (add by reference in pack UI).
If not found and no license, downgrade to exclude.
Emits manifest/pack-ui-add-list.md.
"""
import csv, json, os, time, urllib.parse, urllib.request

API = "https://skills.sh/api/v1/skills/search?q={q}&limit=5"

CURATED_VERCEL = [
    "vercel-react-best-practices",
    "web-design-guidelines",
    "vercel-composition-patterns",
    "next-best-practices",
    "vercel-react-view-transitions",
]


def search_skills_sh(name):
    url = API.format(q=urllib.parse.quote(name))
    req = urllib.request.Request(url, headers={"User-Agent": "dobeu-pack-builder/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
            return data.get("skills") or data.get("results") or data.get("data") or []
    except Exception as e:
        print(f"  [warn] skills.sh lookup failed for '{name}': {e}")
        return None


rows = list(csv.reader(open("manifest/audit.csv")))
header, body = rows[0], rows[1:]

public_refs = []
api_reachable = True

for row in body:
    if row[3] != "reference-public":
        continue
    skill_name = row[1]
    if not api_reachable:
        row[4] = "skills.sh unreachable; add manually if public"
        continue

    print(f"  Searching skills.sh for '{skill_name}' ...")
    hits = search_skills_sh(skill_name)

    if hits is None:
        api_reachable = False
        row[4] = "skills.sh unreachable; add manually if public"
        print("  API unreachable - skipping remaining lookups")
        continue

    exact = next(
        (h for h in hits
         if h.get("slug") == skill_name or h.get("name") == skill_name),
        None,
    )
    if exact:
        sid = exact.get("id") or exact.get("slug") or skill_name
        installs = int(exact.get("installs", 0) or 0)
        row[3] = "reference-public"
        row[4] = f"found on skills.sh as '{sid}'"
        public_refs.append((skill_name, sid, installs))
        print(f"    found: {sid} ({installs} installs)")
    else:
        row[3] = "exclude"
        row[4] = "C4 fail: not found on skills.sh and no redistribution license"
        print(f"    not found - downgrading to exclude")

    time.sleep(0.4)

with open("manifest/audit.csv", "w", newline="") as f:
    csv.writer(f).writerows([header] + body)

with open("manifest/pack-ui-add-list.md", "w") as f:
    f.write("# Skills to add by reference in the skills.sh pack UI\n\n")
    f.write("In the 'Add skills' step of Create pack, search and add each:\n\n")
    if public_refs:
        f.write("## From session - confirmed on skills.sh\n\n")
        for name, sid, installs in sorted(public_refs, key=lambda x: -x[2]):
            f.write(f"- `{name}` - id `{sid}` ({installs:,} installs)\n")
        f.write("\n")
    f.write("## Curated Vercel skills (always add these)\n\n")
    for s in CURATED_VERCEL:
        f.write(f"- `{s}`\n")
    if not public_refs:
        f.write("\n## Session make-plugin skills (add if visible in your account)\n\n")
        f.write("These Figma Make skills passed C2/C3 but could not be confirmed on skills.sh.\n")
        f.write("Search for each in the pack UI - if visible, add by reference:\n\n")
        for row in body:
            if "reference-public" in row[3]:
                f.write(f"- `{row[1]}`\n")

print(f"\n{len(public_refs)} skills confirmed on skills.sh")
