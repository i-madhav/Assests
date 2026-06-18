"""
Generate .piskel sprite animations with CHARACTER-SPECIFIC ACTIONS.
No more just talking heads — each sprite has a signature motion cycle.

All: 48×48, 12 FPS, 6 frames.
Each frame is a FRESH render with unique pixel data.
"""
import base64, io, json, os, hashlib
from PIL import Image

# ---------- helpers ----------

def strip(frames, w, h):
    s = Image.new("RGBA", (w * len(frames), h), (0,0,0,0))
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    b = io.BytesIO()
    s.save(b, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(b.getvalue()).decode('ascii')}"

def piskel(name, desc, fps, w, h, frames):
    lo = {"name":"Layer 1","opacity":1,"frameCount":len(frames),
          "chunks":[{"layout":[[i] for i in range(len(frames))],
                     "base64PNG":strip(frames,w,h)}]}
    return {"modelVersion":2,"piskel":{"name":name,"description":desc,"fps":fps,
            "height":h,"width":w,"layers":[json.dumps(lo)],"hiddenFrames":[]}}

def render(base, per_frame, pal, w=48, h=48):
    fr = []
    for fi in range(6):
        im = Image.new("RGBA", (w,h), (0,0,0,0))
        px = im.load()
        for x,y,ci in base:
            if 0<=x<w and 0<=y<h: px[x,y] = pal[ci]
        for x,y,ci in per_frame[fi]:
            if 0<=x<w and 0<=y<h: px[x,y] = pal[ci]
        fr.append(im)
    return fr

def el(cx,cy,rx2,ry2,ci):
    r = int(max(rx2,ry2)**.5)+1
    return [(x,y,ci) for x in range(int(cx)-r,int(cx)+r+1)
            for y in range(int(cy)-r,int(cy)+r+1)
            if (x-cx)**2/rx2+(y-cy)**2/ry2 <= 1]

def re(x1,x2,y1,y2,ci):
    return [(x,y,ci) for x in range(x1,x2+1) for y in range(y1,y2+1)]

# ================================================================
# 1. OWL — FLYING CYCLE
# Wings flap up and down. Beak opens as if calling mid-flight.
# Body bobs up/down. Eyes blink at peak of wing stroke.
# ================================================================
P = [(0,0,0,0), (160,130,105), (115,90,70), (215,190,160),
     (248,228,188), (30,30,30), (255,215,55), (95,75,50)]

# --- BASE (body, face disc, belly, feet — drawn every frame) ---
B = []
B += el(24, 27, 175, 140, 1)          # body
B += el(23.5, 18.5, 55, 38, 4)        # face disc
B += el(24, 31, 50, 30, 3)            # belly
B += re(12,14,10,11,1) + re(33,35,10,11,1)  # ear tufts
B += re(14,17,38,39,2) + re(30,33,38,39,2)  # feet
# Feather detail
for y in [25,28,31]:
    for x in range(19,29):
        if (x-24)**2/35 <= 1: B.append((x,y,2))
for y in [26,29,32]:
    for x in range(20,28):
        if (x-24)**2/20 <= 1: B.append((x,y,3))
# Beak (fixed triangle as base)
B += [(22,19,7),(23,19,7),(24,19,7),(25,19,7),
      (23,18,7),(24,18,7)]

# --- PER-FRAME: wings change position, body Y shifts, eyes blink ---
# Wing positions: 3 states — UP, MID, DOWN
# UP: wings at body TOP edge
w_up_l  = [(10,18,2),(11,18,2),(12,18,2),(13,19,2),(14,20,2),(15,21,2)]
w_up_r  = [(33,18,2),(34,18,2),(35,18,2),(36,19,2),(37,20,2),(38,21,2)]

# MID: wings at body CENTER
w_mid_l = [(10,22,2),(11,23,2),(12,24,2),(13,25,2),(14,24,2)]
w_mid_r = [(33,22,2),(34,23,2),(35,24,2),(36,25,2),(37,24,2)]

# DOWN: wings extended DOWN
w_dn_l = [(10,27,2),(11,28,2),(12,29,2),(13,30,2),(14,29,2),(15,28,2)]
w_dn_r = [(33,27,2),(34,28,2),(35,29,2),(36,30,2),(37,29,2),(38,28,2)]

