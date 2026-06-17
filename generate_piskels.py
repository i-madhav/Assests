#!/usr/bin/env python3
"""
Generate 5 unique pixel-art characters as .piskel files with talking animations.
Each character: 32x32, 6 frames of talking motion, distinct visual style.
"""

import json
import base64
import io
from PIL import Image
import os

def make_character_piskel(name, description, palette, mouth_frames, hair_pixels, eye_pixels, body_pixels, bg_color=(0,0,0,0)):
    """
    Create a .piskel file with a talking animation.
    
    Args:
        name: Character name
        description: Description text
        palette: list of (r,g,b) colors for the character
        mouth_frames: list of 6 mouth shapes (each is list of (x,y) pixel positions relative to a mouth center)
        hair_pixels: list of (x,y,color_index) for hair pixels
        eye_pixels: list of (x,y,color_index) for eye pixels
        body_pixels: list of (x,y,color_index) for body pixels
    """
    width, height = 32, 32
    num_frames = len(mouth_frames)
    
    # Build the full sprite for each frame
    frame_images = []
    for frame_idx in range(num_frames):
        img = Image.new("RGBA", (width, height), bg_color)
        pixels = img.load()
        
        # Base skin/body (fixed across all frames)
        for x, y, ci in body_pixels:
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = palette[ci] + (255,)
        
        # Hair (fixed)
        for x, y, ci in hair_pixels:
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = palette[ci] + (255,)
        
        # Eyes (fixed)
        for x, y, ci in eye_pixels:
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = palette[ci] + (255,)
        
        # Mouth (varies per frame)
        for x, y, ci in mouth_frames[frame_idx]:
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = palette[ci] + (255,)
        
        frame_images.append(img)
    
    # Create a sprite strip: all 6 frames side by side
    strip_width = width * num_frames
    strip = Image.new("RGBA", (strip_width, height), bg_color)
    for i, img in enumerate(frame_images):
        strip.paste(img, (i * width, 0))
    
    # Save as PNG in memory
    buf = io.BytesIO()
    strip.save(buf, format="PNG")
    png_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    data_url = f"data:image/png;base64,{png_b64}"
    
    # Build Piskel JSON
    piskel_data = {
        "modelVersion": 2,
        "piskel": {
            "name": name,
            "description": description,
            "fps": 6,
            "height": height,
            "width": width,
            "layers": [
                json.dumps({
                    "name": "Layer 1",
                    "opacity": 1,
                    "frameCount": num_frames,
                    "chunks": [
                        {
                            "layout": [[i] for i in range(num_frames)],
                            "base64PNG": data_url
                        }
                    ]
                })
            ],
            "hiddenFrames": []
        }
    }
    
    return piskel_data


# ===================================================================
# Define 5 Characters
# ===================================================================

# --- Character 1: BMO (Adventure Time style robot) ---
# Palette: 0=bg, 1=light green body, 2=darker green, 3=white screen, 4=blue eyes, 5=black mouth, 6=green accent
bmo_palette = [
    (0,0,0,0),     # 0: transparent bg
    (100,210,100), # 1: light green body
    (60,160,60),   # 2: dark green body
    (200,240,200), # 3: screen green
    (50,50,200),   # 4: blue eyes
    (20,20,20),    # 5: dark (mouth)
    (140,230,140), # 6: accent green
]

# Body: a square robot shape (BMO)
bmo_body = []
# Main body rectangle
for x in range(6, 26):
    for y in range(10, 28):
        bmo_body.append((x, y, 1))
# Inner screen area
for x in range(9, 23):
    for y in range(13, 22):
        bmo_body.append((x, y, 3))
# Bottom border accent
for x in range(6, 26):
    bmo_body.append((x, 26, 2))
    bmo_body.append((x, 27, 2))
# Top accent
for x in range(6, 26):
    bmo_body.append((x, 10, 2))
# Side accents
for y in range(10, 28):
    bmo_body.append((6, y, 2))
    bmo_body.append((25, y, 2))
