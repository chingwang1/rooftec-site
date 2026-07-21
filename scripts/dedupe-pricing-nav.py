from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
pat = re.compile(
    r'(<a class="nav-pricing" href="[^"]+">Pricing</a>)\s*'
    r'<a class="nav-pricing" href="[^"]+">Pricing</a>',
    re.I,
)

for p in ROOT.rglob("*.html"):
    if "node_modules" in p.parts:
        continue
    t = p.read_text(encoding="utf-8")
    new, n = pat.subn(r"\1", t)
    # also multiple repeats
    while True:
        new2, n2 = pat.subn(r"\1", new)
        if n2 == 0:
            break
        new = new2
        n += n2
    if new != t:
        p.write_text(new, encoding="utf-8")
        print("fixed", p.relative_to(ROOT), "removals", n)
    else:
        c = len(re.findall(r'class="nav-pricing"', t))
        if c != 1 and p.name != "pricing.html":
            # pricing page has 1, tools may have footer only
            if c > 1:
                print("still multi", p.relative_to(ROOT), c)