# Body bob: shift the whole body + feet up/down by changing a few edge pixels
# Frame 2 & 5 = body HIGH (wings up, body lifted — like a wing beat)
# Frame 0 & 3 = body LOW (wings down, body settled)

eyes_open  = [(19,17,6),(20,17,6),(21,17,6),
              (19,18,6),(20,18,6),(21,18,6),
              (26,17,6),(27,17,6),(28,17,6),
              (26,18,6),(27,18,6),(28,18,6),
              (20,17,5),(27,17,5)]
eyes_blink = [(20,17,5),(27,17,5)]  # narrowed pupils
eyes_half  = [(20,17,5),(27,17,5),(20,16,5),(27,16,5)]  # squint

# Beak open shapes (additional pixels beyond base beak)
b_closed = []
b_slight = [(22,20,7),(25,20,7)]
b_wide   = [(22,20,7),(23,20,7),(24,20,7),(25,20,7),(22,21,7),(24,21,7)]
b_medium = [(22,20,7),(25,20,7),(23,20,7)]

# Body bob pixels (add/subtract on neck to simulate vertical shift)
bob_up  = [(23,10,1),(24,10,1)]   # neck extends up
bob_dn  = []

PF = [
    # F0: wings DOWN, body LOW, eyes open, beak closed
    w_dn_l + w_dn_r + eyes_open + b_closed,
    # F1: wings MID, body settling, eyes half, beak slight
    w_mid_l + w_mid_r + eyes_half + b_slight,
    # F2: wings UP, body HIGH, eyes blink, beak WIDE
    w_up_l + w_up_r + eyes_blink + b_wide + bob_up,
    # F3: wings DOWN, body LOW, eyes open, beak medium
    w_dn_l + w_dn_r + eyes_open + b_medium,
    # F4: wings MID, body settling, eyes open, beak wide
    w_mid_l + w_mid_r + eyes_open + b_wide,
    # F5: wings UP, body HIGH, eyes blink, beak medium + extra feather
    w_up_l + w_up_r + eyes_blink + b_medium + bob_up + [(13,19,2),(14,20,2)],
]

frames = render(B, PF, P)
with open("owl.piskel","w") as f:
    json.dump(piskel("owl","Flying owl with wing-flap cycle",12,48,48,frames),f,separators=(",",":"))
print("✓ owl.piskel — flying cycle")

# ================================================================
# 2. T-REX — STOMP & ROAR
# Body leans forward/back. Jaw snaps. Tiny arms wave. Tail sways.
# ================================================================
P = [(0,0,0,0), (105,185,100), (78,148,73), (155,225,150),
     (58,108,53), (30,30,30), (255,215,55), (255,255,255)]

B = []
B += el(23.5, 25, 80, 55, 1)          # body
B += el(23.5, 28, 55, 25, 3)          # belly
B += el(10, 30, 25, 15, 1)            # tail
B += el(27, 12, 58, 32, 1)            # head
B += re(34,37,11,16,1)                # snout
# Jaw line
for x in range(24,38):
    for y in [16,17]:
        if (x-27)**2/58+(y-12)**2/32 <= 1: B.append((x,y,2))
# Teeth
for x in [27,29,31,33]: B.append((x,17,7))
B += re(13,16,32,42,1) + re(30,33,32,42,1)  # legs
B += re(12,13,41,41,4) + re(17,18,41,41,4)
B += re(29,30,41,41,4) + re(34,35,41,41,4)
# Tiny arms (baseline) — will be overwritten per frame
# Spikes
for x,y in [(16,18),(17,17),(18,16),(19,15),(20,15),
            (21,14),(22,14),(23,14),(24,14),(25,15),
            (26,15),(27,15),(28,16),(29,16),(30,17),
            (31,18),(12,22),(10,24),(8,26),(7,28),(6,29),
            (5,30),(5,31)]:
    B.append((x,y,4))
B.append((36,13,4))  # nostril
# Belly stripes
for x in range(17,32):
    for y in [30,33]:
        if (x-23.5)**2/55+(y-28)**2/25 <= 1: B.append((x,y,2))
# Tail tip detail
B += [(4,31,1),(4,32,1),(4,30,1)]