# Corner buttons (bottom)
for x in [10, 14, 18, 22]:
    bmo_body.append((x, 24, 6))
    bmo_body.append((x, 25, 6))

# Eyes (on the screen area)
bmo_eyes = []
for y in [15, 16]:
    for x in [12, 13]:
        bmo_eyes.append((x, y, 4))
    for x in [19, 20]:
        bmo_eyes.append((x, y, 4))

# No hair for BMO
bmo_hair = []

# Mouth frames - talking shapes inside the screen
bmo_mouth_frames = []
# A small square mouth that changes shape across 6 frames
mouth_centers = [(16, 18), (16, 18), (16, 18), (16, 19), (16, 18), (16, 19)]
mouth_shapes = [
    [(16,18,5)],                                    # closed
    [(16,18,5),(15,18,5),(17,18,5)],               # slightly open
    [(15,18,5),(16,18,5),(17,18,5),(15,19,5),(16,19,5),(17,19,5)],  # open
    [(16,18,5),(16,19,5)],                          # narrow open
    [(15,18,5),(16,18,5),(17,18,5)],               # slightly open
    [(15,18,5),(16,18,5),(17,18,5),(15,19,5),(16,19,5),(17,19,5)],  # open again
]

for shape in mouth_shapes:
    bmo_mouth_frames.append(shape)

bmo_data = make_character_piskel(
    "BMO",
    "BMO the sentient gaming console — talking animation",
    bmo_palette, bmo_mouth_frames, bmo_hair, bmo_eyes, bmo_body
)


# --- Character 2: Totoro (My Neighbor Totoro style) ---
totoro_palette = [
    (0,0,0,0),
    (140,140,140),  # 1: grey body
    (100,100,110),  # 2: dark grey belly accent
    (220,220,230),  # 3: light belly
    (60,60,70),     # 4: dark eyes
    (180,140,120),  # 5: nose
    (20,20,20),     # 6: dark detail
]

totoro_body = []
# Round body
for x in range(4, 28):
    for y in range(8, 30):
        dx, dy = x - 16, y - 20
        dist = (dx*dx + dy*dy) ** 0.5
        if dist < 12:
            totoro_body.append((x, y, 1))
# Belly
for x in range(9, 23):
    for y in range(14, 28):
        dx, dy = x - 16, y - 21
        dist = (dx*dx + dy*dy) ** 0.5
        if dist < 7:
            totoro_body.append((x, y, 3))
# Ears
for x, y in [(6,6),(7,5),(8,6),(7,7),(24,6),(23,5),(22,6),(23,7)]:
    totoro_body.append((x, y, 1))
# Little feet
for x in range(8, 13):
    totoro_body.append((x, 28, 1))
for x in range(19, 24):
    totoro_body.append((x, 28, 1))
# Arms
for x in range(2, 5):
    for y in range(18, 22):
        totoro_body.append((x, y, 1))
for x in range(27, 30):
    for y in range(18, 22):
        totoro_body.append((x, y, 1))

# Nose
totoro_hair = []  # no traditional hair - Totoro has the belly stripes instead
for x in range(9, 23):
    for y in range(20, 22):
        totoro_body.append((x, y, 2))

# Eyes (big round)
totoro_eyes = []
for y in [14, 15]:
    for x in [12, 13]:
        totoro_eyes.append((x, y, 4))
    for x in [19, 20]:
        totoro_eyes.append((x, y, 4))

# Whiskers
for cx in [10]:
    totoro_body.append((8, 19, 6))
    totoro_body.append((7, 20, 6))
    totoro_body.append((8, 21, 6))
for cx in [22]:
    totoro_body.append((24, 19, 6))
    totoro_body.append((25, 20, 6))
    totoro_body.append((24, 21, 6))

# Nose dot
totoro_eyes.append((16, 17, 5))

