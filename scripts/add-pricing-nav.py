# -*- coding: utf-8 -*-
"""Add Pricing nav link + footer link across site HTML pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def pricing_href(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return ("../" * depth) + "pricing.html"


def patch(html: str, href: str, is_index: bool = False) -> str:
    # Already has pricing nav?
    if re.search(r'href="[^"]*pricing\.html"[^>]*>\s*Pricing\s*<', html, re.I):
        # still ensure class nav-pricing on standard nav
        pass
    else:
        # Landing nav (index)
        if 'class="landing-nav"' in html:
            html = re.sub(
                r'(<nav class="landing-nav"[^>]*>.*?)(<a href="[^"]*about\.html">About</a>)',
                rf'\1<a class="nav-pricing" href="{href}">Pricing</a>\n            \2',
                html,
                count=1,
                flags=re.I | re.S,
            )
        # Standard nav: after Tools, before About
        if re.search(r'<a href="[^"]*tools/[^"]*">Tools</a>', html):
            html = re.sub(
                r'(<a href="[^"]*tools/[^"]*">Tools</a>\s*)',
                rf'\1<a class="nav-pricing" href="{href}">Pricing</a>\n                ',
                html,
                count=1,
                flags=re.I,
            )
        elif re.search(r'<a href="[^"]*about\.html">About</a>', html):
            html = re.sub(
                r'(<a href="[^"]*about\.html">About</a>)',
                rf'<a class="nav-pricing" href="{href}">Pricing</a>\n                \1',
                html,
                count=1,
                flags=re.I,
            )

    # Footer resources / free inspection
    if "Build &amp; price" not in html and "Build & price" not in html:
        html = re.sub(
            r'(<a href="[^"]*tools/[^"]*">Roofing tools[^<]*</a>)',
            rf'<a href="{href}">Build &amp; price</a>\n                \1',
            html,
            count=1,
            flags=re.I,
        )
        html = re.sub(
            r'(<a href="[^"]*contact\.html">Free inspection</a>)',
            rf'<a href="{href}">Build &amp; price</a>\n                \1',
            html,
            count=1,
            flags=re.I,
        )

    # Home tools section: feature pricing
    if is_index and "pricing.html" not in html.split('id="tools"')[-1][:800] if 'id="tools"' in html else True:
        if 'id="tools"' in html and 'href="pricing.html"' not in html[html.find('id="tools"') : html.find('id="tools"') + 900]:
            html = html.replace(
                '<a class="card" href="tools/roof-map-measure.html">',
                '<a class="card" href="pricing.html"><h3>Build &amp; price</h3><p>Map measure + Colorbond profile, colour and competitive SEQ estimate on one page.</p><span class="more">Open pricing →</span></a>\n                    <a class="card" href="tools/roof-map-measure.html">',
                1,
            )
            # might break grid-3 with 4 cards - replace first three only is ok, or leave 4
            # Fix if we duplicated wrong - check structure
            # The replace inserts before map measure so we have 4 cards - change grid or leave

    return html


def main():
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if path.name == "pricing.html":
            continue
        html = path.read_text(encoding="utf-8")
        href = pricing_href(path)
        new = patch(html, href, is_index=path.name == "index.html" and path.parent == ROOT)
        if new != html:
            path.write_text(new, encoding="utf-8")
            print("patched", path.relative_to(ROOT))
        else:
            print("no change", path.relative_to(ROOT))

    # sitemap
    sm = ROOT / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    if "pricing.html" not in text:
        text = text.replace(
            "  <url><loc>https://brisbaneroofingservice.com/tools/</loc>",
            "  <url><loc>https://brisbaneroofingservice.com/pricing.html</loc><changefreq>weekly</changefreq><priority>0.98</priority></url>\n"
            "  <url><loc>https://brisbaneroofingservice.com/tools/</loc>",
            1,
        )
        sm.write_text(text, encoding="utf-8")
        print("sitemap updated")

    # cost estimator banner pointing to full pricing
    ce = ROOT / "tools" / "roof-cost-estimator.html"
    if ce.exists():
        t = ce.read_text(encoding="utf-8")
        if "pricing.html" not in t or "full build" not in t.lower():
            t = t.replace(
                '<p class="mm-hint"><a href="roof-map-measure.html"><strong>Measure roof m² on the satellite map →</strong></a>',
                '<p class="mm-hint"><a href="../pricing.html"><strong>Open full Build &amp; Price tool (map + colours + profiles) →</strong></a></p>\n'
                '        <p class="mm-hint"><a href="roof-map-measure.html"><strong>Measure roof m² on the satellite map only →</strong></a>',
                1,
            )
            ce.write_text(t, encoding="utf-8")
            print("cost estimator linked")

    # map measure link to pricing
    mm = ROOT / "tools" / "roof-map-measure.html"
    if mm.exists():
        t = mm.read_text(encoding="utf-8")
        if 'id="mm-to-cost"' in t and "pricing.html" not in t[t.find("mm-to-cost") : t.find("mm-to-cost") + 200]:
            t = t.replace(
                '<a class="cta" id="mm-to-cost" href="roof-cost-estimator.html">Use in cost estimator →</a>',
                '<a class="cta" id="mm-to-cost" href="../pricing.html">Use in Build &amp; Price →</a>\n'
                '                        <a class="btn btn-outline" href="roof-cost-estimator.html">Simple cost estimator</a>',
                1,
            )
            # also update map-measure.js default cost link - handled separately
            mm.write_text(t, encoding="utf-8")
            print("map measure linked")


if __name__ == "__main__":
    main()