# Arm positions
arm_down_l = [(18,20,1),(19,21,1),(20,22,1)]
arm_down_r = [(30,20,1),(31,21,1),(32,22,1)]
arm_up_l   = [(18,18,1),(19,17,1),(20,16,1)]
arm_up_r   = [(30,18,1),(31,17,1),(32,16,1)]
arm_fw_l   = [(18,20,1),(19,19,1),(20,18,1)]
arm_fw_r   = [(30,20,1),(31,19,1),(32,18,1)]

# Jaw positions
jaw_closed = []
jaw_slight = [(28,17,5),(29,17,5),(30,17,5)]
jaw_wide   = [(26,16,5),(27,16,5),(28,16,5),(29,16,5),
              (30,16,5),(31,16,5),(32,16,5),(33,16,5)]
jaw_medium = [(27,17,5),(28,17,5),(29,17,5),(30,17,5)]

# Body lean forward (shift head/tail pixels)
lean_fw = [(34,14,1),(35,14,1),(36,14,1)]  # head extends right
lean_bk = [(5,32,1),(5,33,1)]              # tail extends left

eyes_open  = [(23,9,6),(24,9,6),(23,10,6),(24,10,6),
              (23,9,5),(24,9,7)]
eyes_blink = [(23,9,5),(24,9,5)]

PF = [
    # F0: NEUTRAL — arms down, jaw closed, eyes open
    arm_down_l + arm_down_r + eyes_open + jaw_closed,
    # F1: LEAN BACK — arms up, jaw slight, eyes open, tail back
    arm_up_l + arm_up_r + eyes_open + jaw_slight + lean_bk,
    # F2: ROAR! — arms up, jaw WIDE, eyes blink, head forward
    arm_up_l + arm_up_r + eyes_blink + jaw_wide + lean_fw,
    # F3: RECOVER — arms fwd, jaw medium, eyes open
    arm_fw_l + arm_fw_r + eyes_open + jaw_medium,
    # F4: NEUTRAL — arms down, jaw closed, eyes half
    arm_down_l + arm_down_r + eyes_blink + jaw_closed,
    # F5: ROAR 2 — arms up, jaw extra wide, eyes blink
    arm_up_l + arm_up_r + eyes_blink + jaw_wide + [(34,16,5),(35,16,5)],
]

frames = render(B, PF, P)
with open("t-rex.piskel","w") as f:
    json.dump(piskel("t-rex","Stomping T-Rex with roar cycle",12,48,48,frames),f,separators=(",",":"))
print("✓ t-rex.piskel — stomp & roar")

# ================================================================
# 3. FLAMINGO — NECK SWAY & PECK
# Neck curves left/right in a graceful S-curve. Beak pecks down.
# Wing flutters. One leg lifts.
# ================================================================
P = [(0,0,0,0), (255,185,200), (238,158,168), (255,218,228),
     (50,50,50), (255,145,160), (255,215,105), (255,160,60)]

B = []
# Body (fixed)
B += el(23.5, 26, 95, 38, 1)     # body
B += el(23.5, 24, 72, 14, 3)     # highlight
for x in range(28,35):
    for y in range(21,32):
        if (x-23.5)**2/95+(y-26)**2/38 <= 1: B.append((x,y,2))
# Wing (deep pink accent)
B += el(18, 26, 18, 14, 5)
for x in range(14,19):
    for y in [23,24,25,26,27,28]:
        if (x-18)**2/18+(y-26)**2/14 <= 1: B.append((x,y,2))
# Legs (fixed, one leg lifts per frame)
B += re(16,17,32,46,4)  # left leg always on ground
B += re(25,26,32,46,4)  # right leg always on ground
# Feet
B += re(13,20,46,46,4)
B += re(22,29,46,46,4)

# NECK positions (per frame — flamingo moves its neck in an S-curve)
# Each frame: neck is drawn fresh per frame, not in base.
# Base still has a solid body. Neck + head are per-frame.

# Neck S-curve positions — each is a set of (x,y,ci) for neck pixels
def neck_path(points, ci):
    """Draw neck as a connected pixel strip. points = [(x,y), ...]"""
    px = []
    for i in range(len(points)-1):
        x1,y1 = points[i]
        x2,y2 = points[i+1]
        steps = max(abs(x2-x1), abs(y2-y1)) + 1
        for s in range(steps):
            t = s / steps
            px.append((int(x1+(x2-x1)*t), int(y1+(y2-y1)*t), ci))
    return px

