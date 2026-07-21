from PIL import Image, ImageDraw, ImageFont
import os
import shutil

assets = os.path.join(os.path.dirname(__file__), "..", "assets")
assets = os.path.abspath(assets)
src = os.path.join(assets, "carousel-colorbond-house.jpg")
im = Image.open(src).convert("RGB")

# OG 1200x630 cover crop
W, H = 1200, 630
sw, sh = im.size
scale = max(W / sw, H / sh)
nw, nh = int(sw * scale), int(sh * scale)
im2 = im.resize((nw, nh), Image.Resampling.LANCZOS)
left = (nw - W) // 2
top = max(0, (nh - H) // 2 - 40)
im2 = im2.crop((left, top, left + W, top + H))

overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for y in range(H // 2, H):
    a = int(180 * (y - H // 2) / (H // 2))
    od.line([(0, y), (W, y)], fill=(15, 26, 46, a))
for y in range(0, 90):
    a = int(120 * (1 - y / 90))
    od.line([(0, y), (W, y)], fill=(15, 26, 46, a))

base = im2.convert("RGBA")
out = Image.alpha_composite(base, overlay)
d = ImageDraw.Draw(out)


def font(size):
    for path in [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


f_title = font(52)
f_sub = font(28)
f_brand = font(22)

d.rounded_rectangle((40, 28, 420, 72), radius=10, fill=(196, 92, 38, 230))
d.text((58, 36), "BRISBANE ROOFING SERVICES", font=f_brand, fill=(255, 255, 255, 255))
d.text((48, 430), "Colorbond Roofing & Cladding", font=f_title, fill=(255, 255, 255, 255))
d.text((48, 500), "Brisbane to Sunshine Coast  ·  Free inspections", font=f_sub, fill=(232, 238, 245, 255))
d.text((48, 555), "brisbaneroofingservice.com", font=f_brand, fill=(125, 211, 252, 255))

og_path = os.path.join(assets, "og-default.jpg")
out.convert("RGB").save(og_path, "JPEG", quality=88, optimize=True)
print("Wrote", og_path, os.path.getsize(og_path))


def make_icon(size, path):
    icon = Image.new("RGBA", (size, size), (26, 43, 74, 255))
    dr = ImageDraw.Draw(icon)
    m = size
    pad = m * 0.12
    peak = (m / 2, pad)
    left_pt = (pad, m * 0.55)
    right_pt = (m - pad, m * 0.55)
    dr.line([left_pt, peak, right_pt], fill=(196, 92, 38, 255), width=max(2, size // 14))
    wx1, wx2 = m * 0.22, m * 0.78
    wy1, wy2 = m * 0.5, m * 0.82
    dr.rectangle([wx1, wy1, wx2, wy2], outline=(232, 238, 245, 255), width=max(2, size // 18))
    dw = m * 0.12
    dh = m * 0.2
    dx = m / 2 - dw / 2
    dr.rectangle([dx, wy2 - dh, dx + dw, wy2], fill=(196, 92, 38, 255))
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 6, fill=255)
    final = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    final.paste(icon, mask=mask)
    final.save(path, "PNG")
    print("Wrote", path)


make_icon(32, os.path.join(assets, "favicon-32.png"))
make_icon(180, os.path.join(assets, "apple-touch-icon.png"))
make_icon(192, os.path.join(assets, "icon-192.png"))
shutil.copyfile(os.path.join(assets, "logo.svg"), os.path.join(assets, "favicon.svg"))
print("done")
