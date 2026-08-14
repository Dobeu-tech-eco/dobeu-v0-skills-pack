"""Build dobeu-v0-skills-pack.zip using Python stdlib zipfile."""
import os, sys, zipfile

INCLUDE_DIRS  = ["skills", "manifest"]
INCLUDE_FILES = ["README.md", "NOTICE.md", "PACK-SETUP.md"]
OUTPUT = "dobeu-v0-skills-pack.zip"
EXCLUDE = {"__pycache__", ".pyc"}


def should_skip(path):
    return any(x in path for x in EXCLUDE)


with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
    count = 0
    for d in INCLUDE_DIRS:
        if not os.path.isdir(d): continue
        for root, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in EXCLUDE]
            for f in files:
                path = os.path.join(root, f)
                if not should_skip(path):
                    zf.write(path)
                    count += 1
    for f in INCLUDE_FILES:
        if os.path.isfile(f):
            zf.write(f)
            count += 1
    names = zf.namelist()

size_kb = os.path.getsize(OUTPUT) / 1024
print(f"Built {OUTPUT}: {count} files, {size_kb:.1f} KB")
for n in sorted(names):
    print(f"  {n}")
