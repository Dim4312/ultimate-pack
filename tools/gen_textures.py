#!/usr/bin/env python3
"""Generate 16x16 item textures for Tempering Kits and Boss Echoes.

Run from the repo root: python3 tools/gen_textures.py
"""
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "kubejs/assets/ultimate/textures/item"

# Kit: a leather roll with a hammer and a whetstone. The gem in the middle shows the tier.
KIT = [
    "................",
    "..........HH....",
    ".........HHHH...",
    "..........HH....",
    "..........hh....",
    "...LLLLLLLhhLL..",
    "..LllllllllhlL..",
    "..LlSSSSllhllL..",
    "..LlsssSlGhllL..",
    "..LllllllgglL...",
    "..LllllllllllL..",
    "..LLLLLLLLLLLL..",
    "...dddddddddd...",
    "................",
    "................",
    "................",
]
TIER_GEMS = {
    1: ((230, 140, 90), (170, 90, 55)),    # copper
    2: ((240, 200, 90), (180, 140, 50)),   # brass
    3: ((120, 230, 230), (60, 160, 170)),  # diamond
    4: ((90, 220, 120), (40, 150, 70)),    # emerald
    5: ((120, 200, 255), (60, 120, 200)),  # prismarine / sea
    6: ((255, 120, 60), (190, 60, 30)),    # forge fire
    7: ((230, 50, 80), (140, 20, 45)),     # crimson / nether
    8: ((180, 90, 235), (110, 45, 165)),   # ender
    9: ((245, 230, 255), (185, 150, 215)), # end rod
    10: ((255, 80, 220), (170, 25, 150)),  # dragon
}

# Echo: a hollow crystal with a colored core.
ECHO = [
    "................",
    ".......OO.......",
    "......OccO......",
    ".....OcCCcO.....",
    "....OcCwCCcO....",
    "....OcCCCCcO....",
    "...OcCCKKCCcO...",
    "...OcCKkkKCcO...",
    "...OcCKkkKCcO...",
    "...OcCCKKCCcO...",
    "....OcCCCCcO....",
    "....OcCCCCcO....",
    ".....OcCCcO.....",
    "......OccO......",
    ".......OO.......",
    "................",
]
ECHO_CORES = {
    "wroughtnaut": (170, 120, 90),
    "frostmaw": (200, 240, 255),
    "umvuthi": (255, 200, 60),
    "maledictus": (120, 200, 255),
    "ancient_remnant": (230, 190, 110),
    "leviathan": (60, 120, 220),
    "harbinger": (230, 50, 50),
    "netherite_monstrosity": (200, 70, 35),
    "ignis": (255, 175, 40),
    "ender_guardian": (190, 80, 255),
}

# Return Gate block: a purpur frame around a starry void with a glowing ring.
GATE = [
    "PPPPPPPPPPPPPPPP",
    "PppppppppppppppP",
    "PpVVVVVVVVVVVVpP",
    "PpVVsVVVVVVVsVpP",
    "PpVVVVRRRRVVVVpP",
    "PpVVVRrrrrRVVVpP",
    "PpVsRrVVVVrRVVpP",
    "PpVVRrVwVVrRVVpP",
    "PpVVRrVVVVrRsVpP",
    "PpVVRrVVVVrRVVpP",
    "PpVVVRrrrrRVVVpP",
    "PpVVVVRRRRVVVVpP",
    "PpVsVVVVVVVVsVpP",
    "PpVVVVVVVVVVVVpP",
    "PppppppppppppppP",
    "PPPPPPPPPPPPPPPP",
]
BLOCKS = OUT.parent / "block"


def draw(pattern, palette):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch in palette:
                img.putpixel((x, y), palette[ch] + (255,))
    return img


def shade(color, f):
    return tuple(max(0, min(255, int(c * f))) for c in color)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for tier, (gem, gem_dark) in TIER_GEMS.items():
        palette = {
            "L": (80, 50, 30), "l": (140, 95, 60), "d": (50, 30, 20),
            "H": (150, 150, 160), "h": (110, 75, 45),
            "S": (120, 120, 125), "s": (90, 90, 95),
            "G": gem, "g": gem_dark,
        }
        draw(KIT, palette).save(OUT / f"tempering_kit_{tier}.png")
    for boss, core in ECHO_CORES.items():
        palette = {
            "O": (20, 40, 50), "c": (40, 90, 100), "C": (70, 150, 160), "w": (220, 255, 255),
            "K": core, "k": shade(core, 1.25),
        }
        draw(ECHO, palette).save(OUT / f"echo_{boss}.png")
    BLOCKS.mkdir(parents=True, exist_ok=True)
    draw(GATE, {
        "P": (120, 80, 120), "p": (170, 120, 170), "V": (15, 10, 30), "s": (230, 220, 255),
        "R": (200, 90, 255), "r": (120, 50, 190), "w": (255, 255, 255),
    }).save(BLOCKS / "return_gate.png")
    print(f"wrote textures to {OUT} and {BLOCKS}")


if __name__ == "__main__":
    main()
