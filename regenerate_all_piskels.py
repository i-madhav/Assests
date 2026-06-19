#!/usr/bin/env python3
"""
Beautiful pixel art .piskel generator.
Every shape gets: auto-outline, 3-tone shading, rich palettes, character details.
48×48, 12 FPS, 6 unique frames.
"""

import base64, io, json, os, hashlib
from PIL import Image

W, H = 48, 48
FPS = 12
NFRAMES = 6
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ======================== HELPERS ========================

def strip(frames, w, h):
    s = Image.new("RGBA", (w * len(frames), h), (0,0,0,0))
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    b = io.BytesIO()
    s.save(b, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(b.getvalue()).decode('ascii')}"

def piskel(name, desc, fps, w, h, frames):
    lo = {"name": "Layer 1", "opacity": 1, "frameCount": len(frames),
          "chunks": [{"layout": [[i] for i in range(len(frames))],
                      "base64PNG": strip(frames, w, h)}]}
    return {"modelVersion": 2, "piskel": {"name": name, "description": desc, "fps": fps,
            "height": h, "width": w, "layers": [json.dumps(lo)], "hiddenFrames": []}}

def el(cx, cy, rx2, ry2, ci):
    """Filled ellipse."""
    r = int(max(rx2, ry2)**0.5) + 2
    return [(x, y, ci) for x in range(int(cx)-r, int(cx)+r+1)
            for y in range(int(cy)-r, int(cy)+r+1)
            if (x-cx)**2/max(rx2,0.01) + (y-cy)**2/max(ry2,0.01) <= 1]

def re(x1, x2, y1, y2, ci):
    """Filled rectangle."""
    return [(x, y, ci) for x in range(x1, x2+1) for y in range(y1, y2+1)]

def shaded_el(cx, cy, rx2, ry2, base_ci, hi_ci, shadow_ci):
    """Ellipse with 3-tone shading: highlight top-left, shadow bottom-right."""
    all_px = el(cx, cy, rx2, ry2, base_ci)
    mr = max(rx2, ry2)**0.5
    result = []
    for x, y, _ in all_px:
        diag = ((x - cx) / max(rx2**0.5, 1) + (y - cy) / max(ry2**0.5, 1)) / 2
        if diag < -0.35:
            result.append((x, y, hi_ci))
        elif diag > 0.35:
            result.append((x, y, shadow_ci))
        else:
            result.append((x, y, base_ci))
    return result

def shaded_re(x1, x2, y1, y2, base_ci, hi_ci, shadow_ci):
    """Rectangle with top highlight row and bottom shadow row."""
    result = []
    for x in range(x1, x2+1):
        for y in range(y1, y2+1):
            if y == y1 or y == y1+1:
                result.append((x, y, hi_ci))
            elif y >= y2-1:
                result.append((x, y, shadow_ci))
            else:
                result.append((x, y, base_ci))
    return result

def thick_neck(points, ci, width=4):
    """Draw a thick neck along control points."""
    px = []
    hw = width // 2
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        steps = max(abs(x2-x1), abs(y2-y1), 1) + 1
        for s in range(steps):
            t = s / steps
            cx = int(x1 + (x2-x1)*t)
            cy = int(y1 + (y2-y1)*t)
            for dx in range(-hw, hw+1):
                for dy in range(-1, 2):
                    px.append((cx+dx, cy+dy, ci))
    return px

def render_beautiful(base, per_frame, pal, w=W, h=H):
    """Render with auto-outline: darkens outer 1px of every shape for clean borders."""
    fr = []
    for fi in range(NFRAMES):
        im = Image.new("RGBA", (w, h), (0,0,0,0))
        px = im.load()

        # Pass 1: Draw all pixels
        all_pixels = base + per_frame[fi]
        for x, y, ci in all_pixels:
            if 0 <= x < w and 0 <= y < h:
                px[x, y] = pal[ci]

        # Pass 2: Auto-outline — darken outer edge pixels of every shape
        edges = set()
        for x in range(w):
            for y in range(h):
                if px[x, y][3] > 0:
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = x+dx, y+dy
                        if not (0 <= nx < w and 0 <= ny < h) or px[nx, ny][3] == 0:
                            edges.add((x, y))
                            break

        for x, y in edges:
            r, g, b, a = px[x, y]
            px[x, y] = (max(0, int(r*0.30)), max(0, int(g*0.30)), max(0, int(b*0.30)), a)

        fr.append(im)
    return fr

def write_piskel(filename, data):
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    return filepath

def verify(filename):
    filepath = os.path.join(SCRIPT_DIR, filename)
    with open(filepath) as f:
        d = json.load(f)
    layer = json.loads(d["piskel"]["layers"][0])
    b64 = layer["chunks"][0]["base64PNG"].split(",")[1]
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw))
    w, h = d["piskel"]["width"], d["piskel"]["height"]
    size = os.path.getsize(filepath)
    hashes = []
    for i in range(layer["frameCount"]):
        frame = img.crop((i * w, 0, (i + 1) * w, h))
        hashes.append(hashlib.md5(frame.tobytes()).hexdigest()[:8])
    unique = len(set(hashes))
    ok = "✓" if unique >= 6 else "⚠"
    print(f"  {ok} {filename}: {size}B, {unique}/{layer['frameCount']} unique frames")
    return unique >= 6


# ================================================================
# 1. OWL — FLYING CYCLE
# Rich warm brown palette with golden accents
# ================================================================
print("Building Owl...")

# Palette: warm browns, golden beak, cream face disc
P = [(0,0,0,0),
     (165,130,100,255),   # 1: body base (warm brown)
     (125,95,70,255),     # 2: body shadow (dark brown)
     (195,165,135,255),   # 3: body highlight (light tan)
     (245,230,200,255),   # 4: face disc (cream)
     (35,25,20,255),      # 5: eye dark
     (225,170,45,255),    # 6: beak/claw gold
     (100,75,50,255),     # 7: wing dark (chocolate)
     (255,250,240,255),   # 8: white highlight
     (185,150,50,255)]    # 9: beak shadow

B = []
# Body — shaded ellipse
B += shaded_el(24, 28, 140, 100, 1, 3, 2)
# Belly — lighter shaded
B += shaded_el(24, 31, 55, 35, 3, 4, 1)
# Face disc — bright oval with gradient
B += shaded_el(24, 18, 65, 45, 4, 8, 3)
# Ear tufts
B += re(12, 15, 9, 13, 2) + re(13, 14, 10, 12, 1)
B += re(33, 36, 9, 13, 2) + re(34, 35, 10, 12, 1)
# Feather chest markings (v-shaped chevrons)
for y in [25, 28, 31]:
    B += re(19, 29, y, y, 2)
    B += re(20, 28, y+1, y+1, 3)
