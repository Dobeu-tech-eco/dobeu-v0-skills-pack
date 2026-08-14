"""Tests for tools/validate.py — stdlib only (no pytest required)."""
import os, sys, tempfile, textwrap

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
from validate import validate_skill

def make_skill(root, folder, content):
    d = os.path.join(root, folder)
    os.makedirs(d)
    with open(os.path.join(d, "SKILL.md"), "w") as f:
        f.write(textwrap.dedent(content))
    return d

def run_tests():
    passed = failed = 0

    def check(name, condition):
        nonlocal passed, failed
        if condition:
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}")
            failed += 1

    with tempfile.TemporaryDirectory() as r:
        d = make_skill(r, "good-skill", """\
            ---
            name: good-skill
            description: Does X. Use when Y.
            ---
            # Body
        """)
        check("valid skill passes", validate_skill(d) == [])

        d = make_skill(r, "folder-a", "---\nname: other-name\ndescription: d\n---\nbody\n")
        check("name mismatch fails", any("folder" in e or "name" in e for e in validate_skill(d)))

        d = make_skill(r, "no-desc", "---\nname: no-desc\n---\nbody\n")
        check("missing description fails", any("description" in e for e in validate_skill(d)))

        d = make_skill(r, "Bad-Name", "---\nname: Bad-Name\ndescription: d\n---\nbody\n")
        check("uppercase name fails", any("regex" in e or "lowercase" in e or "fails" in e for e in validate_skill(d)))

        d = make_skill(r, "big-skill", "---\nname: big-skill\ndescription: d\n---\nbody\n")
        with open(os.path.join(d, "big.txt"), "w") as f:
            f.write("x" * (2 * 1024 * 1024 + 1))
        check("oversize file fails", any("2 MB" in e for e in validate_skill(d)))

        d = make_skill(r, "bin-skill", "---\nname: bin-skill\ndescription: d\n---\nbody\n")
        with open(os.path.join(d, "img.png"), "wb") as f:
            f.write(b"\x89PNG\x00\x01")
        check("binary file fails", any("binary" in e for e in validate_skill(d)))

    print(f"\n{passed} passed, {failed} failed")
    return failed

if __name__ == "__main__":
    sys.exit(run_tests())
