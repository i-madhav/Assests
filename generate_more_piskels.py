"""
Generate new .piskel files in the style of llama-assest.piskel
All: 48x48, 12 FPS, 6-frame talking animation, animal silhouette.
"""
import base64, io, json, os
from PIL import Image

# ---- HELPERS ----

def make_sprite_strip(frames, width, height):
    strip = Image.new("RGBA", (width * len(frames), height), (0,0,0,0))
    for i, frame in enumerate(frames):
        strip.paste(frame, (i * width, 0))
    buf = io.BytesIO()
    strip.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def build_piskel(name, desc, fps, width, height, frames):
    png_data = make_sprite_strip(frames, width, height)
    layer_obj = {
        "name": "Layer 1", "opacity": 1, "frameCount": len(frames),
        "chunks": [{"layout": [[i] for i in range(len(frames))], "base64PNG": png_data}]
    }
    return {
        "modelVersion": 2,
        "piskel": {
            "name": name, "description": desc, "fps": fps,
            "height": height, "width": width,
            "layers": [json.dumps(layer_obj)],
            "hiddenFrames": []
        }
    }

def render(base_pixels, eye_pixels, mouth_frames, palette, width=48, height=48):
    frames = []
    for mouth in mouth_frames:
        img = Image.new("RGBA", (width, height), (0,0,0,0))
        pix = img.load()
        for x, y, ci in base_pixels:
            if 0 <= x < width and 0 <= y < height:
                pix[x, y] = palette[ci]
        for x, y, ci in eye_pixels:
            if 0 <= x < width and 0 <= y < height:
                pix[x, y] = palette[ci]
        for x, y, ci in mouth:
            if 0 <= x < width and 0 <= y < height:
                pix[x, y] = palette[ci]
        frames.append(img)
    return frames

# ============================================
# CHARACTER 1: GIRAFFE
# Tall + long-necked, same silhouette family as llama
# ============================================

giraffe_palette = [
    (0,0,0,0),       # 0: transparent
    (220,180,50),    # 1: yellow/orange body
    (180,140,30),    # 2: darker yellow shadow
    (100,70,20),     # 3: brown spots
    (60,40,10),      # 4: dark brown hooves/horns
    (30,30,30),      # 5: dark outline/eye
    (255,255,255),   # 6: white eye glint
]

giraffe_base = []
# Body (x=14→33, y=22→32)
for x in range(14, 34):
    for y in range(22, 33):
        giraffe_base.append((x, y, 1))
# Body highlight (top)
for x in range(15, 33):
    for y in [21]:
        giraffe_base.append((x, y, 2))
# Neck (x=20→27, y=8→21)
for x in range(20, 28):
    for y in range(8, 22):
        giraffe_base.append((x, y, 1))
# Neck highlight
for x in range(21, 27):
    for y in [7]:
        giraffe_base.append((x, y, 2))
# Head (x=17→30, y=3→9)
for x in range(17, 31):
    for y in range(3, 10):
        giraffe_base.append((x, y, 1))
# Head top
for x in range(18, 30):
    for y in [2]:
        giraffe_base.append((x, y, 2))
# Ears
for x in [16, 31]:
    for y in [4, 5]:
        giraffe_base.append((x, y, 1))
# Legs
for x in [15, 16, 17]:
    for y in range(33, 42):
        giraffe_base.append((x, y, 1))
for x in [30, 31, 32]:
    for y in range(33, 42):
        giraffe_base.append((x, y, 1))
# Hooves
for x in [15, 16, 17]:
    for y in [41]:
        giraffe_base.append((x, y, 4))
for x in [30, 31, 32]:
    for y in [41]:
        giraffe_base.append((x, y, 4))
# Horns (ossicones)
for x in [19, 20]:
    for y in [1, 2]:
        giraffe_base.append((x, y, 4))
for x in [27, 28]:
    for y in [1, 2]:
        giraffe_base.append((x, y, 4))
# Spots (brown patches)
spot_positions = [(21,8),(22,9),(23,8),(24,9),(25,10),(22,12),(23,13),
                  (21,15),(22,16),(25,11),(24,14),(26,15),(21,18),(22,19),
                  (24,17),(26,18),(23,20),(15,22),(18,23),(16,25),(19,24),
                  (30,22),(27,23),(29,25),(31,24),(16,28),(18,29),(30,28),(28,29)]
