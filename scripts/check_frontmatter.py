"""Validate every SKILL.md frontmatter. Run before committing.

A skill's frontmatter is YAML, and a description is a plain scalar — so a bare colon-space inside it ("specific to
that service: its template") is read as a nested mapping and the whole block fails to parse. GitHub renders that
as a red error box instead of the file, and a loader may read no description at all, which means the skill never
triggers. Nothing else in the file breaks, so it is invisible locally.

    python3 scripts/check_frontmatter.py
"""
import glob, os, sys

try:
    import yaml
except ImportError:
    sys.exit('needs pyyaml: pip install pyyaml')

bad = 0
for f in sorted(glob.glob('*/SKILL.md')):
    txt = open(f, encoding='utf-8').read()
    if not txt.startswith('---'):
        print(f'{f}: no frontmatter'); bad += 1; continue
    fm = txt.split('---')[1]
    try:
        d = yaml.safe_load(fm)
    except Exception as e:
        print(f'{f}: YAML FAILS — {e}')
        for i, line in enumerate(fm.strip().split('\n'), 1):
            if ': ' in line[line.find(': ') + 2:]:
                print(f'    line {i} has a second ": " — quote it or use a dash')
        bad += 1; continue
    missing = [k for k in ('name', 'description') if not d.get(k)]
    if missing:
        print(f'{f}: missing {missing}'); bad += 1; continue
    name = os.path.dirname(f)
    if d['name'] != name:
        print(f'{f}: name "{d["name"]}" does not match folder "{name}"'); bad += 1; continue
    print(f'{f:24} ok   {d["name"]:10} {len(d["description"])} char description')
sys.exit(1 if bad else 0)
