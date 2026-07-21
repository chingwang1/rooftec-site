import re
from pathlib import Path

p = Path(__file__).with_name("competitor-bundle.js")
t = p.read_text(encoding="utf-8", errors="ignore")
print("len", len(t))

strs = re.findall(r'"([^"\\]{3,140})"', t)
strs += re.findall(r"'([^'\\]{3,140})'", t)

keywords = (
    "price",
    "colorbond",
    "roof",
    "gutter",
    "pitch",
    "storey",
    "m2",
    "m²",
    "insulation",
    "profile",
    "corrugat",
    "trimdek",
    "klip",
    "sheet",
    "cost",
    "quote",
    "material",
    "sarking",
    "valley",
    "ridge",
    "remove",
    "tile",
    "metal",
    "finance",
    "area",
    "width",
    "length",
    "colour",
    "color",
    "base",
    "fastener",
    "screw",
    "flashing",
    "downpipe",
    "fascia",
    "barge",
    "waste",
    "complex",
    "single",
    "double",
    "storeys",
    "stories",
    "sqm",
    "square",
    "estimate",
    "total",
    "option",
    "addon",
    "add-on",
    "scaffolding",
    "access",
    "solar",
    "skylight",
)

seen = set()
out = []
for s in strs:
    low = s.lower()
    if any(k in low for k in keywords):
        if s not in seen:
            seen.add(s)
            out.append(s)

print("--- relevant strings ---")
for s in out[:250]:
    print(s)
print("total relevant", len(out))

# numeric-looking price rates
nums = re.findall(r"(?:price|rate|cost|per)[^0-9]{0,20}(\d{2,4}(?:\.\d+)?)", t, re.I)
print("near-price numbers sample", nums[:40])

# object-like rate maps
for pat in [
    r"basePrice[^,]{0,80}",
    r"pricePer[^,]{0,80}",
    r"perSqm[^,]{0,80}",
    r"perM2[^,]{0,80}",
    r"\$\{[^}]{0,60}\}",
]:
    ms = re.findall(pat, t, re.I)
    if ms:
        print(pat, "->", ms[:15])
