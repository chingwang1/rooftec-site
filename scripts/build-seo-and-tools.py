# -*- coding: utf-8 -*-
"""Bulk SEO upgrades + Tools & Calculators pages for rooftec-site."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://brisbaneroofingservice.com"
PHONE = "0411 510 699"
PHONE_TEL = "+61411510699"
EMAIL = "roofingbrisbane2027@gmail.com"
BRAND = "Roofing Brisbane"


def rel_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth


def seo_head(
    *,
    title: str,
    description: str,
    canonical_path: str,
    prefix: str,
    og_type: str = "website",
    extra_jsonld: list | None = None,
    geo: bool = False,
) -> str:
    canon = SITE + (canonical_path if canonical_path.startswith("/") else "/" + canonical_path)
    og_image = f"{SITE}/assets/og-default.jpg"
    fav = f"{prefix}assets/"
    lines = [
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>{title}</title>",
        f'<meta name="description" content="{description}">',
        f'<link rel="canonical" href="{canon}">',
        '<meta name="robots" content="index,follow">',
        '<meta name="theme-color" content="#1a2b4a">',
    ]
    if geo:
        lines += [
            '<meta name="geo.region" content="AU-QLD">',
            '<meta name="geo.placename" content="Brisbane">',
        ]
    lines += [
        f'<link rel="icon" href="{fav}favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{fav}favicon-32.png" type="image/png" sizes="32x32">',
        f'<link rel="apple-touch-icon" href="{fav}apple-touch-icon.png" sizes="180x180">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{BRAND}">',
        f'<meta property="og:locale" content="en_AU">',
        f'<meta property="og:url" content="{canon}">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:image" content="{og_image}">',
        f'<meta property="og:image:width" content="1200">',
        f'<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="Colorbond roofing by {BRAND} — Brisbane to Sunshine Coast">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{description}">',
        f'<meta name="twitter:image" content="{og_image}">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">',
        f'<link rel="stylesheet" href="{prefix}css/styles.css">',
    ]
    if extra_jsonld:
        for block in extra_jsonld:
            lines.append(
                '<script type="application/ld+json">\n'
                + json.dumps(block, ensure_ascii=False, indent=2)
                + "\n</script>"
            )
    return "\n    ".join(lines)


ORG_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "RoofingContractor",
    "@id": f"{SITE}/#business",
    "name": BRAND,
    "alternateName": ["Brisbane Roofing Services", "Roofing Brisbane SEQ"],
    "url": f"{SITE}/",
    "telephone": "+61-411-510-699",
    "email": EMAIL,
    "image": f"{SITE}/assets/og-default.jpg",
    "logo": f"{SITE}/assets/logo.svg",
    "priceRange": "$$",
    "areaServed": [
        {"@type": "City", "name": "Brisbane"},
        {"@type": "City", "name": "Sunshine Coast"},
        {"@type": "City", "name": "Gold Coast"},
        {"@type": "City", "name": "Tweed Heads"},
        "South East Queensland",
    ],
    "address": {
        "@type": "PostalAddress",
        "addressRegion": "QLD",
        "addressCountry": "AU",
    },
    "description": (
        "Colorbond metal roofing, wall cladding, gutters, box gutters, "
        "penetrations and repairs from Brisbane to the Sunshine Coast."
    ),
    "knowsAbout": [
        "Colorbond roofing",
        "Metal roof installation",
        "Roof repairs",
        "Box gutters",
        "Wall cladding",
    ],
}


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    """items: list of (name, absolute url path starting with /)"""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": SITE + path if path.startswith("/") else path,
            }
            for i, (name, path) in enumerate(items)
        ],
    }


def faq_schema(pairs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


def extract_faqs(html: str) -> list[tuple[str, str]]:
    pairs = []
    for m in re.finditer(
        r"<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>",
        html,
        flags=re.I | re.S,
    ):
        q = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        a = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        q = re.sub(r"\s+", " ", q)
        a = re.sub(r"\s+", " ", a)
        if q and a:
            pairs.append((q, a))
    return pairs


def extract_title_desc(html: str) -> tuple[str, str]:
    t = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    d = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        re.I | re.S,
    )
    title = re.sub(r"\s+", " ", t.group(1)).strip() if t else BRAND
    desc = d.group(1).strip() if d else ""
    # unescape common entities for meta re-use (keep as-is for HTML entities in title)
    return title, desc


def replace_head(html: str, new_inner: str) -> str:
    """Replace everything inside <head>...</head>."""
    return re.sub(
        r"<head\b[^>]*>.*?</head>",
        "<head>\n    " + new_inner + "\n</head>",
        html,
        count=1,
        flags=re.I | re.S,
    )


def ensure_nav_tools(html: str, tools_href: str) -> str:
    """Insert Tools link before About if missing."""
    if re.search(r">Tools</a>|>Tools &amp; Calculators</a>", html, re.I):
        return html

    # Landing nav (index): plain anchors
    if 'class="landing-nav"' in html:
        html = re.sub(
            r'(<nav class="landing-nav"[^>]*>.*?)(<a href="[^"]*about\.html">About</a>)',
            rf'\1<a href="{tools_href}">Tools</a>\n            \2',
            html,
            count=1,
            flags=re.I | re.S,
        )
        return html

    # Standard nav: insert before About
    html = re.sub(
        r'(<nav class="nav"[^>]*>)(.*?)(<a href="[^"]*about\.html">About</a>)',
        lambda m: m.group(1)
        + m.group(2)
        + f'<a href="{tools_href}">Tools</a>\n                '
        + m.group(3),
        html,
        count=1,
        flags=re.I | re.S,
    )
    return html


def ensure_footer_tools(html: str, tools_href: str) -> str:
    if "tools/" in html and "Roofing tools" in html:
        return html
    # Add under service areas column free inspection link area
    html = re.sub(
        r'(<a href="[^"]*contact\.html">Free inspection</a>)',
        rf'\1\n                <a href="{tools_href}">Roofing tools &amp; calculators</a>',
        html,
        count=1,
        flags=re.I,
    )
    # Contact/about short footers without Free inspection
    if "Roofing tools" not in html:
        html = re.sub(
            r'(<div><h4>Areas</h4>.*?)(</div>\s*</div>\s*<div class="legal">)',
            rf'\1<a href="{tools_href}">Tools &amp; calculators</a>\n            \2',
            html,
            count=1,
            flags=re.I | re.S,
        )
    return html


def page_path_to_canonical(rel: Path) -> str:
    s = rel.as_posix()
    if s == "index.html":
        return "/"
    return "/" + s


def infer_breadcrumbs(rel: Path) -> list[tuple[str, str]]:
    parts = rel.parts
    crumbs = [("Home", "/")]
    if parts[0] == "services":
        crumbs.append(("Services", "/#services"))
        name = rel.stem.replace("-", " ").title()
        crumbs.append((name, page_path_to_canonical(rel)))
    elif parts[0] == "areas":
        crumbs.append(("Areas", "/#areas"))
        name = rel.stem.replace("-", " ").title()
        crumbs.append((name, page_path_to_canonical(rel)))
    elif parts[0] == "tools":
        crumbs.append(("Tools", "/tools/"))
        if rel.name != "index.html":
            name = rel.stem.replace("-", " ").title()
            crumbs.append((name, page_path_to_canonical(rel)))
    elif rel.name == "about.html":
        crumbs.append(("About", "/about.html"))
    elif rel.name == "contact.html":
        crumbs.append(("Contact", "/contact.html"))
    return crumbs


HEADER_NAV = """    <div class="sale-bar"><strong>STORM SEASON:</strong> Free roof inspection + up to 15% off repairs — Brisbane to Sunshine Coast · <a href="tel:{phone_tel}">{phone}</a></div>
    <header class="site-header">
        <div class="header-inner">
            <a class="brand" href="{home}">
                <img src="{prefix}assets/logo.svg" alt="{brand}" width="44" height="44" class="brand-mark">
                <span class="brand-text">Roofing Brisbane</span>
            </a>
            <nav class="nav" aria-label="Main">
                <details class="dropdown">
                    <summary>Services</summary>
                    <div class="dropdown-menu">
                        <a href="{prefix}services/colorbond-roofing.html">Colorbond Roofing</a>
                        <a href="{prefix}services/roof-repairs.html">Roof Repairs</a>
                        <a href="{prefix}services/roof-replacement.html">Roof Replacement</a>
                        <a href="{prefix}services/gutters-and-box-gutters.html">Gutters &amp; Box Gutters</a>
                        <a href="{prefix}services/wall-cladding.html">Wall Cladding</a>
                        <a href="{prefix}services/roof-penetrations.html">Roof Penetrations</a>
                    </div>
                </details>
                <details class="dropdown">
                    <summary>Areas</summary>
                    <div class="dropdown-menu">
                        <a href="{prefix}areas/brisbane.html">Brisbane</a>
                        <a href="{prefix}areas/sunshine-coast.html">Sunshine Coast</a>
                        <a href="{prefix}areas/gold-coast-tweed.html">Gold Coast &amp; Tweed</a>
                    </div>
                </details>
                <a href="{prefix}tools/">Tools</a>
                <a href="{prefix}about.html">About</a>
                <a href="{prefix}contact.html">Contact</a>
                <a class="nav-cta" href="tel:{phone_tel}">Call {phone}</a>
            </nav>
        </div>
    </header>