# Feet — solid with claws
B += re(14, 18, 38, 41, 2) + re(30, 34, 38, 41, 2)
B += re(13, 19, 41, 42, 6) + re(29, 35, 41, 42, 6)  # golden claws
# Beak base — golden triangle
B += re(21, 27, 20, 21, 6)
B += re(22, 26, 22, 22, 6)
B += re(23, 25, 23, 23, 9)  # shadow under beak

# WINGS — shaded, thick
wing_up_L = (shaded_re(3, 8, 14, 16, 7, 2, 7) + shaded_re(5, 10, 17, 19, 2, 1, 7) +
             shaded_re(7, 12, 20, 22, 1, 3, 2) + re(9, 14, 23, 25, 1))
wing_up_R = (shaded_re(40, 45, 14, 16, 7, 2, 7) + shaded_re(38, 43, 17, 19, 2, 1, 7) +
             shaded_re(36, 41, 20, 22, 1, 3, 2) + re(34, 39, 23, 25, 1))

wing_mid_L = (shaded_re(4, 9, 22, 24, 7, 2, 7) + shaded_re(6, 11, 25, 27, 2, 1, 7) +
              shaded_re(8, 13, 28, 30, 1, 3, 2) + re(10, 14, 31, 32, 1))
wing_mid_R = (shaded_re(39, 44, 22, 24, 7, 2, 7) + shaded_re(37, 42, 25, 27, 2, 1, 7) +
              shaded_re(35, 40, 28, 30, 1, 3, 2) + re(34, 38, 31, 32, 1))

wing_dn_L = (shaded_re(3, 8, 28, 30, 7, 2, 7) + shaded_re(5, 10, 31, 33, 2, 1, 7) +
             shaded_re(7, 12, 34, 36, 1, 3, 2) + re(9, 14, 37, 38, 1))
wing_dn_R = (shaded_re(40, 45, 28, 30, 7, 2, 7) + shaded_re(38, 43, 31, 33, 2, 1, 7) +
             shaded_re(36, 41, 34, 36, 1, 3, 2) + re(34, 39, 37, 38, 1))

# Eyes — large expressive owl eyes with bright highlights
eyes_open  = (re(18, 21, 16, 18, 5) + re(27, 30, 16, 18, 5) +   # dark sockets
              [(19, 16, 6), (28, 16, 6)] +                         # iris gold
              [(20, 16, 8), (29, 16, 8)])                           # bright highlight dot!
eyes_half  = (re(18, 21, 17, 18, 5) + re(27, 30, 17, 18, 5) +
              [(20, 17, 6), (29, 17, 6)])
eyes_blink = (re(18, 21, 18, 18, 5) + re(27, 30, 18, 18, 5))

bk_c = []
bk_s = re(22, 26, 23, 24, 9)
bk_w = re(21, 27, 23, 25, 9) + re(22, 26, 25, 26, 6)

PF = [
    wing_dn_L + wing_dn_R + eyes_open + bk_c,
    wing_mid_L + wing_mid_R + eyes_half + bk_s,
    wing_up_L + wing_up_R + eyes_blink + bk_w,
    wing_dn_L + wing_dn_R + eyes_open + bk_s,
    wing_mid_L + wing_mid_R + eyes_open + bk_w,
    wing_up_L + wing_up_R + eyes_half + bk_c + re(12, 15, 9, 10, 6) + re(33, 36, 9, 10, 6),
]

frames = render_beautiful(B, PF, P)
write_piskel("owl.piskel", piskel("owl", "Flying owl with wing-flap cycle", FPS, W, H, frames))
print("  ✓ owl.piskel")


# ================================================================
# 2. T-REX — STOMP & ROAR
# Deep green palette with bright belly, fierce eyes
# ================================================================
print("Building T-Rex...")

P = [(0,0,0,0),
     (85,165,80,255),     # 1: green base
     (55,120,50,255),     # 2: green shadow
     (130,205,125,255),   # 3: green highlight
     (45,85,40,255),      # 4: dark green
     (30,30,25,255),      # 5: eye dark
     (230,200,50,255),    # 6: yellow eye
     (245,245,235,255),   # 7: white teeth
     (255,255,200,255),   # 8: bright
     (180,230,170,255)]   # 9: pale belly

B = []
B += shaded_el(24, 26, 120, 70, 1, 3, 2)    # body
B += shaded_el(24, 29, 65, 30, 9, 8, 3)     # pale belly
B += re(17, 31, 28, 28, 2) + re(18, 30, 31, 31, 2)  # belly stripes
B += shaded_el(30, 13, 80, 40, 1, 3, 2)     # head
B += shaded_re(34, 40, 10, 17, 1, 3, 2)     # snout
B += re(39, 40, 12, 13, 4)                   # nostril
B += re(26, 40, 17, 19, 2)                   # jaw line
for x in [28, 31, 34, 37]:
    B += re(x, x+1, 18, 19, 7)              # white teeth
B += shaded_re(14, 19, 33, 42, 1, 3, 2)     # left leg
B += shaded_re(29, 34, 33, 42, 1, 3, 2)     # right leg
B += re(12, 20, 42, 44, 4) + re(27, 35, 42, 44, 4)  # feet
for x in [12, 16, 20]: B.append((x, 45, 4))
for x in [27, 31, 35]: B.append((x, 45, 4))
# Spines
for x, y in [(18,17),(20,15),(22,14),(24,13),(26,14),(28,15)]:
    B += re(x, x+1, y, y+2, 4)
# Tail
B += shaded_el(12, 30, 40, 20, 1, 3, 2)
B += shaded_el(8, 31, 20, 10, 1, 3, 2)

tail_c = shaded_el(5, 31, 12, 8, 1, 3, 2)
tail_l = shaded_el(3, 30, 12, 8, 1, 3, 2)
tail_r = shaded_el(7, 32, 12, 8, 1, 3, 2)

arm_dn_L = shaded_re(20, 23, 21, 25, 1, 3, 2)
arm_dn_R = shaded_re(33, 36, 21, 25, 1, 3, 2)
arm_up_L = shaded_re(20, 23, 17, 21, 1, 3, 2)
arm_up_R = shaded_re(33, 36, 17, 21, 1, 3, 2)
arm_fw_L = shaded_re(18, 21, 19, 23, 1, 3, 2)
arm_fw_R = shaded_re(35, 38, 19, 23, 1, 3, 2)

jaw_c = []
jaw_s = re(28, 38, 19, 21, 4)
jaw_w = (re(26, 40, 19, 23, 4) + re(28, 38, 23, 25, 4) +
         re(28, 32, 20, 20, 7) + re(34, 38, 20, 20, 7))
jaw_m = re(27, 39, 19, 22, 4)

# Fierce yellow eyes with highlight
eyes_o = re(26, 28, 10, 12, 6) + [(27, 10, 5), (26, 10, 8)]
eyes_b = re(26, 28, 12, 12, 5)

