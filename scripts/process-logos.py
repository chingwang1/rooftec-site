from PIL import Image
import os

src_dir = r"C:\Users\kyleh\.grok\sessions\C%3A%5CWINDOWS%5Csystem32\019f846d-f0fe-7871-9808-97ca3f428646\images"
out_dir = r"C:\Users\kyleh\Desktop\rooftec-site\assets"
os.makedirs(out_dir, exist_ok=True)


def remove_bg(path, mode="white", thresh=245):
    im = Image.open(path).convert("RGBA")
    pixels = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if mode == "white":
                if r > thresh and g > thresh and b > thresh:
                    pixels[x, y] = (r, g, b, 0)
                elif r > 230 and g > 230 and b > 230:
                    avg = (r + g + b) / 3
                    alpha = int(max(0, min(255, (255 - avg) * 8)))
                    pixels[x, y] = (r, g, b, alpha)
            else:
                if r < 25 and g < 25 and b < 25:
                    pixels[x, y] = (r, g, b, 0)
                elif r < 45 and g < 45 and b < 45:
                    avg = (r + g + b) / 3
                    alpha = int(min(255, avg * 8))
                    pixels[x, y] = (r, g, b, alpha)
    bbox = im.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        pad = 8
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(w, x1 + pad)
        y1 = min(h, y1 + pad)
        im = im.crop((x0, y0, x1, y1))
    return im


h = remove_bg(os.path.join(src_dir, "10.jpg"), "white", 240)
h.save(os.path.join(out_dir, "logo-horizontal.png"), "PNG")
print("horizontal", h.size)

s = remove_bg(os.path.join(src_dir, "11.jpg"), "white", 240)
s.save(os.path.join(out_dir, "logo-lockup.png"), "PNG")
print("lockup", s.size)

d = remove_bg(os.path.join(src_dir, "9.jpg"), "black", 30)
d.save(os.path.join(out_dir, "logo-lockup-dark.png"), "PNG")
print("dark", d.size)

chosen = r"C:\Users\kyleh\Desktop\rooftec-site\assets\logo-tests\00-CHOSEN-shield-wordmark-ref.png"
im = Image.open(chosen).convert("RGBA")
w, hgt = im.size
shield = im.crop((0, 0, int(w * 0.42), hgt))
px = shield.load()
sw, sh = shield.size
for y in range(sh):
    for x in range(sw):
        r, g, b, a = px[x, y]
        if r > 245 and g > 245 and b > 245:
            px[x, y] = (r, g, b, 0)
bb = shield.getbbox()
if bb:
    shield = shield.crop(bb)
shield.save(os.path.join(out_dir, "logo-shield.png"), "PNG")
print("shield", shield.size)
print("done")