"""

FOOTER = """    <footer class="site-footer">
        <div class="footer-inner">
            <div>
                <h4>{brand}</h4>
                <p>Colorbond metal roofing, cladding, gutters and repairs across South East Queensland — Brisbane to the Sunshine Coast and northern Gold Coast / Tweed corridor.</p>
                <p style="margin-top:12px"><a href="tel:{phone_tel}">{phone}</a></p>
                <p><a href="mailto:{email}">{email}</a></p>
            </div>
            <div>
                <h4>Services</h4>
                <a href="{prefix}services/colorbond-roofing.html">Colorbond Roofing</a>
                <a href="{prefix}services/roof-repairs.html">Roof Repairs</a>
                <a href="{prefix}services/roof-replacement.html">Roof Replacement</a>
                <a href="{prefix}services/gutters-and-box-gutters.html">Gutters &amp; Box Gutters</a>
                <a href="{prefix}services/wall-cladding.html">Wall Cladding</a>
                <a href="{prefix}services/roof-penetrations.html">Roof Penetrations</a>
            </div>
            <div>
                <h4>Resources</h4>
                <a href="{prefix}tools/">Roofing tools &amp; calculators</a>
                <a href="{prefix}areas/brisbane.html">Brisbane</a>
                <a href="{prefix}areas/sunshine-coast.html">Sunshine Coast</a>
                <a href="{prefix}areas/gold-coast-tweed.html">Gold Coast &amp; Tweed</a>
                <a href="{prefix}contact.html">Free inspection</a>
            </div>
        </div>
        <div class="legal">© 2026 {brand} · Queensland Roofing Services · Serving SEQ residential &amp; light commercial</div>
    </footer>