PF = [
    arm_dn_L + arm_dn_R + eyes_o + jaw_c + tail_c,
    arm_up_L + arm_up_R + eyes_o + jaw_s + tail_r,
    arm_up_L + arm_up_R + eyes_b + jaw_w + tail_l + re(41, 43, 12, 16, 1),
    arm_fw_L + arm_fw_R + eyes_o + jaw_m + tail_c,
    arm_dn_L + arm_dn_R + eyes_b + jaw_s + tail_r,
    arm_up_L + arm_up_R + eyes_b + jaw_w + tail_l + re(41, 43, 12, 16, 1) + re(41, 43, 17, 20, 4),
]

frames = render_beautiful(B, PF, P)
write_piskel("t-rex.piskel", piskel("t-rex", "Stomping T-Rex with roar cycle", FPS, W, H, frames))
print("  ✓ t-rex.piskel")


# ================================================================
# 3. FLAMINGO — NECK SWAY & PECK
# Vibrant coral/hot pink, soft gradients
# ================================================================
print("Building Flamingo...")

P = [(0,0,0,0),
     (255,130,160,255),   # 1: coral pink base
     (220,90,125,255),    # 2: deep pink shadow
     (255,175,195,255),   # 3: light pink highlight
     (50,45,45,255),      # 4: dark legs/eye
     (255,75,115,255),    # 5: hot pink accent
     (255,195,65,255),    # 6: golden beak
     (240,140,40,255),    # 7: beak shadow
     (255,245,235,255),   # 8: white highlight
     (255,210,220,255)]   # 9: pale pink

B = []
B += shaded_el(24, 28, 120, 45, 1, 3, 2)     # body
B += shaded_el(22, 26, 50, 15, 3, 9, 1)      # highlight
B += shaded_el(20, 28, 30, 18, 5, 2, 5)      # wing accent
B += el(17, 27, 18, 10, 2)                    # wing detail
# Legs
B += re(18, 21, 34, 44, 4)
B += re(27, 30, 34, 44, 4)
B += re(16, 23, 44, 46, 4)
B += re(25, 32, 44, 46, 4)

# Thick necks with pink shading
neck_c  = thick_neck([(24,22),(24,18),(24,14),(24,10),(24,7)], 1) + thick_neck([(25,22),(25,18),(25,14),(25,10),(25,7)], 3)
neck_l  = thick_neck([(22,22),(21,18),(20,14),(21,10),(22,7)], 1) + thick_neck([(23,22),(22,18),(21,14),(22,10),(23,7)], 3)
neck_r  = thick_neck([(26,22),(27,18),(28,14),(27,10),(26,7)], 1) + thick_neck([(27,22),(28,18),(29,14),(28,10),(27,7)], 3)
neck_lo = thick_neck([(24,22),(24,18),(24,14),(24,11),(24,9)], 1) + thick_neck([(25,22),(25,18),(25,14),(25,11),(25,9)], 3)

# Heads — shaded
head   = shaded_el(24, 5, 16, 10, 1, 3, 2)
head_l = shaded_el(22, 5, 16, 10, 1, 3, 2)
head_r = shaded_el(26, 5, 16, 10, 1, 3, 2)
head_lo = shaded_el(24, 7, 16, 10, 1, 3, 2)

# Beaks — golden with shadow
beak   = re(28, 33, 4, 6, 6) + re(30, 34, 6, 7, 7)
beak_l = re(26, 31, 4, 6, 6) + re(28, 32, 6, 7, 7)
beak_r = re(30, 35, 4, 6, 6) + re(32, 36, 6, 7, 7)
beak_lo = re(28, 33, 6, 8, 6) + re(30, 34, 8, 9, 7)

eye   = [(25, 4, 4), (26, 4, 8)]  # eye + bright highlight
eye_l = [(23, 4, 4), (24, 4, 8)]
eye_r = [(27, 4, 4), (28, 4, 8)]
eye_lo = [(25, 6, 4), (26, 6, 8)]

bk_c = []
bk_o = re(28, 33, 7, 9, 7)
bk_ol = re(26, 31, 7, 9, 7)

wf_none = []
wf_up = shaded_re(15, 20, 22, 24, 5, 2, 5) + re(13, 18, 24, 26, 2) + re(11, 16, 26, 27, 5)
leg_lift = re(28, 30, 30, 34, 4) + re(29, 30, 28, 30, 4)

PF = [
    neck_c + head + beak + eye + bk_c + wf_none,
    neck_l + head_l + beak_l + eye_l + bk_c + wf_none,
    neck_r + head_r + beak_r + eye_r + bk_o + wf_up + leg_lift,
    neck_lo + head_lo + beak_lo + eye_lo + bk_ol + wf_none,
    neck_c + head + beak + eye + bk_c + wf_up,
    neck_l + head_l + beak_l + eye_l + bk_ol + wf_up + leg_lift,
]

frames = render_beautiful(B, PF, P)
write_piskel("flamingo.piskel", piskel("flamingo", "Flamingo with neck sway and pecking cycle", FPS, W, H, frames))
print("  ✓ flamingo.piskel")


# ================================================================
# 4. GIRAFFE — NECK SWAY & BROWSE
# Warm amber/ochre with chocolate spots
# ================================================================
print("Building Giraffe...")

P = [(0,0,0,0),
     (240,195,65,255),    # 1: golden yellow base
     (195,150,40,255),    # 2: amber shadow
     (255,225,120,255),   # 3: light yellow highlight
     (130,70,25,255),     # 4: chocolate spot
     (35,30,20,255),      # 5: dark (eyes/hooves)
     (255,255,200,255),   # 6: cream highlight
     (170,115,35,255),    # 7: medium brown
     (255,250,230,255),   # 8: white
     (100,55,20,255)]     # 9: dark brown

B = []
B += shaded_el(24, 30, 140, 40, 1, 3, 2)     # body
# Spots on body — chocolate brown
for x, y in [(15,26),(17,28),(19,26),(21,30),(23,28),
             (28,26),(30,28),(32,26),(34,30),(26,32),
             (20,32),(16,30),(31,32)]:
    B += re(x, x+1, y, y+1, 4)
# Legs
B += shaded_re(15, 19, 35, 43, 1, 3, 2)
B += shaded_re(29, 33, 35, 43, 1, 3, 2)
B += re(14, 20, 43, 45, 5) + re(28, 34, 43, 45, 5)  # dark hooves
# Tail
B += re(36, 38, 26, 28, 2) + re(38, 40, 24, 26, 2)
B += re(40, 42, 23, 25, 4)  # dark tuft