# Neck curve keyframes (head position moves)
n_mean = [(23,22),(24,20),(24,17),(25,14),(25,12),(24,10),(24,7),(25,5)]
n_left = [(22,22),(22,20),(21,17),(21,14),(22,12),(22,10),(23,7),(24,5)]
n_right= [(24,22),(25,20),(26,17),(26,14),(25,12),(25,10),(24,7),(23,5)]
n_low  = [(23,22),(23,20),(23,17),(24,14),(24,12),(24,10),(24,8),(23,6)]

HEAD = el(24, 4, 5, 4, 1)  # head oval (small)
BEAK_BASE = [(27,3,6),(28,3,6),(29,3,6),(28,4,6),(29,4,7),(30,4,7)]

eyes_open  = [(24,3,4)]
eyes_blink = []

# Beak open (add below base)
bc = []
bs = [(27,5,7)]
bw = [(27,5,7),(28,5,7),(26,5,7)]
bm = [(27,5,7)]

# Wing flutter (adds wing pixels vs base)
wf_low = []
wf_high = [(16,23,5),(16,24,5),(17,25,5)]  # wing lifts

# Leg lift (replace right leg with lifted position)
leg_down = []
leg_up = [(26,28,4),(25,28,4),(26,29,4),(25,29,4)]  # leg bent up

PF = [
    # F0: neck straight, beak closed, wing low
    neck_path(n_mean, 1) + HEAD + BEAK_BASE + eyes_open + bc + wf_low + leg_down,
    # F1: neck left, beak slight, wing low
    neck_path(n_left, 1) + HEAD + [(27,3,6),(28,3,6),(28,4,6),(29,4,7)] + eyes_open + bs + wf_low + leg_down,
    # F2: neck right, beak open, wing high, leg up
    neck_path(n_right, 1) + HEAD + BEAK_BASE + eyes_blink + bw + wf_high + leg_up,
    # F3: neck low (pecking), beak medium, wing low
    neck_path(n_low, 1) + HEAD + [(27,3,6),(28,3,6),(28,4,6),(29,4,7)] + eyes_open + bm + wf_low + leg_down,
    # F4: neck mean, beak closed, wing high
    neck_path(n_mean, 1) + HEAD + BEAK_BASE + eyes_open + bc + wf_high + leg_down + [(22,3,4)],
    # F5: neck left, beak wide, wing high, leg up
    neck_path(n_left, 1) + HEAD + [(27,3,6),(28,3,6),(28,4,6),(29,4,7)] + eyes_blink + bw + wf_high + leg_up + [(23,4,4)],
]

frames = render(B, PF, P)
with open("flamingo.piskel","w") as f:
    json.dump(piskel("flamingo","Flamingo with neck sway and pecking cycle",12,48,48,frames),f,separators=(",",":"))
print("✓ flamingo.piskel — neck sway & peck")

# ================================================================
# 4. GIRAFFE — NECK SWAY & BROWSE
# Neck sways left/right as if reaching for leaves.
# Ears flick. Eyes blink. Legs step in place.
# ================================================================
P = [(0,0,0,0), (245,195,55), (195,145,35), (130,65,20),
     (75,40,10), (30,30,30), (255,255,255)]

B = []
# Body (fixed ellipse)
B += el(23.5, 27, 110, 35, 1)
for x in range(27,34):
    for y in range(22,33):
        if (x-23.5)**2/110+(y-27)**2/35 <= 1: B.append((x,y,2))
# Legs (fixed base)
B += re(15,17,33,42,1) + re(30,32,33,42,1)
B += re(15,17,42,42,4) + re(30,32,42,42,4)
B += re(19,20,0,2,4) + re(27,28,0,2,4)  # horns

# Spots (on body only, not neck which moves)
spots = [(14,22),(15,23),(17,22),(18,24),
         (28,22),(29,23),(31,22),(32,24),
         (15,26),(16,28),(18,27),(19,29),
         (28,26),(29,28),(30,27),(31,29),
         (20,31),(22,30),(25,31),(27,30),
         (23,30),(24,31)]
for x,y in spots: B.append((x,y,3))

# Neck positions (curve changes per frame)
def neck_reach(points, ci):
    """Neck as connected pixels"""
    px = []
    for i in range(len(points)-1):
        x1,y1 = points[i]
        x2,y2 = points[i+1]
        steps = max(abs(x2-x1), abs(y2-y1)) + 1
        for s in range(steps):
            t = s / steps
            px.append((int(x1+(x2-x1)*t), int(y1+(y2-y1)*t), ci))
    return px