"""


def shell(prefix: str) -> tuple[str, str]:
    home = f"{prefix}index.html" if prefix else "index.html"
    hdr = HEADER_NAV.format(
        phone=PHONE,
        phone_tel=PHONE_TEL,
        home=home,
        prefix=prefix,
        brand=BRAND,
    )
    ftr = FOOTER.format(
        brand=BRAND,
        phone=PHONE,
        phone_tel=PHONE_TEL,
        email=EMAIL,
        prefix=prefix,
    )
    return hdr, ftr


TOOLS = [
    {
        "slug": "roof-area-calculator",
        "title": "Roof Area Calculator | Plan Size + Pitch to m² | Roofing Brisbane",
        "h1": "Roof Area Calculator",
        "desc": "Free roof area calculator: convert building plan length, width and pitch into roof surface m² for Colorbond and metal roofing quotes in SEQ.",
        "icon": "📐",
        "card": "Estimate roof surface area from plan dimensions and pitch — essential before sheet or cost estimates.",
        "keywords": "roof area calculator, roof m2 calculator, roof pitch area",
        "body": """
        <p class="lede">Enter the <strong>plan (footprint) length and width</strong> of the roof and the <strong>pitch in degrees</strong>. We convert that to approximate roof surface area, with optional waste for hips and valleys.</p>
        <div class="calc-layout">
          <div class="calc-form" id="ra-form">
            <div class="field-row">
              <div class="field"><label for="ra-length">Plan length (m)</label><input id="ra-length" type="number" min="0" step="0.1" placeholder="e.g. 12"></div>
              <div class="field"><label for="ra-width">Plan width (m)</label><input id="ra-width" type="number" min="0" step="0.1" placeholder="e.g. 8"></div>
            </div>
            <div class="field"><label for="ra-pitch">Pitch (degrees)</label><input id="ra-pitch" type="number" min="0" max="79" step="0.5" value="22.5" placeholder="e.g. 22.5"></div>
            <label class="check-row"><input type="checkbox" id="ra-complex"> Complex roof (hips/valleys) — add ~12% waste</label>
            <p class="calc-error" id="ra-error"></p>
            <button type="button" class="cta" id="ra-calc">Calculate roof area</button>
          </div>
          <div class="calc-result" id="ra-result" hidden>
            <h3>Results</h3>
            <dl>
              <dt>Plan area</dt><dd id="ra-plan">—</dd>
              <dt>Pitch factor</dt><dd id="ra-factor">—</dd>
              <dt>Roof surface</dt><dd id="ra-surface" class="calc-big">—</dd>
              <dt>Order allowance</dt><dd id="ra-order">—</dd>
            </dl>
            <p class="calc-note">Surface area uses plan × 1/cos(pitch). Always confirm with a site measure before ordering materials.</p>
          </div>
        </div>
        <div class="disclaimer-box"><strong>Planning estimate only.</strong> Skylights, verandahs, multi-level planes and unusual geometry need professional measure. <a href="../contact.html">Book a free inspection</a> across Brisbane to the Sunshine Coast.</div>
        <h2 style="margin-top:32px">Why roof area matters</h2>
        <p>Sheet counts, insulation, screws and ballpark quotes all start from <strong>roof surface m²</strong>, not just the house floor plan. A 22.5° pitch increases surface area by about 8% versus flat; steeper roofs rise further.</p>
        <p>Next: use the <a href="roof-sheet-calculator.html">sheet quantity calculator</a> or <a href="roof-cost-estimator.html">cost estimator</a>.</p>
        """,
    },
    {
        "slug": "roof-sheet-calculator",
        "title": "Roof Sheet Calculator | Colorbond Sheet Quantity | Roofing Brisbane",
        "h1": "Roof Sheet Quantity Calculator",
        "desc": "Estimate how many Colorbond or metal roof sheets you need from roof area, effective cover width and sheet length. Free SEQ planning tool.",
        "icon": "📄",
        "card": "Convert roof m² into an approximate Colorbond / metal sheet count with waste allowance.",
        "keywords": "colorbond sheet calculator, how many roof sheets, metal roof sheet quantity",
        "body": """
        <p class="lede">Use your <strong>roof surface area</strong>, the sheet’s <strong>effective cover width</strong> (not overall width) and typical <strong>sheet length</strong> to estimate order quantities.</p>
        <div class="calc-layout">
          <div class="calc-form">
            <div class="field"><label for="sh-area">Roof surface area (m²)</label><input id="sh-area" type="number" min="0" step="0.1" placeholder="e.g. 180"></div>
            <div class="field-row">
              <div class="field"><label for="sh-cover">Effective cover width (mm)</label><input id="sh-cover" type="number" min="0" step="1" value="762" placeholder="e.g. 762"></div>
              <div class="field"><label for="sh-length">Sheet length (m)</label><input id="sh-length" type="number" min="0" step="0.1" value="6" placeholder="e.g. 6"></div>
            </div>
            <div class="field"><label for="sh-waste">Waste / cut allowance (%)</label><input id="sh-waste" type="number" min="0" max="40" step="1" value="10"></div>
            <p class="calc-error" id="sh-error"></p>
            <button type="button" class="cta" id="sh-calc">Calculate sheets</button>
          </div>
          <div class="calc-result" id="sh-result" hidden>
            <h3>Results</h3>
            <dl>
              <dt>Coverage per sheet</dt><dd id="sh-sheet-area">—</dd>
              <dt>Sheets (net)</dt><dd id="sh-net">—</dd>
              <dt>Order quantity</dt><dd id="sh-total" class="calc-big">—</dd>
            </dl>
            <p class="calc-note">Effective cover width varies by profile (corrugated, trimdek-style, etc.). Confirm with your supplier’s data sheet.</p>
          </div>
        </div>
        <div class="disclaimer-box">Sheet lengths are often custom-cut. Ridge, barge and valley flashings are ordered separately. Need supply &amp; install? <a href="../services/colorbond-roofing.html">Colorbond roofing</a>.</div>
        <h2 style="margin-top:32px">Common cover widths</h2>
        <ul class="check-list">
          <li>Many corrugated-style sheets: ~760–775 mm effective cover</li>
          <li>Trapezoidal / decking profiles: check manufacturer (often 700–820 mm)</li>
          <li>Always use <em>effective cover</em>, not overall sheet width including side lap</li>
        </ul>
        """,
    },
    {
        "slug": "gutter-size-calculator",
        "title": "Gutter Size Calculator | Roof Drainage Estimator Australia | Roofing Brisbane",
        "h1": "Gutter Size Calculator",
        "desc": "Free gutter size calculator for Australian homes: estimate runoff from roof catchment and rainfall intensity, plus indicative downpipe counts for SEQ storms.",
        "icon": "🌧️",
        "card": "Size gutters and downpipes from roof catchment and design rainfall — built for SEQ storm planning.",
        "keywords": "gutter size calculator, downpipe calculator, roof drainage calculator australia",
        "body": """
        <p class="lede">SEQ summer storms push domestic gutters hard. This tool estimates <strong>runoff flow</strong> from catchment area and rainfall intensity, then suggests a <strong>gutter class</strong> and downpipe count (indicative only).</p>
        <div class="calc-layout">
          <div class="calc-form">
            <div class="field"><label for="gu-area">Roof catchment to this gutter (m²)</label><input id="gu-area" type="number" min="0" step="0.1" placeholder="e.g. 60"></div>
            <div class="field"><label for="gu-intensity">Design rainfall intensity (mm/h)</label><input id="gu-intensity" type="number" min="0" step="1" value="150" placeholder="e.g. 150"></div>
            <div class="field"><label for="gu-run">Gutter run length (m) — optional</label><input id="gu-run" type="number" min="0" step="0.1" placeholder="e.g. 12"></div>
            <p class="calc-error" id="gu-error"></p>
            <button type="button" class="cta" id="gu-calc">Calculate drainage</button>
          </div>
          <div class="calc-result" id="gu-result" hidden>
            <h3>Results</h3>
            <dl>
              <dt>Estimated peak flow</dt><dd id="gu-flow">—</dd>
              <dt>Suggested gutter</dt><dd id="gu-suggest">—</dd>
              <dt>Downpipes</dt><dd id="gu-downpipes" class="calc-big">—</dd>
              <dt>Spacing hint</dt><dd id="gu-spacing">—</dd>
            </dl>
            <p class="calc-note">Not a hydraulic design certificate. Box gutters and large catchments need engineering. Default 150 mm/h is a planning figure — local design rainfall may differ.</p>
          </div>
        </div>
        <div class="disclaimer-box">Overflowing gutters often mean undersized profiles, blocked outlets or poor falls — not just “more downpipes”. See <a href="../services/gutters-and-box-gutters.html">gutters &amp; box gutters</a>.</div>
        <h2 style="margin-top:32px">SEQ tips</h2>
        <ul class="check-list">
          <li>Coastal debris and leaf litter reduce real-world capacity — plan maintenance</li>
          <li>Box gutters over living areas need correct sumps, overflows and freeboard</li>
          <li>Match downpipe discharge to stormwater, not over footings</li>
        </ul>
        """,
    },
    {
        "slug": "roof-cost-estimator",
        "title": "Roof Cost Estimator Australia | Colorbond Price per m² SEQ | Roofing Brisbane",
        "h1": "Roof Cost Estimator",
        "desc": "Ballpark Colorbond and metal roofing costs per m² for Brisbane and Sunshine Coast: repairs, re-sheet, full replacement, gutters and cladding ranges in AUD.",
        "icon": "💰",
        "card": "Rough AUD cost bands for repairs, re-sheet, full replacement, gutters and cladding in SEQ.",
        "keywords": "roof cost calculator australia, colorbond roof cost per m2, roof replacement cost brisbane",
        "body": """
        <p class="lede">Get a <strong>planning price band</strong> in Australian dollars for common metal roofing jobs. Figures are indicative SEQ ranges — final quotes need site inspection.</p>
        <div class="calc-layout">
          <div class="calc-form">
            <div class="field"><label for="co-area">Approximate area (m²)</label><input id="co-area" type="number" min="0" step="1" placeholder="e.g. 160"></div>
            <div class="field"><label for="co-job">Job type</label>
              <select id="co-job">
                <option value="repair">Targeted repairs</option>
                <option value="resheet">Re-sheet / Colorbond re-roof</option>
                <option value="replace" selected>Full roof replacement</option>
                <option value="gutters">Gutters &amp; downpipes (per m² roof)</option>
                <option value="cladding">Wall cladding (per m² wall)</option>
              </select>
            </div>
            <div class="field"><label for="co-storeys">Access / complexity</label>
              <select id="co-storeys">
                <option value="1" selected>Single storey, normal access</option>
                <option value="2">Two storey or limited access</option>
                <option value="complex">Complex / steep / difficult site</option>
              </select>
            </div>
            <p class="calc-error" id="co-error"></p>
            <button type="button" class="cta" id="co-calc">Estimate cost range</button>
          </div>
          <div class="calc-result" id="co-result" hidden>
            <h3>Indicative range</h3>
            <p id="co-type" style="color:#7dd3fc;font-weight:600;margin-bottom:8px"></p>
            <p class="calc-big" id="co-range">—</p>
            <p class="calc-note" id="co-note"></p>
          </div>
        </div>
        <div class="disclaimer-box">Not a fixed quote. Material colour, insulation, solar removal, structural fixes and storm damage change pricing. <a href="../contact.html">Request a free inspection</a> for an on-site figure.</div>
        <h2 style="margin-top:32px">What usually moves the price</h2>
        <ul class="check-list">
          <li>Storeys, pitch and fall protection requirements</li>
          <li>Strip-out of old tiles vs re-sheet over metal</li>
          <li>Custom flashings, box gutters and penetrations</li>
          <li>Coastal corrosion-resistant fasteners and detailing</li>
        </ul>
        """,
    },
    {
        "slug": "roof-pitch-converter",
        "title": "Roof Pitch Converter | Degrees, Ratio &amp; Percent | Roofing Brisbane",
        "h1": "Roof Pitch Converter",
        "desc": "Convert roof pitch between degrees, rise:run ratio and percent slope. Includes plan-to-surface area factor for metal roofing calculations.",
        "icon": "📶",
        "card": "Convert pitch between degrees, rise:run and percent — plus the area factor for material take-offs.",
        "keywords": "roof pitch calculator, roof pitch to degrees, roof slope converter",
        "body": """
        <p class="lede">Roofers and suppliers mix <strong>degrees</strong>, <strong>rise-over-run</strong> (e.g. 4:12) and <strong>percent slope</strong>. Convert between them and see the surface-area factor.</p>
        <div class="calc-layout">
          <div class="calc-form">
            <div class="field"><label for="pi-mode">Input type</label>
              <select id="pi-mode">
                <option value="deg" selected>Degrees</option>
                <option value="ratio">Rise : run</option>
                <option value="pct">Percent slope</option>
              </select>
            </div>
            <div class="field" id="pi-single-wrap">
              <label for="pi-input" id="pi-input-label">Pitch (degrees)</label>
              <input id="pi-input" type="number" min="0" step="0.1" value="22.5">
            </div>
            <div class="field-row" id="pi-ratio-wrap" hidden>
              <div class="field"><label for="pi-rise">Rise</label><input id="pi-rise" type="number" min="0" step="0.1" value="4"></div>
              <div class="field"><label for="pi-run">Run</label><input id="pi-run" type="number" min="0.1" step="0.1" value="12"></div>
            </div>
            <p class="calc-error" id="pi-error"></p>
            <button type="button" class="cta" id="pi-calc">Convert pitch</button>
          </div>
          <div class="calc-result" id="pi-result" hidden>
            <h3>Converted</h3>
            <dl>
              <dt>Degrees</dt><dd id="pi-deg">—</dd>
              <dt>Rise : run</dt><dd id="pi-ratio">—</dd>
              <dt>Percent</dt><dd id="pi-pct">—</dd>
              <dt>Area factor</dt><dd id="pi-factor" class="calc-big">—</dd>
            </dl>
            <p class="calc-note">Multiply plan area by the factor to approximate roof surface area on a single plane.</p>
          </div>
        </div>
        <div class="disclaimer-box">Minimum pitches depend on profile and manufacturer. Installing below recommended pitch risks leaks and warranty issues.</div>
        """,
    },
    {
        "slug": "screw-fastener-calculator",
        "title": "Roof Screw Calculator | Fastener Quantity for Metal Roofing | Roofing Brisbane",
        "h1": "Roof Screw &amp; Fastener Calculator",
        "desc": "Estimate metal roofing screw quantities from roof area, purlin spacing and ribs per sheet. Free fastener calculator for Colorbond installs in SEQ.",
        "icon": "🔩",
        "card": "Estimate screw counts from area, purlin spacing and fixings across the sheet cover width.",
        "keywords": "roof screw calculator, metal roof fasteners, how many screws for colorbond",
        "body": """
        <p class="lede">Metal roofs are fixed on a grid: along the sheet (purlin/batten spacing) and across the cover (which ribs get a screw). This estimates <strong>total screws</strong> with a waste pack allowance.</p>
        <div class="calc-layout">
          <div class="calc-form">
            <div class="field"><label for="sc-area">Roof surface area (m²)</label><input id="sc-area" type="number" min="0" step="0.1" placeholder="e.g. 180"></div>
            <div class="field-row">
              <div class="field"><label for="sc-spacing">Purlin / fixing spacing (mm)</label><input id="sc-spacing" type="number" min="1" step="1" value="900"></div>
              <div class="field"><label for="sc-cover">Effective cover width (mm)</label><input id="sc-cover" type="number" min="1" step="1" value="762"></div>
            </div>
            <div class="field-row">
              <div class="field"><label for="sc-ribs">Screws across each sheet</label><input id="sc-ribs" type="number" min="1" step="1" value="4"></div>
              <div class="field"><label for="sc-waste">Extra allowance (%)</label><input id="sc-waste" type="number" min="0" max="30" value="10"></div>
            </div>
            <p class="calc-error" id="sc-error"></p>
            <button type="button" class="cta" id="sc-calc">Calculate fasteners</button>
          </div>
          <div class="calc-result" id="sc-result" hidden>
            <h3>Results</h3>
            <dl>
              <dt>Density</dt><dd id="sc-density">—</dd>
              <dt>Total screws</dt><dd id="sc-total" class="calc-big">—</dd>
              <dt>Packs (~100)</dt><dd id="sc-packs">—</dd>
            </dl>
            <p class="calc-note">Use Class 4 or coastal-rated fasteners where specified. Cyclone regions and manufacturer patterns may require denser fixing.</p>
          </div>
        </div>
        <div class="disclaimer-box">Always follow the profile manufacturer’s fixing pattern and engineer requirements. Wrong screws cause corrosion and sheet chatter. <a href="../services/colorbond-roofing.html">Talk to us about installs</a>.</div>
        """,
    },
]


def write_tool_page(tool: dict) -> None:
    tools_dir = ROOT / "tools"
    tools_dir.mkdir(exist_ok=True)
    prefix = "../"
    hdr, ftr = shell(prefix)
    path = f"/tools/{tool['slug']}.html"
    crumbs = breadcrumb_schema(
        [("Home", "/"), ("Tools", "/tools/"), (tool["h1"], path)]
    )
    webapp = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": tool["h1"],
        "url": SITE + path,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "AUD"},
        "description": tool["desc"],
        "provider": {"@id": f"{SITE}/#business"},
    }
    head = seo_head(
        title=tool["title"],
        description=tool["desc"],
        canonical_path=path,
        prefix=prefix,
        extra_jsonld=[ORG_SCHEMA, crumbs, webapp],
    )
    html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
    {head}
</head>
<body>
{hdr}
<main>
    <section class="page-hero">
        <div class="container">
            <p class="breadcrumb"><a href="../index.html">Home</a> · <a href="./">Tools</a> · {tool["h1"]}</p>
            <h1>{tool["h1"]}</h1>
        </div>
    </section>
    <section class="section">
        <div class="container prose">
            {tool["body"]}
            <p style="margin-top:28px"><a class="btn btn-outline" href="./">← All roofing tools</a>
            &nbsp; <a class="btn" href="../contact.html">Free inspection</a></p>
        </div>
    </section>
    <section class="cta-band">
        <h2>Planning a roof in Brisbane or on the Coast?</h2>
        <p>Use the calculators for ballparks, then get a site measure for materials that fit your home.</p>
        <a class="btn" href="tel:{PHONE_TEL}">Call {PHONE}</a>
    </section>
</main>
{ftr}
<script src="../js/calculators.js"></script>
</body>
</html>
"""
    out = tools_dir / f"{tool['slug']}.html"
    out.write_text(html, encoding="utf-8")
    print("Wrote", out.relative_to(ROOT))


