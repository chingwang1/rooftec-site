from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent

pat = re.compile(
    r'<a class="brand" href="([^"]+)">\s*'
    r'<img src="[^"]*logo\.svg"[^>]*>\s*'
    r'<span class="brand-text">[^<]*</span>\s*'
    r"</a>",
    re.I | re.S,
)

for p in root.rglob("*.html"):
    if "node_modules" in p.parts or "backup" in p.name:
        continue
    t = p.read_text(encoding="utf-8")
    if 'class="brand"' not in t:
        continue
    depth = len(p.relative_to(root).parts) - 1
    prefix = "../" * depth
    lockup = f"{prefix}assets/logo-lockup.png"

    def repl(m, lockup=lockup):
        href = m.group(1)
        return (
            f'<a class="brand" href="{href}">'
            f'<img src="{lockup}" alt="Brisbane Roofing Services" '
            f'class="brand-lockup" width="280" height="90">'
            f"</a>"
        )

    t2, n = pat.subn(repl, t)
    if n:
        p.write_text(t2, encoding="utf-8")
        print(f"updated {p.relative_to(root)} ({n})")
    elif "brand-text" in t:
        print(f"MISS {p.relative_to(root)}")