for x, y in spot_positions:
    giraffe_base.append((x, y, 3))

giraffe_eyes = [
    (20, 5, 5), (21, 5, 5),
    (26, 5, 5), (27, 5, 5),
    (20, 4, 6), (27, 4, 6),
]

giraffe_mouth = [
    [(23, 7, 5)],
    [(23, 7, 5), (24, 7, 5)],
    [(22, 7, 5), (23, 7, 5), (24, 7, 5), (25, 7, 5)],
    [(23, 7, 5), (24, 7, 5)],
    [(23, 7, 5)],
    [(22, 7, 5), (23, 7, 5), (24, 7, 5), (25, 7, 5)],
]

giraffe_frames = render(giraffe_base, giraffe_eyes, giraffe_mouth, giraffe_palette)
giraffe_piskel = build_piskel("giraffe", "Tall talking giraffe", 12, 48, 48, giraffe_frames)
with open("giraffe.piskel", "w") as f:
    json.dump(giraffe_piskel, f, separators=(",", ":"))
print("✓ giraffe.piskel created")

# ============================================
# CHARACTER 2: OWL
# ============================================

owl_palette = [
    (0,0,0,0),        # 0: transparent
    (140,120,100),    # 1: brown body
    (110,90,70),      # 2: dark brown wing/feathers
    (200,180,150),    # 3: light belly
    (240,220,180),    # 4: face disc
    (30,30,30),       # 5: dark eye
    (255,200,50),     # 6: yellow eyes
    (80,60,40),       # 7: beak
]

owl_base = []
for x in range(10, 38):
    for y in range(16, 39):
        dx = x - 23.5
        dy = y - 27
        if (dx*dx/180 + dy*dy/150) <= 1:
            owl_base.append((x, y, 1))
# Wings (darker)
for x in range(10, 14):
    for y in range(20, 35):
        if (x-23.5)*(x-23.5)/180 + (y-27)*(y-27)/150 <= 1:
            owl_base.append((x, y, 2))
for x in range(33, 38):
    for y in range(20, 35):
        if (x-23.5)*(x-23.5)/180 + (y-27)*(y-27)/150 <= 1:
            owl_base.append((x, y, 2))
# Face disc
for x in range(16, 31):
    for y in range(13, 24):
        dx = x - 23
        dy = y - 18
        if dx*dx + dy*dy <= 40:
            owl_base.append((x, y, 4))
# Belly
for x in range(18, 29):
    for y in range(25, 36):
        dx = x - 23.5
        dy = y - 30
        if dx*dx/40 + dy*dy/30 <= 1:
            owl_base.append((x, y, 3))
# Ear tufts
for x in [12, 13, 14]:
    for y in [10, 11]:
        owl_base.append((x, y, 1))
for x in [33, 34, 35]:
    for y in [10, 11]:
        owl_base.append((x, y, 1))
# Feet
for x in [14, 15, 16, 17]:
    for y in [38, 39]:
        owl_base.append((x, y, 2))
for x in [30, 31, 32, 33]:
    for y in [38, 39]:
        owl_base.append((x, y, 2))
# Feather details
for x in range(19, 28):
    for y in [27, 30, 33]:
        if (x-23.5)*(x-23.5)/40 + (y-30)*(y-30)/30 <= 1:
            owl_base.append((x, y, 2))

owl_eyes = [
    (19, 17, 6), (20, 17, 6), (21, 17, 6),
    (19, 18, 6), (20, 18, 6), (21, 18, 6),
    (25, 17, 6), (26, 17, 6), (27, 17, 6),
    (25, 18, 6), (26, 18, 6), (27, 18, 6),
    (20, 17, 5), (26, 17, 5),
]

# Beak (fixed)
for x in [23]:
    for y in [19]:
        owl_base.append((x, y, 7))

owl_mouth = [
    [(23, 20, 7)],
    [(23, 20, 7), (24, 20, 7)],
    [(22, 20, 7), (23, 20, 7), (24, 20, 7)],
    [(23, 20, 7), (24, 20, 7)],
    [(23, 20, 7)],
    [(22, 20, 7), (23, 20, 7), (24, 20, 7)],
]