def write_tools_index() -> None:
    prefix = "../"
    hdr, ftr = shell(prefix)
    cards = []
    for t in TOOLS:
        cards.append(
            f"""            <a class="tool-card" href="{t['slug']}.html">
                <div class="tool-icon" aria-hidden="true">{t['icon']}</div>
                <h3>{t['h1']}</h3>
                <p>{t['card']}</p>
                <span class="more">Open calculator →</span>
            </a>"""
        )
    item_list = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Roofing Tools & Calculators",
        "url": f"{SITE}/tools/",
        "description": "Free roofing calculators for area, sheets, gutters, cost, pitch and fasteners — for SEQ homeowners planning Colorbond installs and upgrades.",
        "isPartOf": {"@type": "WebSite", "url": f"{SITE}/"},
        "about": {"@id": f"{SITE}/#business"},
    }
    crumbs = breadcrumb_schema([("Home", "/"), ("Tools", "/tools/")])
    head = seo_head(
        title="Roofing Tools & Calculators | Free Planning Tools SEQ | Roofing Brisbane",
        description="Free roofing calculators for Brisbane & Sunshine Coast: roof area, Colorbond sheet quantity, gutter size, cost estimator, pitch converter and screw calculator.",
        canonical_path="/tools/",
        prefix=prefix,
        extra_jsonld=[ORG_SCHEMA, crumbs, item_list],
    )
    # For GitHub Pages, tools/index.html is served at /tools/ and /tools/index.html
    html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
    {head}
