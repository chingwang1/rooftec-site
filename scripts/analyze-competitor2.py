import re
from pathlib import Path

t = Path(__file__).with_name("competitor-bundle.js").read_text(encoding="utf-8", errors="ignore")

# Find UI labels more carefully - often in JSX as children strings after >
labels = re.findall(r">(Roof[^<]{0,40}|Get [^<]{0,40}|Select [^<]{0,40}|Add [^<]{0,40}|Include [^<]{0,40}|Estimated[^<]{0,40}|Total[^<]{0,40}|Price[^<]{0,40}|Cost[^<]{0,40}|Colour[^<]{0,40}|Color[^<]{0,40}|Profile[^<]{0,40}|Storey[^<]{0,40}|Story[^<]{0,40}|Pitch[^<]{0,40}|Gutter[^<]{0,40}|Insulation[^<]{0,40}|Sarking[^<]{0,40}|Remove[^<]{0,40}|Finance[^<]{0,40}|Quote[^<]{0,40}|m²[^<]{0,20}|sqm[^<]{0,20})", t, re.I)
print("HTML-ish labels:")
for s in sorted(set(labels))[:100]:
    print(" ", s)

# quoted short titles
print("\nQuoted UI:")
for s in re.findall(r'"(Roof [^"]{2,60}|Get [^"]{2,60}|Select [^"]{2,60}|Add [^"]{2,60}|Include [^"]{2,60}|Estimated [^"]{2,60}|Total [^"]{2,60}|Price [^"]{2,60}|Cost [^"]{2,60}|Colour[^"]{0,40}|Profile[^"]{0,40}|Storey[^"]{0,40}|Pitch[^"]{0,40}|Gutter[^"]{0,40}|Insulation[^"]{0,40}|Sarking[^"]{0,40}|Remove[^"]{0,40}|Quote[^"]{0,40}|Build[^"]{0,40}|Customise[^"]{0,40}|Customize[^"]{0,40}|m2[^"]{0,20}|per m[^"]{0,20})"', t):
    print(" ", s)

# Find colour names and hex
print("\nColour-like:")
for s in re.findall(r'"(?:name|label|id)":"([^"]+)"|"([A-Z][a-z]+(?: [A-Z][a-z]+)+)"', t)[:50]:
    pass

# extract bg colours array near LE colours
idx = t.find("colours")
print("\ncolours contexts:")
for m in re.finditer(r"colours?[:\[]", t):
    snip = t[m.start() : m.start() + 200]
    if any(c.isalpha() for c in snip):
        print(snip[:180].replace("\n", " "))
        print("---")

# look for pricing constants
print("\nnumeric arrays / rates:")
for m in re.finditer(r"(?:base|rate|price|cost|multiplier|factor)[A-Za-z]*\s*[:=]\s*[\d\.\{]", t, re.I):
    print(t[m.start() : m.start() + 100])

# profile names already found
print("\nProfile mentions:")
for name in ["Trimdek", "Corrugated", "Kliplok", "Custom Orb", "Spandek", "Longline", "Surfimist", "Monument", "Woodland", "Shale", "Dune", "Paperbark", "Surfmist", "Ironstone", "Basalt", "Night Sky", "Deep Ocean"]:
    if name.lower() in t.lower() or name in t:
        print(" ", name, t.lower().count(name.lower()))

# extract all Title Case multiword strings 2-4 words
cands = re.findall(r'"([A-Z][a-zA-Z]+(?: [A-Za-z0-9+/&-]{1,20}){0,4})"', t)
interesting = []
for s in cands:
    if len(s) < 4:
        continue
    if any(k in s.lower() for k in ["roof", "gutter", "quote", "price", "size", "colour", "color", "profile", "single", "double", "storey", "pitch", "remove", "metal", "tile", "insulation", "sarking", "flash", "down", "fascia", "ridge", "valley", "solar", "access", "scaff", "estimate", "total", "build", "option", "add", "finance", "include", "exclude", "complex", "simple", "area", "width", "length"]):
        interesting.append(s)
print("\nInteresting title strings:")
for s in sorted(set(interesting)):
    print(" ", s)

# Find dollar amounts
print("\nDollar amounts:")
print(sorted(set(re.findall(r"\$\d[\d,]*(?:\.\d+)?", t)))[:50])
print("raw numbers 50-400 that might be $/m2:")
nums = [int(x) for x in re.findall(r"\b(\d{2,3})\b", t) if 40 <= int(x) <= 400]
from collections import Counter
print(Counter(nums).most_common(30))