# Thick shaded necks
neck_str = thick_neck([(22,24),(22,18),(22,12),(22,7),(22,4)], 1) + thick_neck([(23,24),(23,18),(23,14),(23,8),(23,5)], 3)
neck_lft = thick_neck([(21,24),(19,18),(18,12),(19,7),(20,4)], 1) + thick_neck([(22,24),(20,18),(19,14),(20,8),(21,5)], 3)
neck_rgt = thick_neck([(23,24),(25,18),(26,12),(25,7),(24,4)], 1) + thick_neck([(24,24),(26,18),(27,14),(26,8),(25,5)], 3)
neck_up  = thick_neck([(22,24),(22,18),(22,12),(23,7),(23,3)], 1) + thick_neck([(23,24),(23,18),(23,14),(24,8),(24,4)], 3)

# Neck spots
nsp_s = [re(20,21,y,y,4) for y in [10,14,18]]
nsp_s = [p for sub in nsp_s for p in sub]
nsp_l = [re(17,18,y,y,4) for y in [10,14,18]]
nsp_l = [p for sub in nsp_l for p in sub]
nsp_r = [re(24,25,y,y,4) for y in [10,14,18]]
nsp_r = [p for sub in nsp_r for p in sub]
nsp_u = [re(21,22,y,y,4) for y in [9,13,17]]
nsp_u = [p for sub in nsp_u for p in sub]

# Heads — shaded
head_s = shaded_el(22, 2, 18, 8, 1, 3, 2)
head_l = shaded_el(20, 2, 18, 8, 1, 3, 2)
head_r = shaded_el(24, 2, 18, 8, 1, 3, 2)
head_u = shaded_el(23, 1, 18, 8, 1, 3, 2)

# Ossicones (horns) — dark tips
horn_s = re(19, 20, 0, 1, 7) + re(24, 25, 0, 1, 7) + [(19,0,4),(24,0,4)]
horn_l = re(17, 18, 0, 1, 7) + re(22, 23, 0, 1, 7) + [(17,0,4),(22,0,4)]
horn_r = re(21, 22, 0, 1, 7) + re(26, 27, 0, 1, 7) + [(21,0,4),(26,0,4)]
horn_u = re(20, 21, 0, 0, 7) + re(25, 26, 0, 0, 7) + [(20,0,4),(25,0,4)]

ear_s = re(17, 19, 1, 2, 1) + re(25, 27, 1, 2, 1)
ear_l = re(15, 17, 1, 2, 1) + re(23, 25, 1, 2, 1)
ear_r = re(19, 21, 1, 2, 1) + re(27, 29, 1, 2, 1)
ear_u = re(18, 20, 0, 1, 1) + re(26, 28, 0, 1, 1)

# Eyes with highlights
eyes_s = [(20,2,5),(24,2,5),(21,2,8),(25,2,8)]
eyes_l = [(18,2,5),(22,2,5),(19,2,8),(23,2,8)]
eyes_r = [(22,2,5),(26,2,5),(23,2,8),(27,2,8)]
eyes_u = [(21,1,5),(25,1,5),(22,1,8),(26,1,8)]
eyes_blink_s = [(20,3,5),(24,3,5)]
eyes_blink_r = [(22,3,5),(26,3,5)]

mz_s = re(20, 24, 3, 4, 7) + [(22, 4, 5)]
mz_l = re(18, 22, 3, 4, 7) + [(20, 4, 5)]
mz_r = re(22, 26, 3, 4, 7) + [(24, 4, 5)]
mz_u = re(21, 25, 2, 3, 7) + [(23, 3, 5)]
mz_o_s = re(20, 24, 3, 5, 7) + re(21, 23, 5, 6, 5)
mz_o_l = re(18, 22, 3, 5, 7) + re(19, 21, 5, 6, 5)

PF = [
    neck_str + nsp_s + head_s + horn_s + ear_s + eyes_s + mz_s,
    neck_lft + nsp_l + head_l + horn_l + ear_l + eyes_blink_s + mz_l,
    neck_rgt + nsp_r + head_r + horn_r + ear_r + eyes_r + mz_o_s,
    neck_up + nsp_u + head_u + horn_u + ear_u + eyes_u + mz_u,
    neck_str + nsp_s + head_s + horn_s + ear_s + eyes_blink_s + mz_s + re(17,19,1,1,6),
    neck_lft + nsp_l + head_l + horn_l + ear_l + eyes_l + mz_o_l,
]

frames = render_beautiful(B, PF, P)
write_piskel("giraffe.piskel", piskel("giraffe", "Giraffe browsing with neck sway", FPS, W, H, frames))
print("  ✓ giraffe.piskel")


# ================================================================
# 5. CAT — PLAYFUL SWIPE
# Warm sandy/orange tones, bright green eyes
# ================================================================
print("Building Cat...")

P = [(0,0,0,0),
     (210,170,135,255),   # 1: sandy base
     (165,125,90,255),    # 2: tan shadow
     (240,210,175,255),   # 3: light highlight
     (100,65,35,255),     # 4: dark brown stripes
     (35,30,25,255),      # 5: dark (nose, pupils)
     (100,210,95,255),    # 6: bright green eyes
     (255,250,240,255),   # 7: white (whiskers, eye highlight)
     (255,200,200,255),   # 8: pink (inner ear, nose)
     (180,140,100,255)]   # 9: medium brown

B = []
B += shaded_el(24, 30, 140, 45, 1, 3, 2)     # body
B += shaded_el(24, 33, 65, 15, 3, 7, 1)      # belly
# Head
B += shaded_el(24, 14, 55, 50, 1, 3, 2)
B += shaded_el(24, 15, 30, 25, 3, 7, 1)      # inner face light
# Ears with pink inner
B += re(16, 19, 5, 9, 1) + re(17, 18, 3, 4, 1) + [(17, 6, 8), (18, 6, 8)]
B += re(29, 32, 5, 9, 1) + re(30, 31, 3, 4, 1) + [(30, 6, 8), (31, 6, 8)]
# Neck
B += re(20, 28, 20, 24, 1)
# Pink nose
B += re(23, 25, 16, 16, 8)
# White whiskers
B += re(14, 18, 16, 16, 7) + re(14, 18, 18, 18, 7)
B += re(30, 34, 16, 16, 7) + re(30, 34, 18, 18, 7)
# Legs
B += shaded_re(14, 18, 35, 42, 1, 3, 2) + shaded_re(30, 34, 35, 42, 1, 3, 2)
B += re(13, 19, 42, 44, 3) + re(29, 35, 42, 44, 3)  # paws
# Body stripes
for x, y in [(15,26),(17,28),(19,26),(32,26),(34,28),(33,30)]:
    B += re(x, x+1, y, y+1, 4)