</head>
<body>
{hdr}
<main>
    <section class="page-hero">
        <div class="container">
            <p class="breadcrumb"><a href="../index.html">Home</a> · Tools &amp; Calculators</p>
            <h1>Roofing Tools &amp; Calculators</h1>
            <p class="lede">Free planning tools for homeowners and renovators across South East Queensland. Estimate roof area, sheet counts, gutter sizing, ballpark costs, pitch conversions and fastener quantities before you book a measure.</p>
        </div>
    </section>
    <section class="section">
        <div class="container">
            <div class="tools-grid">
{chr(10).join(cards)}
            </div>
            <div class="disclaimer-box" style="margin-top:28px">
                <strong>Estimates only.</strong> These tools help you plan and compare options. They are not engineering certificates or fixed quotes.
                For Colorbond installs, repairs and replacements from Brisbane to the Sunshine Coast, <a href="../contact.html">book a free inspection</a>.
            </div>
        </div>
    </section>
    <section class="section alt">
        <div class="container prose">
            <h2>Popular searches these tools answer</h2>
            <ul class="check-list">
                <li>How many m² of roofing do I need for my house?</li>
                <li>How many Colorbond sheets for my roof?</li>
                <li>What size gutter for Queensland storm rain?</li>
                <li>Rough cost to replace a metal roof in Brisbane?</li>
                <li>Convert roof pitch from degrees to rise-over-run</li>
                <li>How many roofing screws per m²?</li>
            </ul>
            <p>Pair tools with our service pages: <a href="../services/colorbond-roofing.html">Colorbond roofing</a>,
            <a href="../services/roof-replacement.html">roof replacement</a>,
            <a href="../services/gutters-and-box-gutters.html">gutters &amp; box gutters</a>.</p>
        </div>
    </section>
    <section class="cta-band">
        <h2>Ready for real numbers on your roof?</h2>
        <p>Calculators get you close. A site visit locks materials, flashings and price.</p>
        <a class="btn" href="tel:{PHONE_TEL}">Call {PHONE}</a>
        &nbsp;
        <a class="btn btn-outline" style="border-color:#fff;color:#fff!important" href="../contact.html">Book inspection</a>
    </section>