owl_frames = render(owl_base, [], owl_mouth, owl_palette)
owl_piskel = build_piskel("owl", "Wise talking owl", 12, 48, 48, owl_frames)
with open("owl.piskel", "w") as f:
    json.dump(owl_piskel, f, separators=(",", ":"))
print("✓ owl.piskel created")

# ============================================
# CHARACTER 3: T-REX
# ============================================

dino_palette = [
    (0,0,0,0),         # 0: transparent
    (90,170,90),       # 1: green body
    (70,140,70),       # 2: dark green
    (140,210,140),     # 3: light belly
    (50,100,50),       # 4: dark scales
    (30,30,30),        # 5: eye
    (255,200,50),      # 6: yellow eye
]

dino_base = []
# Body
for x in range(14, 34):
    for y in range(18, 33):
        dx = x - 23.5
        dy = y - 25
        if (dx*dx/80 + dy*dy/60) <= 1:
            dino_base.append((x, y, 1))
# Tail
for x in range(5, 15):
    for y in range(25, 35):
        dx = x - 10
        dy = y - 30
        if dx*dx/25 + dy*dy/20 <= 1:
            dino_base.append((x, y, 1))
# Head
for x in range(18, 36):
    for y in range(6, 19):
        dx = x - 26.5
        dy = y - 12
        if dx*dx/60 + dy*dy/35 <= 1:
            dino_base.append((x, y, 1))
# Snout
for x in range(34, 38):
    for y in range(11, 16):
        dino_base.append((x, y, 1))
# Belly
for x in range(16, 32):
    for y in range(28, 32):
        dino_base.append((x, y, 3))
for x in range(7, 13):
    for y in range(29, 33):
        dino_base.append((x, y, 3))
# Legs
for x in [13, 14, 15, 16]:
    for y in range(32, 42):
        dino_base.append((x, y, 1))
for x in [30, 31, 32, 33]:
    for y in range(32, 42):
        dino_base.append((x, y, 1))
# Feet
for x in [12, 13, 17, 18]:
    for y in [41]:
        dino_base.append((x, y, 4))
for x in [29, 30, 34, 35]:
    for y in [41]:
        dino_base.append((x, y, 4))
# Tiny arms
for x in [18, 19, 20]:
    for y in [20, 21]:
        dino_base.append((x, y, 1))
for x in [30, 31, 32]:
    for y in [20, 21]:
        dino_base.append((x, y, 1))
# Spiky scales
spike_positions = [(16,18),(17,17),(19,17),(20,16),(22,16),(24,16),
                   (26,16),(28,17),(30,17),(31,18),(12,22),(10,24),
                   (8,26),(7,28)]
for x, y in spike_positions:
    dino_base.append((x, y, 4))
# Nostril
dino_base.append((36, 13, 4))

dino_eyes = [
    (23, 9, 6), (24, 9, 6),
    (23, 10, 6), (24, 10, 6),
    (23, 9, 5),
]

dino_mouth = [
    [(30, 14, 5)],
    [(30, 14, 5), (31, 14, 5), (32, 14, 5)],
    [(28, 14, 5), (29, 14, 5), (30, 14, 5),
     (31, 14, 5), (32, 14, 5), (33, 14, 5),
     (34, 14, 5), (35, 14, 5)],
    [(30, 14, 5), (31, 14, 5), (32, 14, 5)],
    [(30, 14, 5)],
    [(28, 14, 5), (29, 14, 5), (30, 14, 5),
     (31, 14, 5), (32, 14, 5), (33, 14, 5),
     (34, 14, 5), (35, 14, 5)],
]

dino_frames = render(dino_base, dino_eyes, dino_mouth, dino_palette)
dino_piskel = build_piskel("t-rex", "Roaring baby T-Rex", 12, 48, 48, dino_frames)
with open("t-rex.piskel", "w") as f:
    json.dump(dino_piskel, f, separators=(",", ":"))
print("✓ t-rex.piskel created")

# ============================================
# CHARACTER 4: FLAMINGO
# ============================================

flamingo_palette = [
    (0,0,0,0),         # 0: transparent
    (255,180,190),     # 1: pink body
    (230,150,160),     # 2: dark pink shadow
    (255,210,220),     # 3: light pink highlight
    (50,50,50),        # 4: dark eye/legs
    (255,130,150),     # 5: deep pink wing
    (255,200,100),     # 6: yellow beak base
    (255,150,50),      # 7: orange beak tip
]