# Tail — shaded ellipses with stripes
tail_mid   = shaded_el(8, 31, 25, 12, 1, 3, 2) + el(6, 30, 10, 6, 4)
tail_left  = shaded_el(5, 30, 25, 12, 1, 3, 2) + el(3, 29, 10, 6, 4)
tail_right = shaded_el(11, 31, 25, 12, 1, 3, 2) + el(9, 30, 10, 6, 4)
tail_up    = shaded_el(6, 26, 14, 20, 1, 3, 2) + el(5, 23, 8, 6, 4)

# Green eyes with white highlight
eyes_open = (re(20, 22, 12, 14, 6) + re(26, 28, 12, 14, 6) +   # green iris
             [(21, 12, 5), (27, 12, 5)] +                        # pupils
             [(22, 12, 7), (28, 12, 7)])                          # highlights!
eyes_wide = (re(19, 23, 11, 14, 6) + re(25, 29, 11, 14, 6) +   # BIG
             [(21, 12, 5), (27, 12, 5)] +
             [(22, 11, 7), (28, 11, 7)])
eyes_blink = re(20, 22, 14, 14, 5) + re(26, 28, 14, 14, 5)

mc = [(24, 17, 5)]
mo = re(22, 26, 17, 18, 5)
mw = re(21, 27, 17, 19, 5) + re(22, 26, 19, 20, 5)

paw_L = shaded_re(10, 14, 34, 37, 1, 3, 2) + re(8, 12, 32, 34, 1) + re(7, 10, 31, 32, 3)
paw_R = shaded_re(34, 38, 34, 37, 1, 3, 2) + re(36, 40, 32, 34, 1) + re(38, 41, 31, 32, 3)

PF = [
    tail_mid + eyes_open + mc,
    tail_left + eyes_wide + mo + paw_L,
    tail_up + eyes_blink + mw,
    tail_right + eyes_open + mc,
    tail_mid + eyes_wide + mo + paw_R,
    tail_up + eyes_blink + mw + paw_L + re(16, 19, 5, 6, 2),  # + head tilt
]

frames = render_beautiful(B, PF, P)
write_piskel("cat.piskel", piskel("cat", "Playful cat with tail swish and swipe", FPS, W, H, frames))
print("  ✓ cat.piskel")


# ================================================================
# 6. BMO — DANCING
# Vibrant teal/mint, glowing screen, warm accents
# ================================================================
print("Building BMO...")

P = [(0,0,0,0),
     (80,200,140,255),    # 1: teal body
     (55,160,105,255),    # 2: dark teal
     (120,230,175,255),   # 3: light teal
     (45,55,170,255),     # 4: blue eyes
     (25,25,25,255),      # 5: dark
     (245,220,75,255),    # 6: yellow button
     (225,75,75,255),     # 7: red button
     (255,255,255,255),   # 8: white
     (175,245,210,255)]   # 9: screen glow (pale mint)

B = []
# Body — shaded rectangle
B += shaded_re(11, 36, 12, 38, 1, 3, 2)
# Border highlights
for x in range(11, 37):
    B += [(x, 12, 3), (x, 38, 2)]
for y in range(12, 39):
    B += [(11, y, 2), (36, y, 2)]
# Screen — glowing mint
B += re(14, 33, 15, 27, 9)
# Screen border
for x in range(14, 34):
    B += [(x, 15, 2), (x, 27, 2)]
for y in range(15, 28):
    B += [(14, y, 2), (33, y, 2)]
# D-pad
B += re(16, 19, 30, 34, 2) + re(15, 20, 31, 33, 2)
# Colorful buttons
B += re(27, 29, 30, 32, 6) + re(30, 32, 31, 33, 7) + re(27, 29, 33, 35, 6)
# Legs
B += shaded_re(16, 20, 39, 44, 2, 1, 2)
B += shaded_re(27, 31, 39, 44, 2, 1, 2)
B += re(15, 21, 44, 46, 2) + re(26, 32, 44, 46, 2)
# Antenna
B += re(22, 25, 8, 11, 2) + re(23, 24, 6, 7, 2)

# Arms — thick shaded
arm_L_dn = shaded_re(4, 10, 24, 31, 1, 3, 2)
arm_L_up = shaded_re(4, 10, 14, 21, 1, 3, 2)
arm_L_mid = shaded_re(4, 10, 19, 26, 1, 3, 2)
arm_L_wave = shaded_re(2, 8, 10, 17, 1, 3, 2)

arm_R_dn = shaded_re(37, 43, 24, 31, 1, 3, 2)
arm_R_up = shaded_re(37, 43, 14, 21, 1, 3, 2)
arm_R_mid = shaded_re(37, 43, 19, 26, 1, 3, 2)
arm_R_wave = shaded_re(39, 45, 10, 17, 1, 3, 2)

# Screen faces with bright highlights
eyes_n = (re(18, 20, 19, 21, 4) + re(27, 29, 19, 21, 4) +
          [(19, 19, 8), (28, 19, 8)])  # highlight!
eyes_h = (re(18, 21, 20, 21, 4) + re(26, 29, 20, 21, 4))
eyes_w = (re(17, 21, 18, 21, 4) + re(26, 30, 18, 21, 4) +
          [(19, 18, 8), (28, 18, 8)])
eyes_wk = (re(18, 20, 19, 21, 4) + [(19, 19, 8)] +
            re(27, 29, 21, 21, 5))

m_smile = re(20, 27, 24, 24, 5) + [(20, 25, 5), (27, 25, 5)]
m_open = re(21, 26, 23, 25, 5)
m_grin = re(19, 28, 24, 25, 5) + re(20, 27, 25, 25, 8)
m_o = re(22, 25, 23, 25, 5)

btn_f1 = re(27, 29, 30, 32, 8)
btn_f2 = re(30, 32, 31, 33, 8)
leg_L = shaded_re(14, 18, 39, 44, 2, 1, 2) + re(13, 19, 44, 46, 2)
leg_R = shaded_re(29, 33, 39, 44, 2, 1, 2) + re(28, 34, 44, 46, 2)

PF = [
    arm_L_dn + arm_R_dn + eyes_n + m_smile,
    arm_L_up + arm_R_dn + eyes_h + m_grin + btn_f1 + leg_L,
    arm_L_up + arm_R_up + eyes_w + m_open,
    arm_L_dn + arm_R_up + eyes_wk + m_smile + btn_f2 + leg_R,
    arm_L_wave + arm_R_wave + eyes_h + m_grin + btn_f1,
    arm_L_mid + arm_R_mid + eyes_w + m_o + btn_f2 + leg_L,
]

frames = render_beautiful(B, PF, P)
write_piskel("BMO.piskel", piskel("BMO", "BMO dancing with button-mashing animation", FPS, W, H, frames))
print("  ✓ BMO.piskel")


# ================================================================
# 7. TOTORO — BELLY-DRUM
# Soft grey with warm belly, earthy tones
# ================================================================
print("Building Totoro...")