</main>
{ftr}
</body>
</html>
"""
    (ROOT / "tools" / "index.html").write_text(html, encoding="utf-8")
    print("Wrote tools/index.html")


def patch_existing_pages() -> None:
    html_files = [
        p
        for p in ROOT.rglob("*.html")
        if "node_modules" not in p.parts and "tools" not in p.parts
    ]
    for path in sorted(html_files):
        rel = path.relative_to(ROOT)
        prefix = rel_prefix(path)
        html = path.read_text(encoding="utf-8")
        title, desc = extract_title_desc(html)
        if not desc:
            desc = (
                "Colorbond metal roofing, cladding, gutters and repairs "
                "from Brisbane to the Sunshine Coast."
            )

        canon = page_path_to_canonical(rel)
        jsonld: list = []

        # Home: rich org + website
        if rel.name == "index.html" and rel.parent == ROOT:
            jsonld.append(ORG_SCHEMA)
            jsonld.append(
                {
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "@id": f"{SITE}/#website",
                    "url": f"{SITE}/",
                    "name": BRAND,
                    "alternateName": "Brisbane Roofing Services",
                    "publisher": {"@id": f"{SITE}/#business"},
                    "inLanguage": "en-AU",
                }
            )
        else:
            jsonld.append(ORG_SCHEMA)
            crumbs = infer_breadcrumbs(rel)
            if len(crumbs) > 1:
                jsonld.append(breadcrumb_schema(crumbs))

        faqs = extract_faqs(html)
        if faqs:
            jsonld.append(faq_schema(faqs))

        # Keep Service schema bits if present in old JSON-LD for service pages
        if rel.parts and rel.parts[0] == "services":
            jsonld.append(
                {
                    "@context": "https://schema.org",
                    "@type": "Service",
                    "name": re.sub(r"\s*\|\s*.*$", "", title),
                    "provider": {"@id": f"{SITE}/#business"},
                    "areaServed": [
                        "Brisbane",
                        "Sunshine Coast",
                        "Gold Coast",
                        "Tweed Heads",
                        "South East Queensland",
                    ],
                    "description": desc,
                    "url": SITE + canon,
                }
            )

        if rel.name == "contact.html":
            jsonld.append(
                {
                    "@context": "https://schema.org",
                    "@type": "ContactPage",
                    "name": "Contact Roofing Brisbane",
                    "url": f"{SITE}/contact.html",
                    "mainEntity": {"@id": f"{SITE}/#business"},
                }
            )

        head = seo_head(
            title=title,
            description=desc,
            canonical_path=canon,
            prefix=prefix,
            geo=(rel.name == "index.html"),
            extra_jsonld=jsonld,
        )
        html2 = replace_head(html, head)
        tools_href = f"{prefix}tools/"
        html2 = ensure_nav_tools(html2, tools_href)
        html2 = ensure_footer_tools(html2, tools_href)

        # Index: add tools section if missing
        if rel.name == "index.html" and 'id="tools"' not in html2:
            tools_section = """
        <section class="section" id="tools">
            <div class="container">
                <h2>Roofing tools &amp; calculators</h2>
                <p class="muted">Free planning tools people search for before a Colorbond install or upgrade — area, sheets, gutters, costs, pitch and fasteners.</p>
                <div class="grid-3">
                    <a class="card" href="tools/roof-area-calculator.html"><h3>Roof area calculator</h3><p>Plan size + pitch → roof surface m² for material take-offs.</p><span class="more">Open tool →</span></a>
                    <a class="card" href="tools/roof-sheet-calculator.html"><h3>Sheet quantity</h3><p>Estimate Colorbond / metal sheets from area and cover width.</p><span class="more">Open tool →</span></a>
                    <a class="card" href="tools/roof-cost-estimator.html"><h3>Cost estimator</h3><p>SEQ ballpark AUD ranges for repairs, re-sheet and replacement.</p><span class="more">Open tool →</span></a>
                </div>
                <p style="margin-top:18px"><a class="btn btn-outline" href="tools/">See all calculators</a></p>
            </div>
        </section>
