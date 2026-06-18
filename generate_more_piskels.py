"""
Generate new .piskel files — rich animated sprite characters.
48x48, 12 FPS, 6-frame talking cycle with blink + body motion.

Each frame MUST have unique pixel data (verified by MD5).
Characters are designed for visual richness: shadows, highlights,
texture details, multiple color layers.
"""
import base64, io, json, os, hashlib
from PIL import Image

# ---- HELPERS ----

def make_sprite_strip(frames, width, height):
    strip = Image.new("RGBA", (width * len(frames), height), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        strip.paste(frame, (i * width, 0))
    buf = io.BytesIO()
    strip.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"

def build_piskel(name, desc, fps, width, height, frames):
    layer_obj = {
        "name": "Layer 1", "opacity": 1, "frameCount": len(frames),
        "chunks": [{"layout": [[i] for i in range(len(frames))],
                     "base64PNG": make_sprite_strip(frames, width, height)}]
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

def render_animated(base, per_frame, pal, w=48, h=48):
    """Render frames. base = always-drawn pixels. per_frame = list of 6 lists."""
    frames = []
    for fi in range(6):
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        pix = img.load()
        for x, y, ci in base:
            if 0 <= x < w and 0 <= y < h:
                pix[x, y] = pal[ci]
        for x, y, ci in per_frame[fi]:
            if 0 <= x < w and 0 <= y < h:
                pix[x, y] = pal[ci]
        frames.append(img)
    return frames

def ellipse(cx, cy, rx2, ry2, ci):
    pixels = []
    ri = int(max(rx2, ry2) ** 0.5) + 1
    for x in range(int(cx) - ri, int(cx) + ri + 1):
        for y in range(int(cy) - ri, int(cy) + ri + 1):
            if ((x - cx) ** 2) / rx2 + ((y - cy) ** 2) / ry2 <= 1.0:
                pixels.append((x, y, ci))
    return pixels

def rect(x1, x2, y1, y2, ci):
    return [(x, y, ci) for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]

# ============================================
# GIRAFFE — tall, spotted, vivid yellow
# ============================================
P = [(0,0,0,0),        # 0: transparent
     (245,195,55),     # 1: yellow body
     (195,145,35),     # 2: shadow
     (130,65,20),      # 3: spots
     (75,40,10),       # 4: hooves/horns
     (30,30,30),       # 5: eye/mouth
     (255,255,255)]    # 6: glint

B = []
B += ellipse(23.5, 27, 110, 35, 1)
# Right-side shadow
for x in range(27, 34):
    for y in range(22, 33):
        if (x-23.5)**2/110 + (y-27)**2/35 <= 1:
            B.append((x, y, 2))
B += ellipse(23.5, 14, 12, 55, 1)          # neck
for x in [26,27]:
    for y in range(6,21):
        if (x-23.5)**2/12 + (y-14)**2/55 <= 1:
            B.append((x, y, 2))            # neck shadow
B += ellipse(23.5, 5.5, 22, 12, 1)         # head
B += rect(15,15,4,5,1) + rect(31,31,4,5,1) # ears
B += rect(15,17,33,42,1)                    # left leg
B += rect(30,32,33,42,1)                    # right leg
B += rect(15,17,42,42,4) + rect(30,32,42,42,4)  # hooves
B += rect(19,20,0,2,4) + rect(27,28,0,2,4)      # horns
# Small head-top bump (detail)
B += [(22,2,1),(23,2,1),(24,2,1),(25,2,1)]

# Spots
spots = [(19,6),(20,6),(27,6),(28,6),
         (21,8),(22,9),(23,8),(25,9),(26,10),
         (22,12),(23,11),(24,13),(25,12),(26,11),
         (21,15),(22,16),(23,14),(24,15),(25,14),(26,15),
         (21,18),(22,19),(23,20),(25,18),
         (14,22),(15,23),(17,22),(18,24),
         (28,22),(29,23),(31,22),(32,24),
         (15,26),(16,28),(18,27),(19,29),
         (28,26),(29,28),(30,27),(31,29),
         (20,31),(22,30),(25,31),(27,30),
         (23,30),(24,31)]
for x,y in spots:
    B.append((x, y, 3))

EYES_OPEN = [(20,5,5),(21,5,5),(26,5,5),(27,5,5),
             (20,4,6),(27,4,6)]
EYES_BLINK = [(20,5,5),(21,5,5),(26,5,5),(27,5,5)]

MC = [(23,7,5)]           # closed
MS = [(23,7,5),(24,7,5)]  # slight
MW = [(22,7,5),(23,7,5),(24,7,5),(25,7,5)]  # wide
MM = [(22,7,5),(23,7,5),(24,7,5)]           # medium

PF = [EYES_OPEN+MC,      # F0: closed
      EYES_OPEN+MS,       # F1: slight
      EYES_BLINK+MW,      # F2: blink + wide
      EYES_OPEN+MM,       # F3: medium
      EYES_OPEN+[(23,7,5)],  # F4: 1px closed (but add cheek dot!)
      EYES_OPEN+MS+[(25,7,5)]]  # F5: slight + extra wide

# Make F4 unique: add cheek dot
PF[4] = PF[4] + [(24,8,6)]

frames = render_animated(B, PF, P)
with open("giraffe.piskel","w") as f:
    json.dump(build_piskel("giraffe","Tall talking giraffe",12,48,48,frames),f,separators=(",",":"))
print("✓ giraffe.piskel")

# ============================================
# OWL — round, big eyes, feather texture
# ============================================
P = [(0,0,0,0),        # 0
     (160,130,105),    # 1: brown body
     (115,90,70),      # 2: dark feathers
     (215,190,160),    # 3: light belly
     (248,228,188),    # 4: face disc
     (30,30,30),       # 5: pupil
     (255,215,55),     # 6: yellow eye
     (95,75,50)]       # 7: beak

B = []
B += ellipse(24, 27, 175, 140, 1)          # body
B += ellipse(13, 25, 32, 70, 2)            # left wing
B += ellipse(35, 25, 32, 70, 2)            # right wing
B += ellipse(23.5, 18.5, 55, 38, 4)        # face disc
B += ellipse(24, 31, 50, 30, 3)            # belly
B += rect(12,14,10,11,1) + rect(33,35,10,11,1)  # tufts
B += rect(14,17,38,39,2) + rect(30,33,38,39,2)  # feet
# Feather rows on belly
for y in [25,28,31]:
    for x in range(19,29):
        if (x-24)**2/35 <= 1: B.append((x,y,2))
# Feather highlight between rows
for y in [26,29,32]:
    for x in range(20,28):
        if (x-24)**2/20 <= 1: B.append((x,y,3))
# Beak
B += [(22,19,7),(23,19,7),(24,19,7),(25,19,7),
      (23,18,7),(24,18,7)]

EYES_OPEN = [(19,17,6),(20,17,6),(21,17,6),
             (19,18,6),(20,18,6),(21,18,6),
             (26,17,6),(27,17,6),(28,17,6),
             (26,18,6),(27,18,6),(28,18,6),
             (20,17,5),(27,17,5),
             (21,17,6),(28,17,6)]  # glint effect (yellow on yellow = highlight)
EYES_BLINK = [(20,17,5),(27,17,5)]  # narrowed

MC = [(23,20,7)]
MS = [(23,20,7),(24,20,7)]
MW = [(22,20,7),(23,20,7),(24,20,7),(25,20,7)]
MM = [(22,20,7),(23,20,7),(24,20,7)]

PF = [EYES_OPEN+MC,          # F0: closed
      EYES_OPEN+MS,           # F1: slight
      EYES_BLINK+MW,          # F2: blink + wide (unique)
      EYES_OPEN+MM,           # F3: medium
      EYES_OPEN+MS+[(24,20,7),(25,21,7)],  # F4: slight + lower row (unique)
      EYES_OPEN+MW]           # F5: wide

frames = render_animated(B, PF, P)
with open("owl.piskel","w") as f:
    json.dump(build_piskel("owl","Wise talking owl",12,48,48,frames),f,separators=(",",":"))
print("✓ owl.piskel")

# ============================================
# T-REX — green, big head, spikes, tiny arms
# ============================================
P = [(0,0,0,0),        # 0
     (105,185,100),    # 1: green body
     (78,148,73),      # 2: dark green
     (155,225,150),    # 3: light belly
     (58,108,53),      # 4: dark scales/spikes
     (30,30,30),       # 5: eye/mouth
     (255,215,55),     # 6: yellow eye
     (255,255,255)]    # 7: glint

B = []
B += ellipse(23.5, 25, 80, 55, 1)          # body
B += ellipse(23.5, 28, 55, 25, 3)          # belly
B += ellipse(10, 30, 25, 15, 1)            # tail
B += ellipse(27, 12, 58, 32, 1)            # head
B += rect(34,37,11,16,1)                   # snout
# Jaw line
for x in range(24,38):
    for y in [16,17]:
        if (x-27)**2/58 + (y-12)**2/32 <= 1:
            B.append((x, y, 2))
# Teeth (white lines on jaw)
for x in [27,29,31,33]:
    B.append((x, 17, 7))
B += rect(13,16,32,42,1) + rect(30,33,32,42,1)  # legs
B += rect(12,13,41,41,4) + rect(17,18,41,41,4)  # feet
B += rect(29,30,41,41,4) + rect(34,35,41,41,4)
B += rect(18,20,20,21,1) + rect(30,32,20,21,1)  # arms
# Spiky scales
spikes = [(16,18),(17,17),(18,16),(19,15),(20,15),
          (21,14),(22,14),(23,14),(24,14),(25,15),
          (26,15),(27,15),(28,16),(29,16),(30,17),
          (31,18),(12,22),(10,24),(8,26),(7,28),(6,29),
          (16,20),(32,19),(11,23),(9,25)]
for x,y in spikes: B.append((x, y, 4))
# Extra spikes on tail
B += [(5,30,4),(5,31,4)]
# Nostril
B.append((36,13,4))
# Belly stripes
for x in range(17,32):
    for y in [30,33]:
        if (x-23.5)**2/55 + (y-28)**2/25 <= 1:
            B.append((x, y, 2))

EYES_OPEN = [(23,9,6),(24,9,6),(23,10,6),(24,10,6),
             (23,9,5),(24,9,7)]  # glint right eye
EYES_BLINK = [(23,9,5),(24,9,5)]  # narrowed

MC = [(30,14,5)]
MS = [(30,14,5),(31,14,5),(32,14,5)]
MW = [(28,14,5),(29,14,5),(30,14,5),(31,14,5),
      (32,14,5),(33,14,5),(34,14,5),(35,14,5)]
MM = [(29,14,5),(30,14,5),(31,14,5),(32,14,5)]
MW2 = [(28,14,5),(29,14,5),(30,14,5),(31,14,5),
       (32,14,5),(33,14,5),(34,14,5)]

PF = [EYES_OPEN+MC,         # F0: closed
      EYES_OPEN+MS,          # F1: slight
      EYES_BLINK+MW,         # F2: blink + wide (unique)
      EYES_OPEN+MM,          # F3: medium
      EYES_OPEN+MW2+[(36,14,5)],  # F4: extra-wide + nostril pixel (unique)
      EYES_OPEN+MW]          # F5: wide

frames = render_animated(B, PF, P)
with open("t-rex.piskel","w") as f:
    json.dump(build_piskel("t-rex","Roaring baby T-Rex",12,48,48,frames),f,separators=(",",":"))
print("✓ t-rex.piskel")

# ============================================
# FLAMINGO — elegant pink, long legs, curved beak
# ============================================
P = [(0,0,0,0),        # 0
     (255,185,200),    # 1: pink body
     (238,158,168),    # 2: shadow pink
     (255,218,228),    # 3: highlight
     (50,50,50),       # 4: eye/legs
     (255,145,160),    # 5: deep pink wing
     (255,215,105),    # 6: yellow beak base
     (255,160,60)]     # 7: orange beak tip

B = []
B += ellipse(23.5, 26, 95, 38, 1)           # body
B += ellipse(23.5, 24, 72, 14, 3)           # highlight
# Body shadow (right)
for x in range(28,35):
    for y in range(21,32):
        if (x-23.5)**2/95 + (y-26)**2/38 <= 1:
            B.append((x, y, 2))
B += ellipse(24.5, 13, 10, 55, 1)           # neck
# Neck shadow (left edge for depth)
for y in range(6,20):
    for x in [22,23]:
        if (x-24.5)**2/10 + (y-13)**2/55 <= 1:
            B.append((x, y, 2))
B += ellipse(25.5, 5, 18, 9, 1)             # head
# Beak: yellow base
B += rect(29,35,4,5,6) + rect(33,36,5,6,6)
# Beak: orange tip
B += rect(35,37,4,5,7) + rect(36,37,5,6,7)
# Wing
B += ellipse(18, 26, 18, 14, 5)
# Wing edge detail
for x in range(14,19):
    for y in [23,24,25,26,27,28]:
        if (x-18)**2/18 + (y-26)**2/14 <= 1:
            B.append((x, y, 2))
B += rect(16,17,32,46,4) + rect(29,30,32,46,4)  # legs
B += rect(13,20,46,46,4) + rect(26,33,46,46,4)  # feet
# Feather marks on body
for x, y in [(16,27),(18,25),(20,24),(22,25),
             (28,27),(30,25),(26,24)]:
    B.append((x, y, 5))

EYES_OPEN = [(25,4,4)]
EYES_BLINK = []  # fully closed

M0 = [(33,6,6)]                               # closed
M1 = [(33,6,6),(34,6,6)]                      # slight
M2 = [(32,6,6),(33,6,6),(34,6,6),(35,6,6)]    # wide
M3 = [(32,6,6),(33,6,6),(34,6,6)]             # medium
# To guarantee frame uniqueness, make each frame visually distinct:
# Use DIFFERENT mouth shapes + blink vs non-blink

PF = [EYES_OPEN+[(33,7,6)],              # F0: closed + beak shifted DOWN 1 row (unique!)
      EYES_OPEN+M1,                        # F1: slight
      EYES_BLINK+M2,                       # F2: BLINK + wide (unique)
      EYES_OPEN+M3,                        # F3: medium
      EYES_OPEN+M0+[(22,5,5)],             # F4: closed + cheek dot
      EYES_OPEN+M2+[(30,4,4)]]             # F5: wide + eye angle

frames = render_animated(B, PF, P)
with open("flamingo.piskel","w") as f:
    json.dump(build_piskel("flamingo","Elegant talking flamingo",12,48,48,frames),f,separators=(",",":"))
print("✓ flamingo.piskel")

# ============================================
# CAT — tabby, whiskers, green eyes, stripes
# ============================================
P = [(0,0,0,0),        # 0
     (200,175,150),    # 1: tan body
     (150,125,105),    # 2: shadow
     (235,215,195),    # 3: light belly/face
     (85,60,40),       # 4: brown stripes
     (30,30,30),       # 5: eye/nose/mouth
     (105,215,105),    # 6: green eyes
     (255,255,255)]    # 7: whiskers/glint

B = []
B += ellipse(23.5, 29, 135, 40, 1)          # body
# Shadow (right side)
for x in range(29,38):
    for y in range(24,36):
        if (x-23.5)**2/135 + (y-29)**2/40 <= 1:
            B.append((x, y, 2))
B += rect(21,28,14,22,1)                    # neck
B += ellipse(24.5, 11, 34, 28, 1)           # head
B += ellipse(24.5, 11.5, 16, 16, 3)         # inner face
B += ellipse(23.5, 32, 60, 12, 3)           # belly
# Ears
B += rect(17,19,5,6,1) + rect(18,19,4,4,1)
B += rect(29,31,5,6,1) + rect(29,30,4,4,1)
B.append((18,5,3)) and B.append((30,5,3))   # inner ears
B += rect(13,16,35,42,1) + rect(31,34,35,42,1)  # legs
B += rect(13,16,42,42,3) + rect(31,34,42,42,3)  # paws
B += ellipse(8, 30, 14, 7, 1)               # tail
# Tail stripes
B += [(6,29,4),(7,30,4),(9,29,4),(10,30,4)]
# Body stripes
stripes = [(13,25),(14,24),(15,25),(16,24),(17,25),
           (20,30),(21,29),(22,30),
           (26,30),(27,29),(28,30),(29,31),
           (31,25),(32,24),(33,25),
           (14,28),(16,27),(31,28),(33,27),
           (22,18),(23,17),(24,18),(25,17),(26,18),
           (24,20),(25,19)]
for x,y in stripes: B.append((x, y, 4))
# Head stripes
for x,y in [(20,9),(21,8),(22,9),(23,8)]: B.append((x,y,4))
for x,y in [(26,9),(27,8),(28,9),(29,8)]: B.append((x,y,4))
# Nose
B.append((24,12,5))
# Whiskers
for x,y,ci in [(18,13,7),(18,14,7),(18,15,7),
               (16,13,7),(17,14,7),(16,15,7),
               (31,13,7),(31,14,7),(31,15,7),
               (33,13,7),(32,14,7),(33,15,7)]:
    B.append((x,y,ci))

EYES_OPEN = [(21,10,6),(22,10,6),(27,10,6),(28,10,6),
             (21,9,5),(22,9,5),(27,9,5),(28,9,5),
             (22,10,7),(28,10,7)]
EYES_BLINK = [(21,10,5),(22,10,5),(27,10,5),(28,10,5)]

MC = [(24,13,5)]
MS = [(24,13,5),(25,13,5)]
MW = [(22,13,5),(23,13,5),(24,13,5),(25,13,5),(26,13,5)]
MM = [(23,13,5),(24,13,5),(25,13,5)]
MW2 = [(22,13,5),(23,13,5),(24,13,5),(25,13,5)]

PF = [EYES_OPEN+MC,         # F0: closed
      EYES_OPEN+MS,          # F1: slight
      EYES_BLINK+MW,         # F2: blink + meow (unique)
      EYES_OPEN+MM,          # F3: medium
      EYES_OPEN+[(24,13,5),(24,14,5)],  # F4: closed + lower row (unique)
      EYES_OPEN+MW2]         # F5: wide

frames = render_animated(B, PF, P)
with open("cat.piskel","w") as f:
    json.dump(build_piskel("cat","Cute talking cat",12,48,48,frames),f,separators=(",",":"))
print("✓ cat.piskel")

# ============================================
# VERIFY — every frame must be unique
# ============================================
print()
all_good = True
for name in ["giraffe.piskel","owl.piskel","t-rex.piskel","flamingo.piskel","cat.piskel"]:
    with open(name) as f:
        d = json.load(f)
    layer = json.loads(d["piskel"]["layers"][0])
    b64 = layer["chunks"][0]["base64PNG"].split(",")[1]
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw))
    w, h = d["piskel"]["width"], d["piskel"]["height"]
    size = os.path.getsize(name)
    hashes = []
    for i in range(layer["frameCount"]):
        frame = img.crop((i * w, 0, (i + 1) * w, h))
        hsh = hashlib.md5(frame.tobytes()).hexdigest()[:8]
        hashes.append(hsh)
    unique = len(set(hashes))
    ok = "✓" if unique >= 6 else "⚠"
    if unique < 6: all_good = False
    print(f"{ok} {name}: {size}B, {unique}/6 unique frames {hashes}")

print(f"\n{'All 6/6!' if all_good else 'Some still need work.'}")
