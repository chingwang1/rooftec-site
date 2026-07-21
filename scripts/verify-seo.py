from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for f in [
    "index.html",
    "about.html",
    "tools/index.html",
    "services/colorbond-roofing.html",
    "contact.html",
]:
    t = (ROOT / f).read_text(encoding="utf-8")
    print(
        f"{f}: og={'og:title' in t} tw={'twitter:card' in t} "
        f"fav={'favicon' in t} tools={'Tools</a>' in t or 'tools/' in t} "
        f"mdash={chr(0x2014) in t} copy={chr(0xA9) in t}"
    )

idx = (ROOT / "index.html").read_text(encoding="utf-8")
print("index has #tools section:", 'id="tools"' in idx)
print("index landing Tools:", any("Tools" in L for L in idx.splitlines() if "landing-nav" in idx))
# print nav lines
for L in idx.splitlines():
    if "Tools" in L or "og:image" in L:
        print(" ", L.strip()[:130])

sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
print("sitemap /tools/ count:", sm.count("/tools/"))
print("sitemap urls:", sm.count("<url>"))

# Check about nav has Tools
about = (ROOT / "about.html").read_text(encoding="utf-8")
if "Tools</a>" not in about:
    print("WARNING: about missing Tools nav")
else:
    print("about Tools nav: OK")

# Double-check no classic mojibake
for p in ROOT.rglob("*.html"):
    if "node_modules" in p.parts:
        continue
    t = p.read_text(encoding="utf-8")
    if "â€" in t or "Â·" in t or "Ã" in t:
        print("MOJIBAKE?", p)
print("scan done")