"""
            html2 = html2.replace(
                '        <section class="cta-band">\n            <h2>Need a roofer',
                tools_section
                + '        <section class="cta-band">\n            <h2>Need a roofer',
                1,
            )

        # Landing nav tools link for index
        if rel.name == "index.html":
            html2 = ensure_nav_tools(html2, "tools/")

        path.write_text(html2, encoding="utf-8")
        print("Patched", rel.as_posix())


def write_sitemap() -> None:
    urls = [
        ("/", 1.0, "weekly"),
        ("/about.html", 0.6, "monthly"),
        ("/contact.html", 0.8, "monthly"),
        ("/tools/", 0.9, "weekly"),
    ]
    for t in TOOLS:
        urls.append((f"/tools/{t['slug']}.html", 0.85, "monthly"))
    for s in [
        "colorbond-roofing",
        "roof-repairs",
        "roof-replacement",
        "gutters-and-box-gutters",
        "wall-cladding",
        "roof-penetrations",
    ]:
        urls.append((f"/services/{s}.html", 0.9, "monthly"))
    for a in ["brisbane", "sunshine-coast", "gold-coast-tweed"]:
        urls.append((f"/areas/{a}.html", 0.9, "monthly"))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, prio, freq in urls:
        loc = SITE + path
        lines.append(
            f"  <url><loc>{loc}</loc><changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
        )
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote sitemap.xml")


def main() -> None:
    write_tools_index()
    for t in TOOLS:
        write_tool_page(t)
    patch_existing_pages()
    write_sitemap()
    print("Done.")


if __name__ == "__main__":
    main()
