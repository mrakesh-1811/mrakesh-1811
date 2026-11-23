from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

# Keep avatar.png beside this script. It can be your original photo.
INPUT = 'avatar.png'
OUTPUT = 'rakesh_scanner.gif'
W, H = 480, 600
FRAMES = 36
CHARS = ['·', '.', ':', '+', '*', '#', '@']

photo = Image.open(INPUT).convert('RGB')
# Crop to a portrait composition and fit the canvas.
ratio = max(W / photo.width, H / photo.height)
photo = photo.resize((int(photo.width * ratio), int(photo.height * ratio)), Image.Resampling.LANCZOS)
x0 = (photo.width - W) // 2
y0 = (photo.height - H) // 2
photo = photo.crop((x0, y0, x0 + W, y0 + H)).convert('L')
# Smooth detail and darken slightly for neon-symbol contrast.
photo = photo.filter(ImageFilter.GaussianBlur(0.8))

font = ImageFont.load_default()
cols, rows = 70, 88
cell_w, cell_h = W / cols, H / rows
random.seed(1811)
# Precompute ASCII density, but use the original grayscale photo to preserve the silhouette.
levels = []
for r in range(rows):
    row = []
    for c in range(cols):
        val = photo.getpixel((int((c + .5) * cell_w), int((r + .5) * cell_h)))
        density = int((255 - val) / 255 * (len(CHARS)-1))
        row.append(CHARS[max(0, min(len(CHARS)-1, density))])
    levels.append(row)

frames = []
for f in range(FRAMES):
    base = Image.new('RGB', (W, H), (5, 7, 18))
    draw = ImageDraw.Draw(base)
    scan_y = int((f / (FRAMES-1)) * H)
    # Symbol portrait with violet-to-cyan palette and scan illumination.
    for r in range(rows):
        yy = int(r * cell_h)
        for c in range(cols):
            ch = levels[r][c]
            if ch in ['·', '.'] and random.random() < 0.08:
                continue
            xx = int(c * cell_w)
            # Density drives visibility; scan beam adds light near its position.
            gray = photo.getpixel((min(W-1, xx), min(H-1, yy)))
            if gray > 218 and ch in ['·', '.']:
                continue
            scanboost = max(0, 1 - abs(yy - scan_y) / 85)
            t = c / cols
            rcol = int(105 + 95 * t + 30 * scanboost)
            gcol = int(30 + 175 * (1-t) + 45 * scanboost)
            bcol = int(210 + 40 * (1-t))
            intensity = max(0.3, (255-gray)/255)
            color = (int(min(255,rcol*intensity)), int(min(255,gcol*intensity)), int(min(255,bcol*intensity)))
            draw.text((xx, yy), ch, font=font, fill=color)
    # Thin moving scan line and soft glow.
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle((0, scan_y-5, W, scan_y+5), fill=(40, 210, 255, 38))
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    base = Image.alpha_composite(base.convert('RGBA'), glow)
    d = ImageDraw.Draw(base)
    d.line((0, scan_y, W, scan_y), fill=(65, 220, 255, 170), width=1)
    # Decorative frame and title footer.
    d.rounded_rectangle((12, 12, W-12, H-12), radius=20, outline=(100, 65, 255, 150), width=2)
    d.text((22, H-42), 'M RAKESH  |  AI & ML', font=font, fill=(130, 215, 255, 220))
    d.text((W-142, 22), 'SCAN // 1811', font=font, fill=(160, 90, 255, 210))
    frames.append(base.convert('RGB'))

frames[0].save(OUTPUT, save_all=True, append_images=frames[1:], duration=65, loop=0, optimize=True)
print(f'Created {OUTPUT}')