P = [(0,0,0,0),
     (150,150,165,255),   # 1: grey base
     (110,110,125,255),   # 2: grey shadow
     (190,190,205,255),   # 3: grey highlight
     (235,235,245,255),   # 4: white belly
     (190,155,130,255),   # 5: nose (warm brown)
     (35,35,40,255),      # 6: dark details
     (205,205,220,255),   # 7: light grey
     (125,185,105,255),   # 8: leaf green
     (255,250,240,255)]   # 9: white highlight

B = []
B += shaded_el(24, 28, 170, 130, 1, 3, 2)     # body
B += shaded_el(24, 31, 80, 50, 4, 9, 7)       # white belly with shading!
# Belly V-marks
for dx in [-4, -2, 0, 2, 4]:
    B += [(24+dx, 28, 2), (24+dx+1, 29, 2)]
for dx in [-3, -1, 1, 3]:
    B += [(24+dx, 31, 2), (24+dx+1, 32, 2)]
# Feet
B += re(14, 20, 40, 43, 2) + re(28, 34, 40, 43, 2)
for x in [14, 17, 20]: B.append((x, 44, 6))
for x in [28, 31, 34]: B.append((x, 44, 6))
# Warm brown nose
B += re(22, 26, 22, 23, 5)
# Whiskers
B += re(12, 16, 24, 24, 6) + re(12, 16, 26, 26, 6)
B += re(32, 36, 24, 24, 6) + re(32, 36, 26, 26, 6)
# Leaf — bright green
B += re(22, 26, 9, 12, 8) + re(23, 25, 8, 8, 8) + [(24, 7, 8)]

# Ears
ear_L_up   = shaded_re(12, 16, 9, 16, 1, 3, 2)  + re(13, 15, 7, 8, 1)
ear_L_tilt = shaded_re(9, 13, 10, 17, 1, 3, 2) + re(10, 12, 8, 9, 1)
ear_R_up   = shaded_re(32, 36, 9, 16, 1, 3, 2) + re(33, 35, 7, 8, 1)
ear_R_tilt = shaded_re(35, 39, 10, 17, 1, 3, 2) + re(36, 38, 8, 9, 1)

# Cute eyes with bright highlights
eyes_o = (re(19, 21, 19, 21, 6) + re(27, 29, 19, 21, 6) +
           [(21, 19, 9), (29, 19, 9)])  # highlight!
eyes_h = re(19, 22, 21, 21, 6) + re(26, 29, 21, 21, 6)
eyes_w = re(19, 21, 18, 21, 6) + re(27, 29, 18, 21, 6)
eyes_b = re(19, 21, 21, 21, 6) + re(27, 29, 21, 21, 6)

m_c = re(22, 26, 25, 25, 6)
m_o = re(21, 27, 25, 27, 6)
m_w = re(20, 28, 25, 28, 6)
m_r = re(20, 28, 25, 28, 6) + re(21, 27, 26, 26, 9)  # teeth!

arm_L_dn  = shaded_re(7, 12, 26, 34, 1, 3, 2)
arm_L_up  = shaded_re(7, 12, 19, 27, 1, 3, 2)
arm_L_pat = shaded_re(14, 19, 28, 33, 1, 3, 2)
arm_L_out = shaded_re(2, 8, 22, 30, 1, 3, 2)

arm_R_dn  = shaded_re(36, 41, 26, 34, 1, 3, 2)
arm_R_up  = shaded_re(36, 41, 19, 27, 1, 3, 2)
arm_R_pat = shaded_re(29, 34, 28, 33, 1, 3, 2)
arm_R_out = shaded_re(40, 46, 22, 30, 1, 3, 2)

PF = [
    arm_L_dn + arm_R_dn + ear_L_up + ear_R_up + eyes_o + m_c,
    arm_L_up + arm_R_up + ear_L_tilt + ear_R_up + eyes_w + m_o,
    arm_L_pat + arm_R_up + ear_L_up + ear_R_tilt + eyes_h + m_r,
    arm_L_up + arm_R_pat + ear_L_tilt + ear_R_up + eyes_w + m_w,
    arm_L_pat + arm_R_pat + ear_L_tilt + ear_R_tilt + eyes_b + m_r,
    arm_L_out + arm_R_out + ear_L_up + ear_R_up + eyes_h + m_w,
]

frames = render_beautiful(B, PF, P)
write_piskel("Totoro.piskel", piskel("Totoro", "Totoro belly-drum celebration dance", FPS, W, H, frames))
print("  ✓ Totoro.piskel")


# ================================================================
# 8. KNIGHT — SWORD SWING
# Noble steel blues, rich crimson plume, gold accents
# ================================================================
print("Building Knight...")

P = [(0,0,0,0),
     (170,175,195,255),   # 1: steel base
     (120,125,145,255),   # 2: steel shadow
     (210,215,235,255),   # 3: steel highlight
     (200,45,45,255),     # 4: crimson plume
     (160,120,75,255),    # 5: brown belt
     (70,75,90,255),      # 6: visor dark
     (235,235,245,255),   # 7: bright steel
     (255,240,140,255),   # 8: gold glint
     (145,30,30,255)]     # 9: dark red

B = []
B += shaded_el(24, 11, 60, 45, 1, 3, 2)       # helmet
B += re(16, 32, 5, 5, 2)                       # top line
B += re(17, 31, 12, 15, 6)                     # visor
for x in [20, 24, 28]:
    B += re(x, x, 12, 15, 2)
B += shaded_re(14, 33, 18, 32, 1, 3, 2)       # chest
B += shaded_re(17, 30, 18, 23, 7, 8, 3)       # chest shine
B += re(14, 33, 33, 34, 5)                     # belt
B += re(22, 25, 33, 34, 8)                     # gold buckle
B += shaded_re(16, 22, 35, 42, 2, 1, 2)       # legs
B += shaded_re(25, 31, 35, 42, 2, 1, 2)
B += re(15, 23, 43, 45, 1) + re(24, 32, 43, 45, 1)  # boots
B += shaded_el(12, 19, 18, 12, 2, 1, 2)       # shoulder L
B += shaded_el(35, 19, 18, 12, 2, 1, 2)       # shoulder R

# Plume — shaded deep red
plume_c = shaded_re(21, 27, 0, 5, 4, 4, 9)
plume_l = shaded_re(17, 23, 0, 5, 4, 4, 9)
plume_r = shaded_re(25, 31, 0, 5, 4, 4, 9)

# Sword — bright steel blade with gold hilt
sword_ready = (shaded_re(35, 40, 20, 30, 2, 1, 2) +
               re(39, 42, 10, 20, 7) + re(40, 43, 8, 10, 8))
sword_back  = (shaded_re(37, 42, 18, 28, 2, 1, 2) +
               re(41, 44, 6, 18, 7) + re(42, 45, 4, 6, 8))