flamingo_base = []
# Body
for x in range(12, 36):
    for y in range(20, 33):
        dx = x - 23.5
        dy = y - 26
        if dx*dx/100 + dy*dy/40 <= 1:
            flamingo_base.append((x, y, 1))
# Highlight
for x in range(14, 33):
    for y in range(21, 24):
        dx = x - 23.5
        if dx*dx/80 <= 1:
            flamingo_base.append((x, y, 3))
# Neck
for x in range(22, 29):
    for y in range(6, 21):
        dx = x - 24.5
        dy = y - 13
        if dx*dx/10 + dy*dy/60 <= 1:
            flamingo_base.append((x, y, 1))
# Neck shadow
for x in [22, 23]:
    for y in range(7, 20):
        flamingo_base.append((x, y, 2))
# Head
for x in range(21, 31):
    for y in range(2, 9):
        dx = x - 25.5
        dy = y - 5
        if dx*dx/18 + dy*dy/9 <= 1:
            flamingo_base.append((x, y, 1))
# Beak
for x in range(29, 35):
    for y in range(4, 6):
        flamingo_base.append((x, y, 6))
for x in range(33, 36):
    for y in range(5, 7):
        flamingo_base.append((x, y, 6))
for x in range(35, 37):
    for y in range(6, 8):
        flamingo_base.append((x, y, 6))
# Beak tip
for x in range(34, 37):
    for y in range(4, 6):
        flamingo_base.append((x, y, 7))
for x in range(36, 38):
    for y in range(5, 8):
        flamingo_base.append((x, y, 7))
# Wing
for x in range(14, 22):
    for y in range(22, 30):
        dx = x - 18
        dy = y - 26
        if dx*dx/16 + dy*dy/16 <= 1:
            flamingo_base.append((x, y, 5))
# Legs
for x in [16, 17]:
    for y in range(32, 46):
        flamingo_base.append((x, y, 4))
for x in [29, 30]:
    for y in range(32, 46):
        flamingo_base.append((x, y, 4))
# Feet
for x in range(13, 20):
    for y in [45]:
        flamingo_base.append((x, y, 4))
for x in range(26, 33):
    for y in [45]:
        flamingo_base.append((x, y, 4))

flamingo_eyes = [(25, 4, 4)]

flamingo_mouth = [
    [(33, 6, 6)],
    [(33, 6, 6), (34, 6, 6)],
    [(32, 6, 6), (33, 6, 6), (34, 6, 6), (35, 6, 6)],
    [(33, 6, 6), (34, 6, 6)],
    [(33, 6, 6)],
    [(32, 6, 6), (33, 6, 6), (34, 6, 6), (35, 6, 6)],
]

flamingo_frames = render(flamingo_base, flamingo_eyes, flamingo_mouth, flamingo_palette)
flamingo_piskel = build_piskel("flamingo", "Elegant talking flamingo", 12, 48, 48, flamingo_frames)
with open("flamingo.piskel", "w") as f:
    json.dump(flamingo_piskel, f, separators=(",", ":"))
print("✓ flamingo.piskel created")

# ============================================
# CHARACTER 5: CAT
# ============================================

cat_palette = [
    (0,0,0,0),         # 0: transparent
    (180,160,140),     # 1: tan/cream body
    (140,120,100),     # 2: darker tan
    (220,200,180),     # 3: light belly/face
    (80,60,40),        # 4: brown stripes
    (30,30,30),        # 5: eye/nose
    (100,200,100),     # 6: green eyes
    (255,255,255),     # 7: whisker
]

cat_base = []
# Body
for x in range(10, 38):
    for y in range(22, 36):
        dx = x - 23.5
        dy = y - 29
        if dx*dx/140 + dy*dy/40 <= 1:
            cat_base.append((x, y, 1))
# Neck
for x in range(21, 29):
    for y in range(14, 23):
        cat_base.append((x, y, 1))
# Head
for x in range(18, 32):
    for y in range(6, 17):
        dx = x - 24.5
        dy = y - 11
        if dx*dx/35 + dy*dy/28 <= 1:
            cat_base.append((x, y, 1))