# Mouth frames
totoro_mouth_frames = [
    [(16,20,6)],                                 # closed smile
    [(16,20,6),(15,20,6),(17,20,6)],            # open slightly
    [(15,20,6),(16,20,6),(17,20,6),(15,21,6),(16,21,6),(17,21,6)],  # big smile
    [(16,20,6),(15,21,6),(16,21,6),(17,21,6)],  # open down
    [(16,20,6),(15,20,6),(17,20,6)],            # medium
    [(15,20,6),(16,20,6),(17,20,6),(15,21,6),(16,21,6),(17,21,6)],  # big again
]

totoro_data = make_character_piskel(
    "Totoro",
    "Totoro with a talking animation — inspired by My Neighbor Totoro",
    totoro_palette, totoro_mouth_frames, totoro_hair, totoro_eyes, totoro_body
)


# --- Character 3: Knight (Medieval RPG) ---
knight_palette = [
    (0,0,0,0),
    (180,180,190),  # 1: silver armor
    (130,130,140),  # 2: dark armor
    (220,180,130),  # 3: skin
    (200,50,50),    # 4: red plume
    (170,130,90),   # 5: belt/brown
    (80,80,90),     # 6: visor slit
    (200,200,210),  # 7: highlight
]

knight_body = []
# Helmet
for x in range(8, 24):
    for y in range(4, 14):
        knight_body.append((x, y, 1))
# Helmet top curve
for x in range(7, 25):
    knight_body.append((x, 3, 1))
# Visor
for x in range(9, 23):
    for y in range(8, 12):
        knight_body.append((x, y, 2))
# Visor slit
for y in [10, 11]:
    for x in [13, 14, 17, 18]:
        knight_body.append((x, y, 6))
# Plume (red)
for x in [14, 15, 16, 17]:
    for y in [0, 1, 2]:
        knight_body.append((x, y, 4))
knight_body.append((15, 1, 4))
knight_body.append((16, 1, 4))
# Body armor
for x in range(7, 25):
    for y in range(14, 24):
        knight_body.append((x, y, 1))
# Breastplate detail
for x in range(9, 23):
    for y in range(14, 18):
        knight_body.append((x, y, 7))
# Belt
for x in range(7, 25):
    for y in [23, 24]:
        knight_body.append((x, y, 5))
# Legs
for x in range(9, 15):
    for y in range(25, 30):
        knight_body.append((x, y, 2))
for x in range(17, 23):
    for y in range(25, 30):
        knight_body.append((x, y, 2))
# Boots
for x in range(8, 16):
    for y in [29, 30]:
        knight_body.append((x, y, 1))
for x in range(16, 24):
    for y in [29, 30]:
        knight_body.append((x, y, 1))
# Arms
for x in range(2, 7):
    for y in range(14, 22):
        knight_body.append((x, y, 2))
for x in range(25, 30):
    for y in range(14, 22):
        knight_body.append((x, y, 2))
# Sword (right hand)
for x in [29]:
    for y in range(8, 14):
        knight_body.append((x, y, 1))
knight_body.append((30, 9, 1))
knight_body.append((30, 10, 1))
knight_body.append((30, 11, 1))
# Shield (left hand)  
for x in range(0, 5):
    for y in range(16, 24):
        dx, dy = x - 2, y - 20
        if (dx*dx + dy*dy) ** 0.5 < 5:
            knight_body.append((x, y, 4))

knight_hair = []  # helmet covers it
knight_eyes = []  # hidden behind visor

# Mouth frames (talking through the visor slit)
knight_mouth_frames = [
    [(15, 11, 6), (16, 11, 6)],
    [(14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6)],
    [(13, 11, 6), (14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6), (18, 11, 6)],
    [(14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6)],
    [(15, 11, 6), (16, 11, 6)],
    [(13, 11, 6), (14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6), (18, 11, 6)],
]

knight_data = make_character_piskel(
    "Knight",
    "Armored knight with a talking animation — medieval RPG style",
    knight_palette, knight_mouth_frames, knight_hair, knight_eyes, knight_body
)