sword_slash = (shaded_re(34, 38, 20, 28, 2, 1, 2) +
               re(24, 35, 18, 20, 7) + re(22, 24, 17, 19, 8))
sword_over  = (shaded_re(35, 40, 18, 26, 2, 1, 2) +
               re(36, 39, 4, 18, 7) + re(36, 39, 2, 4, 8))
sword_down  = (shaded_re(35, 40, 22, 32, 2, 1, 2) +
               re(39, 42, 32, 42, 7) + re(40, 43, 42, 44, 8))
sword_thrust= (shaded_re(35, 40, 20, 28, 2, 1, 2) +
               re(40, 47, 22, 24, 7) + re(46, 47, 21, 25, 8))

# Shield — deep red with gold rim
shield_rest  = shaded_el(8, 28, 30, 40, 4, 4, 9) + el(8, 28, 10, 14, 8)
shield_raise = shaded_el(8, 24, 30, 40, 4, 4, 9) + el(8, 24, 10, 14, 8)
shield_bash  = shaded_el(5, 26, 30, 40, 4, 4, 9) + el(5, 26, 10, 14, 8)

glint_n = []
glint_L = re(19, 20, 13, 13, 8)
glint_R = re(28, 29, 13, 13, 8)
glint_B = re(19, 20, 13, 13, 8) + re(28, 29, 13, 13, 8)

PF = [
    sword_ready + shield_rest + plume_c + glint_R,
    sword_back + shield_raise + plume_l + glint_B,
    sword_slash + shield_raise + plume_r + glint_L,
    sword_over + shield_bash + plume_l + glint_n,
    sword_thrust + shield_rest + plume_c + glint_R,
    sword_down + shield_raise + plume_r + glint_B,
]

frames = render_beautiful(B, PF, P)
write_piskel("Knight.piskel", piskel("Knight", "Knight sword swing and shield bash cycle", FPS, W, H, frames))
print("  ✓ Knight.piskel")


# ================================================================
# 9. ALIEN — HOVERING / BEAM
# Vivid greens, glowing yellows, purple accents
# ================================================================
print("Building Alien...")

P = [(0,0,0,0),
     (95,215,100,255),    # 1: green base
     (60,175,65,255),     # 2: green shadow
     (145,240,150,255),   # 3: green highlight
     (220,220,55,255),    # 4: yellow eyes
     (150,55,200,255),    # 5: purple accent
     (25,25,25,255),      # 6: dark
     (255,100,100,255),   # 7: red antenna glow
     (100,185,255,255),   # 8: beam blue
     (75,255,245,255)]    # 9: cyan glow

B = []
B += shaded_el(24, 16, 110, 80, 1, 3, 2)       # head
B += shaded_el(24, 12, 60, 25, 3, 3, 1)        # forehead glow
B += re(19, 29, 26, 28, 2)                      # neck
B += shaded_el(24, 33, 70, 30, 1, 3, 2)        # torso
B += re(17, 19, 31, 36, 5) + re(29, 31, 31, 36, 5)  # purple markings
B += el(24, 37, 50, 8, 2)                       # body bottom

# Eyes — large with bright highlights
eyes_c = (re(18, 22, 14, 17, 4) + re(26, 30, 14, 17, 4) +
          [(21, 15, 6), (29, 15, 6)] +    # pupils
          [(19, 14, 9), (27, 14, 9)])      # bright highlight!
eyes_l = (re(18, 22, 14, 17, 4) + re(26, 30, 14, 17, 4) +
          [(18, 15, 6), (26, 15, 6)] + [(19, 14, 9), (27, 14, 9)])
eyes_r = (re(18, 22, 14, 17, 4) + re(26, 30, 14, 17, 4) +
          [(22, 15, 6), (30, 15, 6)] + [(19, 14, 9), (27, 14, 9)])
eyes_bk = re(18, 22, 17, 17, 6) + re(26, 30, 17, 17, 6)

mouth_c  = re(21, 27, 20, 20, 6)
mouth_o  = re(21, 27, 20, 22, 6)
mouth_sm = re(21, 27, 20, 21, 6) + [(21, 21, 6), (27, 21, 6)]

# Antennae — thick with red/cyan glow
ant_L_up   = re(15, 17, 3, 8, 2) + shaded_re(14, 18, 1, 3, 7, 7, 7)
ant_R_up   = re(31, 33, 3, 8, 2) + shaded_re(30, 34, 1, 3, 7, 7, 7)
ant_L_tilt = re(11, 13, 4, 9, 2) + shaded_re(9, 13, 2, 4, 7, 7, 7)
ant_R_tilt = re(35, 37, 4, 9, 2) + shaded_re(35, 39, 2, 4, 7, 7, 7)
ant_L_glow = re(15, 17, 3, 8, 2) + shaded_re(13, 19, 0, 3, 9, 9, 9)
ant_R_glow = re(31, 33, 3, 8, 2) + shaded_re(29, 35, 0, 3, 9, 9, 9)

# Arms — shaded
arm_L_dn   = shaded_re(8, 14, 30, 37, 2, 1, 2) + shaded_el(11, 38, 10, 6, 1, 3, 2)
arm_L_wave = shaded_re(4, 10, 22, 29, 2, 1, 2) + shaded_el(4, 21, 10, 6, 1, 3, 2)
arm_L_out  = shaded_re(2, 8, 28, 32, 2, 1, 2)  + shaded_el(1, 30, 10, 6, 1, 3, 2)
arm_L_up   = shaded_re(8, 14, 20, 27, 2, 1, 2) + shaded_el(11, 19, 10, 6, 1, 3, 2)

arm_R_dn   = shaded_re(34, 40, 30, 37, 2, 1, 2) + shaded_el(37, 38, 10, 6, 1, 3, 2)
arm_R_wave = shaded_re(38, 44, 22, 29, 2, 1, 2) + shaded_el(44, 21, 10, 6, 1, 3, 2)
arm_R_out  = shaded_re(40, 46, 28, 32, 2, 1, 2) + shaded_el(47, 30, 10, 6, 1, 3, 2)
arm_R_up   = shaded_re(34, 40, 20, 27, 2, 1, 2) + shaded_el(37, 19, 10, 6, 1, 3, 2)

# Beam — glowing with cyan core
beam_off  = []
beam_on   = (re(21, 27, 40, 42, 8) + re(22, 26, 42, 44, 9) + re(23, 25, 44, 46, 8))
beam_wide = (re(18, 30, 40, 42, 8) + re(20, 28, 42, 44, 9) +
             re(22, 26, 44, 46, 8) + re(23, 25, 46, 47, 9))