n_straight = [(23,22),(23,18),(23,14),(23,10),(23,7),(23,5),(23,3)]
n_left     = [(23,22),(22,18),(21,14),(21,10),(22,7),(23,5),(24,3)]
n_right    = [(23,22),(24,18),(25,14),(25,10),(24,7),(23,5),(22,3)]
n_up       = [(23,22),(23,18),(23,14),(23,10),(24,7),(24,5),(25,3)]

HEAD = el(23, 3, 8, 4, 1)
EARS = [(18,2,1),(19,2,1),(27,2,1),(28,2,1)]
GLINT = [(22,2,6),(24,2,6)]

eyes_open  = [(22,3,5),(24,3,5)]
eyes_blink = [(22,2,5),(24,2,5)]  # narrowed, shifted up

# Neck spots (move with head)
n_spots_center = [(17,8,3),(18,9,3),(19,10,3),(20,11,3),(21,12,3)]
n_spots_left   = [(16,8,3),(16,9,3),(17,10,3),(18,11,3),(19,12,3)]
n_spots_right  = [(18,8,3),(19,9,3),(20,10,3),(21,11,3),(22,12,3)]

MC, MS, MW, MM = [(23,5,5)], [(23,5,5),(24,5,5)], \
                 [(22,5,5),(23,5,5),(24,5,5),(25,5,5)], \
                 [(22,5,5),(23,5,5),(24,5,5)]