# Inner face
for x in range(21, 28):
    for y in range(8, 15):
        dx = x - 24.5
        dy = y - 11.5
        if dx*dx/12 + dy*dy/15 <= 1:
            cat_base.append((x, y, 3))
# Belly
for x in range(14, 33):
    for y in range(31, 35):
        cat_base.append((x, y, 3))
# Ears
for x in [17, 18, 19]:
    for y in [5, 6]:
        cat_base.append((x, y, 1))
for x in [18, 19]:
    for y in [4]:
        cat_base.append((x, y, 1))
for x in [29, 30, 31]:
    for y in [5, 6]:
        cat_base.append((x, y, 1))
for x in [29, 30]:
    for y in [4]:
        cat_base.append((x, y, 1))
# Inner ears
for x in [18]:
    for y in [5]:
        cat_base.append((x, y, 3))
for x in [30]:
    for y in [5]:
        cat_base.append((x, y, 3))
# Legs
for x in [13, 14, 15, 16]:
    for y in range(35, 42):
        cat_base.append((x, y, 1))
for x in [31, 32, 33, 34]:
    for y in range(35, 42):
        cat_base.append((x, y, 1))
# Paws
for x in [13, 14, 15, 16]:
    for y in [41]:
        cat_base.append((x, y, 3))
for x in [31, 32, 33, 34]:
    for y in [41]:
        cat_base.append((x, y, 3))
# Tail
for x in range(4, 12):
    for y in range(28, 33):
        dx = x - 8
        dy = y - 30
        if dx*dx/16 + dy*dy/8 <= 1:
            cat_base.append((x, y, 1))
# Tail stripes
for x in [6, 7]:
    for y in [29, 30]:
        cat_base.append((x, y, 4))
for x in [9, 10]:
    for y in [29, 30]:
        cat_base.append((x, y, 4))
# Body stripes
stripe_positions = [(13,25),(14,24),(15,25),(16,24),(17,25),
                    (20,30),(21,29),(22,30),
                    (26,30),(27,29),(28,30),(29,31),
                    (31,25),(32,24),(33,25)]
for x, y in stripe_positions:
    cat_base.append((x, y, 4))

cat_eyes = [
    (21, 10, 6), (22, 10, 6),
    (27, 10, 6), (28, 10, 6),
    (21, 9, 5), (22, 9, 5),
    (27, 9, 5), (28, 9, 5),
    (21, 10, 7), (28, 10, 7),
]

# Nose
cat_base.append((24, 12, 5))

# Whiskers
whisker_left = [(18,13,7),(18,14,7),(18,15,7),(16,13,7),(17,14,7),(16,15,7)]
whisker_right = [(31,13,7),(31,14,7),(31,15,7),(33,13,7),(32,14,7),(33,15,7)]
for x, y, ci in whisker_left + whisker_right:
    cat_base.append((x, y, ci))

cat_mouth = [
    [(24, 13, 5)],
    [(23, 13, 5), (24, 13, 5)],
    [(22, 13, 5), (23, 13, 5), (24, 13, 5), (25, 13, 5), (26, 13, 5)],
    [(23, 13, 5), (24, 13, 5), (25, 13, 5)],
    [(24, 13, 5)],
    [(22, 13, 5), (23, 13, 5), (24, 13, 5), (25, 13, 5), (26, 13, 5)],
]

cat_frames = render(cat_base, cat_eyes, cat_mouth, cat_palette)
cat_piskel = build_piskel("cat", "Cute talking cat", 12, 48, 48, cat_frames)
with open("cat.piskel", "w") as f:
    json.dump(cat_piskel, f, separators=(",", ":"))
print("✓ cat.piskel created")

# ---- VERIFY ----
print()
for name in ["giraffe.piskel", "owl.piskel", "t-rex.piskel", "flamingo.piskel", "cat.piskel"]:
    size = os.path.getsize(name)
    with open(name) as f:
        d = json.load(f)
    layer = json.loads(d["piskel"]["layers"][0])
    print(f"  {name}: {size} bytes, {d['piskel']['width']}x{d['piskel']['height']}, "
          f"{layer['frameCount']} frames, {d['piskel']['fps']} FPS")
print("\nDone!")