PF = [
    arm_L_dn + arm_R_dn + eyes_c + mouth_c + ant_L_up + ant_R_up + beam_off,
    arm_L_wave + arm_R_dn + eyes_l + mouth_sm + ant_L_tilt + ant_R_up + beam_on,
    arm_L_wave + arm_R_wave + eyes_r + mouth_o + ant_L_glow + ant_R_glow + beam_wide,
    arm_L_out + arm_R_out + eyes_c + mouth_sm + ant_L_up + ant_R_tilt + beam_on,
    arm_L_dn + arm_R_wave + eyes_bk + mouth_c + ant_L_tilt + ant_R_tilt + beam_off,
    arm_L_up + arm_R_up + eyes_c + mouth_o + ant_L_glow + ant_R_glow + beam_wide,
]

frames = render_beautiful(B, PF, P)
write_piskel("Alien.piskel", piskel("Alien", "Alien hovering with tractor beam and wave", FPS, W, H, frames))
print("  ✓ Alien.piskel")


# ================================================================
# 10. WITCH — SPELL-CASTING
# Deep purple robe, green magic glow, golden sparkles
# ================================================================
print("Building Witch...")

P = [(0,0,0,0),
     (90,60,120,255),     # 1: dark purple
     (65,40,95,255),      # 2: deep purple shadow
     (120,90,155,255),    # 3: medium purple
     (230,210,190,255),   # 4: skin
     (65,210,65,255),     # 5: green magic
     (250,215,90,255),    # 6: golden sparkle
     (170,115,70,255),    # 7: brown hair
     (255,140,220,255),   # 8: pink glow
     (185,255,185,255)]   # 9: light green glow

B = []
# Hat brim
B += re(6, 42, 18, 20, 2)
# Hat cone — shaded
B += shaded_re(15, 33, 14, 17, 1, 3, 2)
B += shaded_re(18, 30, 10, 13, 1, 3, 2)
B += shaded_re(20, 28, 6, 9, 1, 3, 2)
B += shaded_re(22, 26, 3, 5, 1, 3, 2)
# Hat band — golden
B += re(15, 33, 17, 17, 6)
B += re(22, 26, 17, 17, 6)
# Face
B += re(14, 34, 21, 30, 4)
# Hair
B += re(8, 14, 18, 28, 7) + re(34, 40, 18, 28, 7)
# Nose
B += re(23, 25, 26, 27, 4)
# Robe — shaded
B += shaded_re(12, 36, 31, 44, 1, 3, 2)
# Robe hem — darker
B += re(10, 38, 43, 46, 2)
for x in range(10, 39, 3):
    B.append((x, 45, 3))
# Stars on robe — golden
B += re(15, 17, 36, 37, 6) + re(31, 33, 36, 37, 6) + re(23, 25, 40, 41, 6)

hat_c = re(23, 25, 0, 2, 1)
hat_l = re(19, 21, 0, 2, 1)
hat_r = re(27, 29, 0, 2, 1)

# Eyes — dark with green glow variant
eyes_n = re(18, 20, 23, 25, 1) + re(28, 30, 23, 25, 1)
eyes_g = re(18, 20, 23, 25, 5) + re(28, 30, 23, 25, 5) + [(20,23,9),(30,23,9)]
eyes_s = re(18, 20, 25, 25, 1) + re(28, 30, 25, 25, 1)
eyes_b = re(18, 20, 25, 25, 2) + re(28, 30, 25, 25, 2)

m_sm = re(22, 27, 28, 28, 2)
m_op = re(22, 27, 28, 29, 2)
m_ck = re(21, 28, 28, 30, 2) + re(22, 27, 29, 29, 4)

# Wand arm — shaded with bright sparkle tip
wand_dn = (shaded_re(37, 42, 28, 36, 7, 7, 7) +
            re(42, 44, 26, 28, 5) + re(44, 46, 24, 26, 6))
wand_mid = (shaded_re(37, 42, 24, 32, 7, 7, 7) +
             re(42, 44, 20, 24, 5) + re(44, 46, 18, 20, 6))
wand_up = (shaded_re(37, 42, 18, 26, 7, 7, 7) +
            re(42, 44, 14, 18, 5) + re(44, 46, 12, 14, 6) + re(43, 47, 10, 12, 8))
wand_cast = (shaded_re(35, 40, 22, 30, 7, 7, 7) +
              re(30, 36, 18, 20, 5) + re(28, 30, 16, 18, 6) + re(26, 28, 14, 16, 8))

arm_L_dn = shaded_re(4, 10, 28, 36, 1, 3, 2)
arm_L_up = shaded_re(4, 10, 22, 30, 1, 3, 2)
arm_L_cast = shaded_re(2, 8, 24, 32, 1, 3, 2)

# Sparkles — golden with pink glow
sp1 = re(28, 30, 12, 14, 6) + re(32, 34, 8, 10, 8)
sp2 = re(4, 6, 8, 10, 6) + re(8, 10, 4, 6, 8)
sp3 = re(40, 42, 6, 8, 6) + re(44, 46, 4, 6, 8)
sp4 = re(16, 18, 4, 6, 6) + re(12, 14, 2, 4, 8)
sp_n = []

robe_n = []
robe_l = shaded_re(8, 12, 38, 44, 1, 3, 2)
robe_r = shaded_re(36, 40, 38, 44, 1, 3, 2)

PF = [
    wand_dn + arm_L_dn + eyes_n + m_sm + hat_c + sp_n + robe_n,
    wand_mid + arm_L_up + eyes_s + m_op + hat_l + sp_n + robe_l,
    wand_up + arm_L_cast + eyes_g + m_ck + hat_r + sp1 + sp3 + robe_r,
    wand_cast + arm_L_up + eyes_g + m_op + hat_l + sp2 + sp4 + robe_l,
    wand_mid + arm_L_cast + eyes_s + m_sm + hat_c + sp1 + robe_r,
    wand_up + arm_L_up + eyes_b + m_ck + hat_r + sp1 + sp2 + sp3 + robe_l,
]

frames = render_beautiful(B, PF, P)
write_piskel("Witch.piskel", piskel("Witch", "Witch casting spells with sparkle trail", FPS, W, H, frames))
print("  ✓ Witch.piskel")


# ================================================================
# VERIFICATION
# ================================================================
print("\n" + "=" * 50)
print("VERIFICATION")
print("=" * 50)

all_files = [
    "owl.piskel", "t-rex.piskel", "flamingo.piskel", "giraffe.piskel", "cat.piskel",
    "BMO.piskel", "Totoro.piskel", "Knight.piskel", "Alien.piskel", "Witch.piskel",
]

all_ok = True
for f in all_files:
    if not verify(f):
        all_ok = False

print()
if all_ok:
    print("✅ All 10 characters — beautiful with outlines, shading & details!")
else:
    print("⚠️  Some characters need investigation.")
print("\nUntouched: goku-fixed version.piskel, llama-assest.piskel")
print("Done!")