PF = [
    # F0: neck straight, eyes open, mouth closed
    neck_reach(n_straight, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_open + n_spots_center + MC,
    # F1: neck left, eyes blink, mouth slight
    neck_reach(n_left, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_blink + n_spots_left + MS,
    # F2: neck right, eyes open, mouth wide
    neck_reach(n_right, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_open + n_spots_right + MW,
    # F3: neck up (reaching high), eyes open, mouth medium
    neck_reach(n_up, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_open + n_spots_center + MM,
    # F4: neck straight, eyes blink, mouth closed
    neck_reach(n_straight, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_blink + n_spots_center + MC + [(20,3,6)],
    # F5: neck left, eyes open, mouth wide
    neck_reach(n_left, 1) + [(x,y,1) for x,y,c in HEAD] + EARS + GLINT + eyes_open + n_spots_left + MW,
]

frames = render(B, PF, P)
with open("giraffe.piskel","w") as f:
    json.dump(piskel("giraffe","Giraffe browsing with neck sway",12,48,48,frames),f,separators=(",",":"))
print("✓ giraffe.piskel — neck sway & browse")

# ================================================================
# 5. CAT — PLAYFUL SWIPE
# Cat bats at something. Tail swishes. Body crouches/springs.
# Ears flick. Eyes open wide (hunting mode) then blink.
# ================================================================
P = [(0,0,0,0), (200,175,150), (150,125,105), (235,215,195),
     (85,60,40), (30,30,30), (105,215,105), (255,255,255)]

B = []
# Body (fixed)
B += el(23.5, 29, 135, 40, 1)
for x in range(29,38):
    for y in range(24,36):
        if (x-23.5)**2/135+(y-29)**2/40 <= 1: B.append((x,y,2))
B += el(23.5, 32, 60, 12, 3)  # belly
B += re(13,16,35,42,1) + re(31,34,35,42,1)  # legs
B += re(13,16,42,42,3) + re(31,34,42,42,3)  # paws
# Head (fixed base — expressions added per frame)
B += re(21,28,14,22,1)  # neck
B += el(24.5, 11, 34, 28, 1)  # head
B += el(24.5, 11.5, 16, 16, 3)  # inner face
# Ears
B += re(17,19,5,6,1) + re(18,19,4,4,1)
B += re(29,31,5,6,1) + re(29,30,4,4,1)
B.append((18,5,3)) and B.append((30,5,3))
# Nose
B.append((24,12,5))
# Whiskers (white)
for x,y,ci in [(18,13,7),(18,14,7),(18,15,7),
               (16,13,7),(17,14,7),(16,15,7),
               (31,13,7),(31,14,7),(31,15,7),
               (33,13,7),(32,14,7),(33,15,7)]:
    B.append((x,y,ci))

# Body stripes (on body only, not moving parts)
for x,y in [(13,25),(14,24),(15,25),(16,24),(17,25),
            (20,30),(21,29),(22,30),
            (26,30),(27,29),(28,30),(29,31),
            (31,25),(32,24),(33,25),
            (14,28),(16,27),(31,28),(33,27)]:
    B.append((x,y,4))

# --- TAIL positions (per frame) ---
t_swish_l = el(6, 29, 10, 6, 1)  # tail left
t_swish_r = el(10, 29, 10, 6, 1)  # tail right
t_up      = el(6, 25, 8, 12, 1)   # tail up (excited)
t_mid     = el(8, 30, 12, 8, 1)   # tail neutral

# Tail stripes (move with tail)
ts_l = [(4,29,4),(5,28,4),(3,30,4)]
ts_r = [(8,29,4),(9,28,4),(7,30,4)]
ts_up = [(4,24,4),(5,23,4)]

# --- PAW positions (swipe) ---
paw_neutral = []
paw_swipe_l = [(15,34,1),(14,33,1),(13,32,1),(12,31,1),(11,30,1)]  # left arm extends
paw_swipe_r = [(32,34,1),(33,33,1),(34,32,1),(35,31,1),(36,30,1)]  # right arm extends
paw_retract = [(14,36,1)]

# Head tilt (shift ear + face position)
tilt_l = [(17,5,1),(18,5,1),(18,4,4)]  # left ear shifts
tilt_r = [(31,5,1),(30,5,1),(30,4,4)]  # right ear shifts

eyes_open  = [(21,10,6),(22,10,6),(27,10,6),(28,10,6),
              (21,9,5),(22,9,5),(27,9,5),(28,9,5),
              (22,10,7),(28,10,7)]
eyes_wide  = [(20,10,6),(21,10,6),(22,10,6),(23,10,6),  # BIG eyes (hunting mode)
              (26,10,6),(27,10,6),(28,10,6),(29,10,6),
              (21,9,5),(22,9,5),(27,9,5),(28,9,5),
              (22,10,7),(28,10,7)]
eyes_blink = [(21,10,5),(22,10,5),(27,10,5),(28,10,5)]

MC, MS, MW, MM = [(24,13,5)], [(24,13,5),(25,13,5)], \
                 [(22,13,5),(23,13,5),(24,13,5),(25,13,5),(26,13,5)], \
                 [(23,13,5),(24,13,5),(25,13,5)]

PF = [
    # F0: NEUTRAL — tail mid, paw neutral, eyes open, mouth closed
    t_mid + ts_r + paw_neutral + eyes_open + MC,
    # F1: SWISH LEFT — tail left, head tilt, paw swipe
    t_swish_l + ts_l + paw_swipe_l + eyes_wide + MS + tilt_l,
    # F2: SPRING — tail up, paw retract, eyes blink, mouth wide (meow!)
    t_up + ts_up + paw_retract + eyes_blink + MW + tilt_l,
    # F3: SWISH RIGHT — tail right, paw neutral, eyes open, mouth medium
    t_swish_r + ts_r + paw_neutral + eyes_open + MM,
    # F4: CROUCH — tail mid, paw swipe right, eyes wide, mouth closed
    t_mid + ts_r + paw_swipe_r + eyes_wide + MC + tilt_r,
    # F5: POUNCE — tail up, paw neutral, eyes blink, mouth meow
    t_up + ts_up + paw_neutral + eyes_blink + MW,
]

frames = render(B, PF, P)
with open("cat.piskel","w") as f:
    json.dump(piskel("cat","Playful cat with tail swish and swipe",12,48,48,frames),f,separators=(",",":"))
print("✓ cat.piskel — playful swipe cycle")

# ================================================================
# VERIFY
# ================================================================
print()
all_ok = True
for name in ["owl.piskel","t-rex.piskel","flamingo.piskel","giraffe.piskel","cat.piskel"]:
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
        hashes.append(hashlib.md5(frame.tobytes()).hexdigest()[:8])
    unique = len(set(hashes))
    ok = "✓" if unique >= 6 else "⚠"
    if unique < 6: all_ok = False
    print(f"{ok} {name}: {size}B, {unique}/6 unique {hashes}")

print(f"\n{'All 6/6 unique frames!' if all_ok else 'Some still need work.'}")