# --- Character 4: Alien (Sci-Fi) ---
alien_palette = [
    (0,0,0,0),
    (100,220,100),  # 1: green skin
    (60,180,60),    # 2: dark green
    (180,255,180),  # 3: light green
    (200,200,50),   # 4: yellow eyes
    (150,50,200),   # 5: purple accents
    (20,20,20),     # 6: dark detail
    (255,100,100),  # 7: antenna glow
]

alien_body = []
# Head (oval)
for x in range(6, 26):
    for y in range(4, 18):
        dx, dy = x - 16, y - 11
        dist = (dx*dx/36 + dy*dy/25) ** 0.5
        if dist < 1:
            alien_body.append((x, y, 1))
# Head highlight
for x in range(9, 23):
    for y in range(5, 10):
        dx, dy = x - 16, y - 8
        dist = (dx*dx/25 + dy*dy/16) ** 0.5
        if dist < 0.8:
            alien_body.append((x, y, 3))

# Antennae
for x_off, y_off in [(-7, -5), (7, -5)]:
    cx, cy = 16 + x_off, 10 + y_off
    alien_body.append((cx, cy, 7))
    if cy > 0:
        alien_body.append((cx, cy - 1, 2))

# Neck lines
for x in range(12, 20):
    for y in [18, 19]:
        alien_body.append((x, y, 2))

# Body
for x in range(8, 24):
    for y in range(20, 28):
        alien_body.append((x, y, 1))
# Body markings (purple)
for x in [10, 21]:
    for y in range(22, 26):
        alien_body.append((x, y, 5))

# Arms
for x in range(3, 8):
    for y in range(21, 26):
        alien_body.append((x, y, 2))
for x in range(24, 29):
    for y in range(21, 26):
        alien_body.append((x, y, 2))

# Big eyes
alien_eyes = []
for x in [11, 12]:
    for y in [10, 11]:
        dx, dy = x - 11.5, y - 10.5
        if (dx*dx + dy*dy) ** 0.5 < 1.5:
            alien_eyes.append((x, y, 4))
for x in [19, 20]:
    for y in [10, 11]:
        dx, dy = x - 19.5, y - 10.5
        if (dx*dx + dy*dy) ** 0.5 < 1.5:
            alien_eyes.append((x, y, 4))
# Pupils
alien_eyes.append((12, 10, 6))
alien_eyes.append((20, 10, 6))

alien_hair = []  # antennae instead

# Mouth frames (alien mouth below eyes)
alien_mouth_frames = [
    [(14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6)],
    [(13, 14, 6), (14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6), (18, 14, 6)],
    [(12, 14, 6), (13, 14, 6), (14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6), (18, 14, 6), (19, 14, 6)],
    [(14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6)],
    [(13, 14, 6), (14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6), (18, 14, 6)],
    [(12, 14, 6), (13, 14, 6), (14, 14, 6), (15, 14, 6), (16, 14, 6), (17, 14, 6), (18, 14, 6), (19, 14, 6)],
]

alien_data = make_character_piskel(
    "Alien",
    "Extraterrestrial with a talking animation — sci-fi alien design",
    alien_palette, alien_mouth_frames, alien_hair, alien_eyes, alien_body
)


# --- Character 5: Witch (Fantasy / Spooky) ---
witch_palette = [
    (0,0,0,0),
    (80,60,100),    # 1: dark purple robe
    (60,40,80),     # 2: darker robe
    (110,80,130),   # 3: medium purple
    (220,200,180),  # 4: skin
    (60,180,60),    # 5: green magic
    (200,160,80),   # 6: yellow stars
    (160,100,60),   # 7: brown hair
]

witch_body = []
# Hat (classic pointed witch hat)
for x in range(6, 26):
    for y in range(0, 6):
        witch_body.append((x, y, 1))
# Hat cone
for x in range(9, 23):
    for y in range(6, 8):
        witch_body.append((x, y, 1))
for x in range(11, 21):
    for y in range(8, 12):
        witch_body.append((x, y, 1))
for x in range(13, 19):
    for y in range(12, 16):
        witch_body.append((x, y, 1))
# Hat brim (slightly wider)
for x in range(4, 28):
    for y in [16, 17]:
        witch_body.append((x, y, 2))
# Hat band
for x in range(5, 27):
    for y in [15]:
        witch_body.append((x, y, 3))

# Face
for x in range(8, 24):
    for y in range(18, 26):
        witch_body.append((x, y, 4))

# Hair (peeking from under hat)
witch_hair = []
for x in range(5, 10):
    for y in range(16, 22):
        witch_hair.append((x, y, 7))
for x in range(22, 27):
    for y in range(16, 22):
        witch_hair.append((x, y, 7))

# Body/robe
for x in range(6, 26):
    for y in range(26, 32):
        witch_body.append((x, y, 1))
# Robe details
for x in range(7, 25):
    for y in [26, 27, 30]:
        witch_body.append((x, y, 2))
# Stars on robe
for x, y in [(10, 28), (22, 28), (16, 30)]:
    witch_body.append((x, y, 6))

# Magic wand (hand area)
for x in [26, 27, 28]:
    for y in [26, 27]:
        witch_body.append((x, y, 5))
witch_body.append((29, 25, 5))
witch_body.append((30, 24, 5))
# Sparkle at wand tip
witch_body.append((31, 23, 6))

# Eyes
witch_eyes = []
for x in [12, 13]:
    for y in [20, 21]:
        witch_eyes.append((x, y, 1))
for x in [19, 20]:
    for y in [20, 21]:
        witch_eyes.append((x, y, 1))

# Mouth frames
witch_mouth_frames = [
    [(15, 23, 12), (16, 23, 12), (17, 23, 1)],   # closed smirk
    [(14, 23, 12), (15, 23, 12), (16, 23, 12), (17, 23, 12), (18, 23, 1)],  # slight open
    [(13, 23, 12), (14, 23, 12), (15, 23, 12), (16, 23, 12), (17, 23, 12), (18, 23, 12), (19, 23, 1)],  # open
    [(15, 23, 12), (16, 23, 12), (17, 23, 1)],
    [(14, 23, 12), (15, 23, 12), (16, 23, 12), (17, 23, 12), (18, 23, 1)],
    [(13, 23, 12), (14, 23, 12), (15, 23, 12), (16, 23, 12), (17, 23, 12), (18, 23, 12), (19, 23, 1)],
]

# Fix mouth frames to use valid palette colors
witch_mouth_frames = [
    [(16, 23, 3)],                                    # closed
    [(15, 23, 3), (16, 23, 3), (17, 23, 3)],         # slight open
    [(14, 23, 3), (15, 23, 3), (16, 23, 3), (17, 23, 3), (18, 23, 3)],  # open
    [(15, 23, 3), (16, 23, 3), (17, 23, 3)],         # back to slight
    [(16, 23, 3)],                                    # closed
    [(14, 23, 3), (15, 23, 3), (16, 23, 3), (17, 23, 3), (18, 23, 3)],  # open
]

witch_data = make_character_piskel(
    "Witch",
    "Enchanting witch with a talking animation — fantasy spooky style",
    witch_palette, witch_mouth_frames, witch_hair, witch_eyes, witch_body
)


# ===================================================================
# Write all 5 .piskel files
# ===================================================================

output_dir = "/home/madhavsharma/repos/Assests"

characters = [
    ("BMO.piskel", bmo_data),
    ("Totoro.piskel", totoro_data),
    ("Knight.piskel", knight_data),
    ("Alien.piskel", alien_data),
    ("Witch.piskel", witch_data),
]

for filename, data in characters:
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    size = os.path.getsize(filepath)
    print(f"Created: {filepath} ({size} bytes)")

print("\nDone! 5 .piskel files generated.")
