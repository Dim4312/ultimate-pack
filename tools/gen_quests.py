#!/usr/bin/env python3
"""Generate the FTB Quests book for Ultimate Pack.

Run from the repo root:  python3 tools/gen_quests.py
Writes config/ftbquests/quests/. Quest IDs are derived from stable keys, so
re-running keeps everyone's progress. Never rename a quest key once released.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "config/ftbquests/quests"


# ---------------------------------------------------------------- SNBT writer

class L(int):
    """Long tag (1L)."""


class D(float):
    """Double tag (1.0d)."""


def snbt(value, indent=0):
    tab = "\t" * indent
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, L):
        return f"{int(value)}L"
    if isinstance(value, D):
        return f"{float(value)}d"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value}d"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, list):
        if not value:
            return "[ ]"
        inner = "\n".join(tab + "\t" + snbt(v, indent + 1) for v in value)
        return "[\n" + inner + "\n" + tab + "]"
    if isinstance(value, dict):
        inner = "\n".join(f"{tab}\t{k}: {snbt(v, indent + 1)}" for k, v in sorted(value.items()))
        return "{\n" + inner + "\n" + tab + "}"
    raise TypeError(type(value))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(snbt(value) + "\n", encoding="utf-8")


def qid(key):
    """Stable 16-hex-digit ID from a key. The first digit is 1-7 so the ID fits a signed long."""
    h = hashlib.sha1(key.encode()).hexdigest().upper()
    return "1234567"[int(h[0], 16) % 7] + h[1:16]


LANG = {}


# ---------------------------------------------------------------- tasks / rewards

def item(id, count=1, consume=False):
    t = {"type": "item", "item": {"count": 1, "id": id}}
    if count > 1:
        t["count"] = L(count)
    if consume:
        t["consume_items"] = True
    return t


def kill(entity, count=1):
    return {"type": "kill", "entity": entity, "value": L(count)}


def structure(id):
    return {"type": "structure", "structure": id}


def biome(id):
    return {"type": "biome", "biome": id}


def dimension(id):
    return {"type": "dimension", "dimension": id}


def stage(name):
    return {"type": "gamestage", "stage": name}


def check(title):
    return {"type": "checkmark", "_title": title}


def r_xp(amount):
    return {"type": "xp", "xp": amount}


def r_item(id, count=1):
    r = {"type": "item", "item": {"count": 1, "id": id}}
    if count > 1:
        r["count"] = count
    return r


def r_stage(name):
    return {"type": "gamestage", "stage": name}


# ---------------------------------------------------------------- quest builder

class Chapter:
    def __init__(self, key, title, icon, group="", subtitle=None):
        self.key = key
        self.id = qid("chapter:" + key)
        self.title = title
        self.icon = icon
        self.group = group
        self.subtitle = subtitle
        self.quests = []
        self.by_key = {}

    def quest(self, key, title, x, y, tasks, desc=(), rewards=(), deps=(), icon=None,
              subtitle=None, shape=None, size=None, optional=False, min_deps=None):
        full_key = f"{self.key}:{key}"
        q = {"id": qid("quest:" + full_key), "x": D(x), "y": D(y)}
        q_tasks = []
        for i, t in enumerate(tasks):
            t = dict(t)
            t["id"] = qid(f"task:{full_key}:{i}")
            title_override = t.pop("_title", None)
            if title_override:
                LANG[f"task.{t['id']}.title"] = title_override
            q_tasks.append(t)
        q["tasks"] = q_tasks
        if rewards:
            q["rewards"] = [dict(r, id=qid(f"reward:{full_key}:{i}")) for i, r in enumerate(rewards)]
        if deps:
            q["dependencies"] = [self.by_key[d]["id"] if ":" not in d else qid("quest:" + d) for d in deps]
        if icon:
            q["icon"] = {"id": icon}
        if shape:
            q["shape"] = shape
        if size:
            q["size"] = D(size)
        if optional:
            q["optional"] = True
        if min_deps:
            q["min_required_dependencies"] = min_deps
        LANG[f"quest.{q['id']}.title"] = title
        if subtitle:
            LANG[f"quest.{q['id']}.quest_subtitle"] = subtitle
        if desc:
            LANG[f"quest.{q['id']}.quest_desc"] = list(desc)
        self.quests.append(q)
        self.by_key[key] = q
        return q

    def trial(self, phase, x, y, tasks, desc, deps, icon, extra_rewards=(), min_deps=None):
        """End-of-phase Trial: teaches Tempering N and gives one free kit."""
        return self.quest(
            "trial", f"&6Trial of Phase {phase}", x, y, tasks,
            desc=list(desc) + [
                "",
                f"&eReward:&r you learn &6Tempering {ROMAN[phase]}&r and get your first Tempering Kit {ROMAN[phase]}.",
                f"From now on you can craft that kit and temper any weapon or staff up to level {ROMAN[phase]}.",
            ],
            rewards=[r_stage(f"ultimate_tier_{phase}"), r_item(f"ultimate:tempering_kit_{phase}"), r_xp(200 * phase)]
                    + list(extra_rewards),
            deps=deps, icon=icon, shape="gear", size=2.0, min_deps=min_deps,
            subtitle=f"Learn Tempering {ROMAN[phase]}",
        )

    def to_snbt(self, order):
        LANG[f"chapter.{self.id}.title"] = self.title
        if self.subtitle:
            LANG[f"chapter.{self.id}.chapter_subtitle"] = [self.subtitle]
        return {
            "default_hide_dependency_lines": False,
            "default_quest_shape": "",
            "filename": self.key,
            "group": self.group,
            "icon": {"id": self.icon},
            "id": self.id,
            "order_index": order,
            "quest_links": [],
            "quests": self.quests,
        }


ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
GROUP_ACT1 = qid("group:act1")
GROUP_ACT2 = qid("group:act2")
GROUP_ACT3 = qid("group:act3")
GROUP_ACT4 = qid("group:act4")
GROUP_ACT5 = qid("group:act5")
GROUP_SIDE = qid("group:side")
GROUPS = [
    (GROUP_ACT1, "&aAct I — The Land"), (GROUP_ACT2, "&bAct II — The Frontier"), (GROUP_ACT3, "&cAct III — The Nether"),
    (GROUP_ACT4, "&5Act IV — The End: New World"), (GROUP_ACT5, "&dAct V — The End: The Way Back"),
    (GROUP_SIDE, "&eSide Quests & Discoveries"),
]


# ---------------------------------------------------------------- content

def welcome():
    c = Chapter("welcome", "&eWelcome", "ftbquests:book",
                subtitle="Read this first. It takes two minutes.")
    c.quest("welcome", "&eWelcome to Ultimate Pack", 0, 0, [dimension("minecraft:overworld")],
            desc=[
                "&6One world. Play together. Create, don't grind.",
                "",
                "The book is split into &aPhases&r. Each Phase sends you somewhere new and ends with a &6Trial&r.",
                "Beating a Trial teaches you the next level of &6Tempering&r, the only power upgrade in the pack.",
                "",
                "There are only three worlds: the &2Overworld&r, the &cNether&r and the &5End&r.",
                "The Nether and the End start &csealed&r. You open them together, for the whole server, by beating bosses.",
                "",
                "Not in the mood for the story? The &eSide Quests&r chapters (biomes, dungeons, cooking, magic, gear) are all optional.",
            ],
            rewards=[r_xp(50)], shape="pentagon", size=3.0, icon="ftbquests:book")
    c.quest("no_classes", "Everyone fights, everyone casts", -3, 2, [check("Got it")],
            desc=[
                "There are no classes. Pick up a sword &oand&r a spellbook.",
                "",
                "&cWeapons:&r Simply Swords, Better Combat (combos, dual wield), Combat Roll (dodge with &eR&r).",
                "&9Magic:&r Iron's Spells 'n Spellbooks (find scrolls, inscribe them into a spellbook)",
                "and Ars Nouveau (design your own spells).",
                "",
                "Every Phase gives a weapon goal and a magic goal. Lean wherever you like, and change your mind any time.",
            ], deps=["welcome"], icon="minecraft:iron_sword", rewards=[r_xp(20)])
    c.quest("tempering", "&6Tempering", 0, 2.5, [check("Got it")],
            desc=[
                "&6Tempering&r gives a weapon or staff &e+12% damage&r and &e+6% spell power&r per level.",
                "",
                "1. Beat a Phase &6Trial&r. You &olearn&r that Tempering level forever.",
                "2. Craft a &6Tempering Kit&r of that level (normal materials, see JEI).",
                "3. Hold the weapon in one hand and the kit in the other, then right-click.",
                "",
                "Found a cooler sword later? Temper it too. Your knowledge stays, a kit only costs materials.",
                "No grinding, no random rolls. Tempering X is about 2.2x damage, and that's the cap.",
            ], deps=["welcome"], icon="ultimate:tempering_kit_1", rewards=[r_xp(20)])
    c.quest("together", "Play together", 3, 2, [check("Got it")],
            desc=[
                "&aBoss credit is shared:&r everyone within 64 blocks when a boss dies gets credit for it.",
                "&aBosses scale:&r more players means each hit does a bit less, so a group still gets a real fight.",
                "&aLoot is per player:&r every chest has its own loot for each player (Lootr). Latecomers still find loot.",
                "&aGraves:&r if you die, your items wait in a grave.",
                "",
                "Want to share quest progress with a friend? Make a party: &e/ftbteams party create&r.",
            ], deps=["welcome"], icon="minecraft:totem_of_undying", rewards=[r_xp(20)])
    c.quest("guides", "Lost? JEI and Ponder", -1.5, 4.5, [check("Got it")],
            desc=[
                "&eJEI&r (item list on the right): hover an item and press &eR&r for its recipe or &eU&r for its uses.",
                "&ePonder&r: hold &eW&r while hovering any Create item to see an animated guide.",
                "&eJade&r shows what you are looking at, at the top of the screen.",
                "&eWaystones&r: find them in villages or craft them to travel between places you've been.",
            ], deps=["welcome"], icon="create:wrench", rewards=[r_xp(20)])
    c.quest("echoes", "&dBoss Echoes", 1.5, 4.5, [check("Got it")],
            desc=[
                "Someone already killed the boss you need? No problem.",
                "Every quest boss has a craftable &dEcho&r. Right-click it where that boss lives (Overworld, Nether or End) to call it to you.",
                "Echoes need an &dEcho Shard&r, which you'll find in Ancient Cities (Phase 3). See JEI for recipes.",
            ], deps=["welcome"], icon="minecraft:echo_shard", rewards=[r_xp(20)])
    return c


def phase1():
    c = Chapter("phase_1_arrival", "&a1. Arrival", "minecraft:oak_sapling", GROUP_ACT1,
                subtitle="Settle in. First machines, first fights, first spells.")
    c.quest("arrival", "A Place to Start", 0, 0, [item("minecraft:crafting_table")],
            desc=["Punch a tree, make a crafting table. Every great base starts this way.",
                  "Look around. Can you see a village, a tower, a ruin? Remember it."],
            deps=["welcome:welcome"], rewards=[r_xp(20), r_item("minecraft:bread", 8)], shape="hexagon", size=1.5)
    c.quest("iron", "Iron Age", 2, 0, [item("minecraft:iron_ingot", 8)],
            desc=["Iron is what everything else is built from: tools, armor, machines, spellbooks."],
            deps=["arrival"], rewards=[r_xp(40)])
    c.quest("night", "Night Watch", 4, 0,
            [kill("minecraft:zombie", 10), kill("minecraft:skeleton", 5), kill("minecraft:spider", 5)],
            desc=["The nights are dangerous. Learn how your weapon swings (Better Combat) and how to dodge (&eR&r)."],
            deps=["iron"], rewards=[r_xp(60), r_item("minecraft:arrow", 32)], icon="minecraft:iron_sword")
    # Create branch
    c.quest("alloy", "&6Create:&r Andesite Alloy", 2, -2, [item("create:andesite_alloy", 8)],
            desc=["&6Create&r lets you build machines out of moving parts.",
                  "Andesite Alloy is the start of it all. Mix andesite with iron nuggets (or zinc).",
                  "Hold &eW&r over any Create item to see a Ponder scene."],
            deps=["iron"], rewards=[r_xp(40), r_item("create:andesite_alloy", 8)])
    c.quest("water_wheel", "&6Create:&r Power", 4, -2, [item("create:water_wheel")],
            desc=["A water wheel turns flowing water into rotation. Rotation powers everything in Create."],
            deps=["alloy"], rewards=[r_xp(40), r_item("create:shaft", 8)])
    c.quest("press", "&6Create:&r First Machines", 6, -2,
            [item("create:mechanical_press"), item("create:millstone")],
            desc=["A press flattens ingots into sheets. A millstone grinds ores and crops.",
                  "Ores ground up give extra ingots. Automation starts paying off right away."],
            deps=["water_wheel"], rewards=[r_xp(60)])
    # Magic branch
    c.quest("spellbook", "&9Magic:&r A Spellbook", 2, 2,
            [item("irons_spellbooks:inscription_table"), item("irons_spellbooks:copper_spell_book")],
            desc=["&9Iron's Spells:&r spells are found as &oscrolls&r in chests and from wizards.",
                  "Put a scroll into your spellbook at the Inscription Table to learn it for good.",
                  "Cast with the spell wheel (default &eV&r) and the cast key (default &eR&r, rebind if it clashes with dodge)."],
            deps=["iron"], rewards=[r_xp(40), r_item("irons_spellbooks:arcane_essence", 4)])
    c.quest("ars", "&9Magic:&r Ars Nouveau", 4, 2, [item("ars_nouveau:novice_spell_book")],
            desc=["&9Ars Nouveau&r is the other magic: you design spells yourself from glyphs.",
                  "Read the Worn Notebook for a full guide. Totally optional, totally fun."],
            deps=["spellbook"], optional=True, rewards=[r_xp(40)])
    # Explore / utility
    c.quest("backpack", "Pack Your Bags", 0, 2, [item("sophisticatedbackpacks:backpack")],
            desc=["A backpack is the best friend of an explorer. Upgrade it later."],
            deps=["arrival"], rewards=[r_xp(20)], optional=True)
    c.quest("waystone", "Waystones", 0, -2, [check("I found or built a waystone")],
            desc=["Waystones let you teleport between places you have visited.",
                  "Villages often have one. Build one at your base and at every place you want to come back to."],
            deps=["arrival"], rewards=[r_xp(20), r_item("waystones:warp_stone")], optional=True,
            icon="waystones:waystone")
    c.trial(1, 6.5, 0,
            [item("create:andesite_alloy", 16), kill("minecraft:creeper", 3)],
            desc=["Show that you can build and fight.", "Have 16 Andesite Alloy, and take down 3 creepers before they take down your base."],
            deps=["night"], icon="ultimate:tempering_kit_1")
    return c


def phase2():
    c = Chapter("phase_2_ruins", "&a2. Ruins", "minecraft:mossy_stone_bricks", GROUP_ACT1,
                subtitle="The surface is full of places to raid.")
    c.quest("start", "The World Beyond", 0, 0, [structure("#minecraft:village")],
            desc=["Visit a village. Trade, find a waystone, and ask yourself: where do all those ruins lead?"],
            deps=["phase_1_arrival:trial"], rewards=[r_xp(40), r_item("minecraft:emerald", 4)], shape="hexagon", size=1.5)
    c.quest("outpost", "Pillager Outpost", 2, -1.5,
            [structure("#minecraft:pillager_outpost"), kill("minecraft:pillager", 8)],
            desc=["Pillagers have built a tower nearby. Bring it down."],
            deps=["start"], rewards=[r_xp(80), r_item("minecraft:crossbow")], icon="minecraft:crossbow")
    c.quest("dungeon", "Into the Dungeon", 2, 1.5,
            [structure("#betterdungeons:better_dungeons")],
            desc=["Dungeons hide under the ground: catacombs of zombies, skeletons and spiders.",
                  "Each player gets their own loot from every chest, so share the hunt."],
            deps=["start"], rewards=[r_xp(80)], icon="minecraft:spawner")
    c.quest("desert", "Desert Temple", 4, 2.5, [structure("#betterdeserttemples:better_desert_temples")],
            desc=["A huge temple under the sand. Watch out for traps and the pharaoh's curse (mining fatigue).",
                  "Break the seals to lift it."],
            deps=["dungeon"], rewards=[r_xp(80), r_item("minecraft:gold_ingot", 8)], optional=True, icon="minecraft:chiseled_sandstone")
    c.quest("jungle", "Jungle Temple", 4, 0.5, [structure("#betterjungletemples:better_jungle_temples")],
            desc=["Puzzles, traps and treasure under the vines."],
            deps=["dungeon"], rewards=[r_xp(80), r_item("minecraft:emerald", 8)], optional=True, icon="minecraft:mossy_cobblestone")
    c.quest("illagers", "Illager Strongholds", 4, -1.5, [structure("#nova_structures:illager_structures")],
            desc=["Manors, hideouts, mansions. The illagers have more than outposts.",
                  "Evokers drop totems of undying. You'll want some later."],
            deps=["outpost"], rewards=[r_xp(100)], optional=True, icon="minecraft:totem_of_undying")
    c.quest("wizard", "&9Magic:&r Wizard Towers", 0, 3,
            [kill("irons_spellbooks:pyromancer"), kill("irons_spellbooks:cryomancer")],
            desc=["Wandering wizards and tower mages carry spell scrolls and arcane essence.",
                  "Some are friendly, some are not. Pyromancers and cryomancers live in their towers."],
            deps=["start"], rewards=[r_xp(80), r_item("irons_spellbooks:arcane_essence", 8)], optional=True,
            icon="irons_spellbooks:arcane_essence")
    c.quest("brass", "&6Create:&r Brass", 0, -3, [item("create:brass_ingot", 8)],
            desc=["Brass needs &oheated&r mixing, which normally means a blaze.",
                  "The Nether is sealed, so this pack has an Overworld recipe for the &6Blaze Burner&r:",
                  "an empty burner (iron plates and magma) plus magma blocks, lava and coal. Check JEI.",
                  "Zinc ore is found in the Overworld; copper you know."],
            deps=["start"], rewards=[r_xp(80), r_item("create:brass_ingot", 4)], icon="create:brass_ingot")
    c.quest("brass_machines", "&6Create:&r Brass Machines", 2, -3.5,
            [item("create:deployer"), item("create:mechanical_arm")],
            desc=["Deployers use items like a player would. Mechanical arms move things around.",
                  "Your factory can now craft things on its own."],
            deps=["brass"], rewards=[r_xp(80)], optional=True, icon="create:mechanical_arm")
    c.trial(2, 6, 0,
            [kill("minecraft:vindicator", 5), item("create:brass_ingot", 16)],
            desc=["Prove the ruins are yours. Defeat 5 vindicators and have 16 brass ingots."],
            deps=["outpost", "dungeon"], icon="ultimate:tempering_kit_2")
    return c


def phase3():
    c = Chapter("phase_3_deep", "&a3. The Deep", "minecraft:sculk", GROUP_ACT1,
                subtitle="Mineshafts, caves, and something ancient below.")
    c.quest("start", "Going Down", 0, 0, [item("minecraft:diamond", 3)],
            desc=["The best stuff is underground. Find diamonds, and bring torches."],
            deps=["phase_2_ruins:trial"], rewards=[r_xp(60)], shape="hexagon", size=1.5)
    c.quest("drill", "&6Create:&r Mechanical Drill", 0, -2, [item("create:mechanical_drill")],
            desc=["Let a machine dig for you. Put drills on a moving contraption and you have a tunnel bore."],
            deps=["start"], rewards=[r_xp(80)], icon="create:mechanical_drill")
    c.quest("mineshaft", "Abandoned Mineshafts", 2, -1.5, [structure("#ultimate:mineshafts")],
            desc=["The old miners left rails, chests and cave spiders behind."],
            deps=["start"], rewards=[r_xp(60), r_item("minecraft:rail", 32)], icon="minecraft:rail")
    c.quest("wrought_chamber", "The Wrought Chamber", 2, 1.5, [structure("mowziesmobs:wrought_chamber")],
            desc=["Deep under the mountains there is a sealed iron room.",
                  "Something huge waits inside, wearing iron armor."],
            deps=["start"], rewards=[r_xp(80)], icon="minecraft:iron_door")
    c.quest("wroughtnaut", "&cBoss: Ferrous Wroughtnaut", 4, 1.5, [stage("ultimate_boss_wroughtnaut")],
            desc=["&cThe Ferrous Wroughtnaut&r only takes damage when struck &efrom behind&r.",
                  "Dodge its swings, wait until it gets its axe stuck, then hit its back.",
                  "Everyone within 64 blocks gets credit."],
            deps=["wrought_chamber"], rewards=[r_xp(200)], icon="mowziesmobs:wrought_axe", size=1.5)
    c.quest("deep_dark", "The Deep Dark", 4, -1.5, [biome("minecraft:deep_dark"), structure("minecraft:ancient_city")],
            desc=["Silent, dark, full of sculk. Don't wake the Warden.",
                  "Ancient City chests hold &dEcho Shards&r, the base of every Boss Echo."],
            deps=["mineshaft"], rewards=[r_xp(150)], icon="minecraft:sculk_shrieker")
    c.quest("echo_shard", "&dEcho Shards", 6, -1.5, [item("minecraft:echo_shard", 2)],
            desc=["With Echo Shards you can craft &dBoss Echoes&r and fight any quest boss again."],
            deps=["deep_dark"], rewards=[r_xp(60)], optional=True)
    c.quest("arcane_anvil", "&9Magic:&r Arcane Anvil", 0, 2, [item("irons_spellbooks:arcane_anvil")],
            desc=["The Arcane Anvil upgrades spellbooks and imbues weapons with spells.",
                  "Yes, you can put a spell on your sword."],
            deps=["start"], rewards=[r_xp(80)], optional=True)
    c.trial(3, 6.5, 1.5,
            [stage("ultimate_boss_wroughtnaut"), structure("minecraft:ancient_city")],
            desc=["Defeat the Ferrous Wroughtnaut and reach an Ancient City."],
            deps=["wroughtnaut", "deep_dark"], icon="ultimate:tempering_kit_3")
    return c


def phase4():
    c = Chapter("phase_4_far_lands", "&b4. Far Lands", "minecraft:compass", GROUP_ACT2,
                subtitle="Expeditions. Pick two of four.")
    c.quest("start", "Expedition", 0, 0, [check("Ready to travel")],
            desc=["Four great enemies live far from spawn: in the ice, in the jungle, in the frozen peaks and in the desert.",
                  "&eYou only need to beat two of them&r to pass this Phase. Pick the trips that sound fun.",
                  "Now is a good time for a train line or a waystone network."],
            deps=["phase_3_deep:trial"], rewards=[r_xp(60)], shape="hexagon", size=1.5, icon="minecraft:compass")
    c.quest("train", "&6Create:&r Trains", 0, -2.5,
            [item("create:track", 64), item("create:track_station"), item("create:controls")],
            desc=["Build a train. Tracks, a station, and a controls block on a frame of casings.",
                  "A shared rail network is the backbone of a server. Connect your friends' bases."],
            deps=["start"], rewards=[r_xp(150)], icon="create:controls")
    c.quest("cold", "The Frozen North", 2, -3, [biome("#c:is_snowy")],
            desc=["&bFrostmaw&r roams the ice spikes and snowy plains, sleeping until disturbed."],
            deps=["start"], rewards=[r_xp(40)], icon="minecraft:blue_ice")
    c.quest("frostmaw", "&cBoss: Frostmaw", 4, -3, [stage("ultimate_boss_frostmaw")],
            desc=["A great ice beast. Stay away from its breath, use fire, and keep moving."],
            deps=["cold"], rewards=[r_xp(300), r_item("minecraft:diamond", 3)], icon="mowziesmobs:ice_crystal", size=1.5)
    c.quest("grove", "Umvuthana Grove", 2, -1, [structure("mowziesmobs:umvuthana_grove")],
            desc=["Masked warriors guard a grove in the savanna. Their chief wears the mask of the sun."],
            deps=["start"], rewards=[r_xp(40)], icon="minecraft:acacia_sapling")
    c.quest("umvuthi", "&cBoss: Umvuthi", 4, -1, [stage("ultimate_boss_umvuthi")],
            desc=["Umvuthi calls the sun down on you. Kill the followers first, and don't stand in the light."],
            deps=["grove"], rewards=[r_xp(300), r_item("minecraft:diamond", 3)], icon="mowziesmobs:sol_visage", size=1.5)
    c.quest("prison", "The Frosted Prison", 2, 1, [structure("cataclysm:frosted_prison")],
            desc=["A castle on the snowy peaks, full of draugr. In its great hall lies a cursed tombstone."],
            deps=["start"], rewards=[r_xp(40)], icon="minecraft:packed_ice")
    c.quest("maledictus", "&cBoss: Maledictus", 4, 1, [stage("ultimate_boss_maledictus")],
            desc=["The cursed warrior. Fast, deadly and loud. Bring shields and friends."],
            deps=["prison"], rewards=[r_xp(300), r_item("minecraft:diamond", 3)], icon="minecraft:wither_skeleton_skull", size=1.5)
    c.quest("pyramid", "The Cursed Pyramid", 2, 3, [structure("cataclysm:cursed_pyramid")],
            desc=["Under the desert lies the tomb of a king. You need the &eNecklace of the Desert&r to wake him.",
                  "...or an Echo."],
            deps=["start"], rewards=[r_xp(40)], icon="minecraft:sandstone")
    c.quest("remnant", "&cBoss: Ancient Remnant", 4, 3, [stage("ultimate_boss_ancient_remnant")],
            desc=["The sand king and his sandstorms. Keep your distance from the charge."],
            deps=["pyramid"], rewards=[r_xp(300), r_item("minecraft:diamond", 3)], icon="cataclysm:necklace_of_the_desert", size=1.5)
    c.quest("evoker_fort", "&9Magic:&r Evoker Fort", 0, 2.5, [structure("irons_spellbooks:evoker_fort")],
            desc=["An illager fortress full of evokers and their spells. Great loot for casters."],
            deps=["start"], rewards=[r_xp(100), r_item("irons_spellbooks:arcane_essence", 8)], optional=True,
            icon="irons_spellbooks:evoker_spell_book")
    c.trial(4, 6.5, 0, [check("Return from the far lands")],
            desc=["Beat &etwo&r of the four far-land bosses: Frostmaw, Umvuthi, Maledictus or the Ancient Remnant."],
            deps=["frostmaw", "umvuthi", "maledictus", "remnant"], min_deps=2, icon="ultimate:tempering_kit_4")
    return c


def phase5():
    c = Chapter("phase_5_sea", "&b5. The Sea", "minecraft:heart_of_the_sea", GROUP_ACT2,
                subtitle="A city sank. Something still lives in it.")
    c.quest("start", "Set Sail", 0, 0, [item("minecraft:heart_of_the_sea")],
            desc=["Buried treasure maps lead to the Heart of the Sea. With it, build a conduit and breathe underwater."],
            deps=["phase_4_far_lands:trial"], rewards=[r_xp(80)], shape="hexagon", size=1.5)
    c.quest("monument", "Ocean Monument", 2, -1.5, [structure("betteroceanmonuments:ocean_monument")],
            desc=["Guardians, elder guardians and gold. Bring milk for mining fatigue."],
            deps=["start"], rewards=[r_xp(100), r_item("minecraft:sponge", 4)], icon="minecraft:prismarine_bricks")
    c.quest("airship", "&6Create:&r First Airship", 0, -2.5,
            [item("aeronautics:propeller_bearing"), item("simulated:physics_assembler")],
            desc=["With Create Aeronautics you can build a flying ship: an envelope or propellers to lift it,",
                  "a propeller bearing to push it, and a Physics Assembler to bring it to life.",
                  "Ponder (&eW&r) shows how. An airship makes the sea a lot friendlier."],
            deps=["start"], rewards=[r_xp(200)], icon="aeronautics:propeller_bearing")
    c.quest("sunken_city", "The Sunken City", 2, 1.5, [structure("cataclysm:sunken_city")],
            desc=["A drowned city full of deeplings. At its heart is the Altar of the Abyss."],
            deps=["start"], rewards=[r_xp(100)], icon="minecraft:prismarine")
    c.quest("leviathan", "&cBoss: The Leviathan", 4, 1.5, [stage("ultimate_boss_leviathan")],
            desc=["The Leviathan only fights in water. Water breathing, Depth Strider and a conduit help a lot.",
                  "Its Echo only works while you stand in water."],
            deps=["sunken_city"], rewards=[r_xp(500), r_item("minecraft:diamond", 5)], icon="minecraft:trident", size=1.5)
    c.quest("scylla", "&5Optional: Scylla", 6, 3, [stage("ultimate_boss_scylla")],
            desc=["Atop the Acropolis waits Scylla, a storm queen. Optional, but glorious."],
            deps=["leviathan"], rewards=[r_xp(500)], optional=True, icon="minecraft:lightning_rod")
    c.trial(5, 6.5, 0, [stage("ultimate_boss_leviathan")],
            desc=["Defeat the Leviathan."],
            deps=["leviathan", "monument"], icon="ultimate:tempering_kit_5")
    return c


def phase6():
    c = Chapter("phase_6_forge", "&b6. The Forge", "minecraft:anvil", GROUP_ACT2,
                subtitle="An ancient factory holds the key to the Nether.")
    c.quest("start", "Precision", 0, 0, [item("create:precision_mechanism", 4)],
            desc=["Precision mechanisms come from sequenced assembly: a chain of deployers and a press.",
                  "If you've built that line, you're ready for the factory."],
            deps=["phase_5_sea:trial"], rewards=[r_xp(150)], shape="hexagon", size=1.5)
    c.quest("factory", "The Ancient Factory", 2, 0, [structure("cataclysm:ancient_factory")],
            desc=["Deep under the ground lies a factory of the old world. Its guardian, &cthe Harbinger&r, is dormant.",
                  "Normally you need a Nether Star to wake it, but the Nether is sealed.",
                  "Instead, right-click it with an &dEcho of The Harbinger&r."],
            deps=["start"], rewards=[r_xp(150)], icon="minecraft:redstone_block")
    c.quest("echo", "&dWake the Harbinger", 2, 2, [item("ultimate:echo_harbinger")],
            desc=["Craft an Echo of The Harbinger (echo shard, precision mechanism, redstone block, iron block)."],
            deps=["factory"], rewards=[r_xp(50)], icon="ultimate:echo_harbinger")
    c.quest("harbinger", "&cBoss: The Harbinger", 4, 0, [stage("ultimate_boss_harbinger")],
            desc=["A war machine with lasers and missiles. Use cover, spread out, and keep hitting.",
                  "&6When it falls for the first time, the Nether opens for everyone.&r"],
            deps=["factory"], rewards=[r_xp(800), r_item("minecraft:diamond", 8)], icon="minecraft:nether_star", size=2.0)
    c.quest("sculptor", "&5Optional: The Sculptor", 0, -2, [stage("ultimate_boss_sculptor")],
            desc=["On a mountain monastery a sculptor challenges you to climb his pillar while he attacks.",
                  "A puzzle fight. Optional, but nobody forgets it."],
            deps=["start"], rewards=[r_xp(500)], optional=True, icon="minecraft:stone_bricks")
    c.trial(6, 6.5, 0, [stage("ultimate_boss_harbinger")],
            desc=["Defeat the Harbinger.",
                  "This is the end of Act II. The Nether is open: Act III starts now."],
            deps=["harbinger"], icon="ultimate:tempering_kit_6")
    return c


def phase7():
    c = Chapter("phase_7_fire", "&c7. The Fire", "minecraft:blaze_powder", GROUP_ACT3,
                subtitle="Fortresses, bastions, and the two fire bosses.")
    c.quest("start", "Into the Nether", 0, 0, [dimension("minecraft:the_nether")],
            desc=["The Harbinger is down and the Nether is open for everyone. Light a portal.",
                  "Bring fire resistance potions, a shield and gold armor (piglins leave you alone if you wear gold).",
                  "Incendium made the Nether a lot wilder than you remember."],
            deps=["phase_6_forge:trial"], rewards=[r_xp(150), r_item("minecraft:golden_carrot", 16)], shape="hexagon", size=1.5,
            icon="minecraft:netherrack")
    c.quest("fortress", "Nether Fortress", 2, -1.5, [structure("#betterfortresses:better_fortresses")],
            desc=["YUNG's fortresses are huge: halls, bridges, a whole keep. Blazes and wither skeletons live here."],
            deps=["start"], rewards=[r_xp(150)], icon="minecraft:nether_bricks")
    c.quest("blaze", "Blaze Rods", 4, -1.5, [item("minecraft:blaze_rod", 8)],
            desc=["Blaze rods brew potions and power a real Blaze Burner. You'll need them for Eyes of Ender too."],
            deps=["fortress"], rewards=[r_xp(100)], icon="minecraft:blaze_rod")
    c.quest("bastion", "Bastion Remnant", 2, 1.5, [structure("#minecraft:bastion_remnant")],
            desc=["A piglin castle full of gold, and full of piglin brutes. Their chests hold netherite scraps."],
            deps=["start"], rewards=[r_xp(150), r_item("minecraft:gold_ingot", 16)], icon="minecraft:gilded_blackstone")
    c.quest("netherite", "Netherite", 4, 1.5, [item("minecraft:netherite_ingot")],
            desc=["Ancient debris hides deep in the Nether at about Y 15. Four scraps and four gold make one ingot.",
                  "Use a smithing table and a netherite upgrade template (bastions have them)."],
            deps=["bastion"], rewards=[r_xp(200)], icon="minecraft:netherite_ingot")
    c.quest("soul_smith", "The Soul Black Smith", 2, 4, [structure("cataclysm:soul_black_smith")],
            desc=["In the soul sand valleys stands an old forge. Its smith never stopped working."],
            deps=["start"], rewards=[r_xp(150)], icon="minecraft:soul_lantern")
    c.quest("monstrosity", "&cBoss: Netherite Monstrosity", 4, 4, [stage("ultimate_boss_netherite_monstrosity")],
            desc=["A walking furnace of netherite and lava. It hits like a mountain and throws lava.",
                  "Fire resistance is a must. Hit it after its slam, then get out of the way."],
            deps=["soul_smith"], rewards=[r_xp(800), r_item("minecraft:netherite_scrap", 2)], icon="cataclysm:monstrous_horn", size=1.5)
    c.quest("arena", "The Burning Arena", 2, -4, [structure("cataclysm:burning_arena")],
            desc=["An arena of fire, deep in the Nether. At its heart is the &eAltar of Fire&r.",
                  "Ignis sleeps until the altar is lit... or until someone uses an &dEcho of Ignis&r."],
            deps=["start"], rewards=[r_xp(150)], icon="cataclysm:altar_of_fire")
    c.quest("ignis", "&cBoss: Ignis", 4, -4, [stage("ultimate_boss_ignis")],
            desc=["A knight of living fire with a sword and a shield. Three phases, each angrier than the last.",
                  "&6When Ignis falls for the first time, the End opens for everyone.&r"],
            deps=["arena"], rewards=[r_xp(1000), r_item("minecraft:diamond", 8)], icon="cataclysm:ignitium_ingot", size=2.0)
    c.quest("echoes", "&dNether Echoes", 6, -4, [item("ultimate:echo_ignis")],
            desc=["An Echo of Ignis or of the Netherite Monstrosity calls them again, but only in the Nether.",
                  "Late joiners: ask a friend who has fought them to come along."],
            deps=["ignis"], rewards=[r_xp(50)], optional=True, icon="ultimate:echo_ignis")
    c.quest("wither", "&5Optional: The Wither", 0, -3, [stage("ultimate_boss_wither")],
            desc=["Three wither skeleton skulls and four soul sand. Build it far away from your base.",
                  "Its Nether Star makes a beacon."],
            deps=["fortress"], rewards=[r_xp(800), r_item("minecraft:netherite_scrap")], optional=True, icon="minecraft:nether_star")
    c.quest("blaze_burner", "&6Create:&r A Real Blaze Burner", 0, 3, [item("create:blaze_burner"), item("create:blaze_cake")],
            desc=["Catch a blaze in an empty burner. Feed it a Blaze Cake and it becomes &esuperheated&r,",
                  "which unlocks the hottest mixing recipes."],
            deps=["start"], rewards=[r_xp(150)], optional=True, icon="create:blaze_cake")
    c.quest("netherite_book", "&9Magic:&r Netherite Spell Book", 6, 1.5, [item("irons_spellbooks:netherite_spell_book")],
            desc=["More spell slots and a lot more toughness. Your casters will thank you."],
            deps=["netherite"], rewards=[r_xp(150)], optional=True)
    c.trial(7, 7, 0, [stage("ultimate_boss_netherite_monstrosity"), stage("ultimate_boss_ignis")],
            desc=["Defeat the Netherite Monstrosity and Ignis."],
            deps=["monstrosity", "ignis"], icon="ultimate:tempering_kit_7")
    return c


def phase8():
    c = Chapter("phase_8_one_way", "&58. One Way", "minecraft:end_stone", GROUP_ACT4,
                subtitle="The portal only goes one way. Pack well.")
    c.quest("eyes", "Eyes of Ender", 0, 0, [item("minecraft:ender_eye", 12)],
            desc=["Blaze powder and ender pearls. Throw an eye and follow it to a stronghold."],
            deps=["phase_7_fire:trial"], rewards=[r_xp(150)], shape="hexagon", size=1.5)
    c.quest("stronghold", "The Stronghold", 2, 0, [structure("#betterstrongholds:better_strongholds")],
            desc=["YUNG's strongholds are big and full of traps. The portal room is at the bottom."],
            deps=["eyes"], rewards=[r_xp(150)], icon="minecraft:end_portal_frame")
    c.quest("pack", "&cRead this before you jump", 2, -2, [check("I packed my bags")],
            desc=["&cThe End is a one-way trip.&r Nothing takes you back: no portal, no waystone. Only dying does.",
                  "You won't land next to the dragon. The portal throws you onto an outer island, far away from it.",
                  "",
                  "Bring: food and seeds, a water bucket, tools, lots of blocks, torches, Create parts.",
                  "Beds explode in the End. If you die, your items wait in a &egrave&r where you fell, and the portal still takes you back there.",
                  "Go together. The first group builds the base everyone else lands in."],
            deps=["stronghold"], rewards=[r_xp(50)], icon="minecraft:chest")
    c.quest("arrive", "A New World", 4, 0, [dimension("minecraft:the_end")],
            desc=["Welcome to the End. Everyone who comes through the portal lands here, on this same island.",
                  "Build a base. You'll be here for a while."],
            deps=["pack"], rewards=[r_xp(300)], icon="minecraft:end_stone", size=1.5)
    c.quest("food", "Food in the Void", 6, -2, [item("minecraft:popped_chorus_fruit", 16)],
            desc=["Chorus fruit grows on the islands. Pop it in a furnace. End's Delight turns chorus, shulkers",
                  "and even endermites into real meals."],
            deps=["arrive"], rewards=[r_xp(100)], icon="minecraft:chorus_fruit")
    c.quest("end_city", "End City", 6, 0, [structure("#minecraft:end_city")],
            desc=["Purple towers full of shulkers. Some have a ship floating next to them.",
                  "Remember the ships. They matter later."],
            deps=["arrive"], rewards=[r_xp(200)], icon="minecraft:purpur_block")
    c.quest("shells", "Shulker Shells", 8, 0, [item("minecraft:shulker_shell", 4)],
            desc=["Shulker boxes keep your stuff organized, and the End's Tempering Kits need shells."],
            deps=["end_city"], rewards=[r_xp(150)], icon="minecraft:shulker_box")
    c.quest("elytra", "Wings", 8, -2, [item("minecraft:elytra")],
            desc=["End ships carry an elytra. Fly between the outer islands!",
                  "&eBut:&r near the dragon's island the void winds tear wings apart. You'll see."],
            deps=["end_city"], rewards=[r_xp(200), r_item("minecraft:firework_rocket", 32)], optional=True)
    c.quest("citadel", "The Ruined Citadel", 6, 2.5, [structure("cataclysm:ruined_citadel")],
            desc=["A broken castle of end stone. Its guardian is not broken at all."],
            deps=["arrive"], rewards=[r_xp(200)], icon="minecraft:end_stone_bricks")
    c.quest("guardian", "&cBoss: Ender Guardian", 8, 2.5, [stage("ultimate_boss_ender_guardian")],
            desc=["Teleports, punches, and throws void runes. Watch the ground for purple marks and move.",
                  "&dWhoever helps beat it can wake a Return Gate.&r"],
            deps=["citadel"], rewards=[r_xp(1200), r_item("minecraft:diamond", 8)], icon="cataclysm:gauntlet_of_guard", size=2.0)
    c.trial(8, 10.5, 1, [stage("ultimate_boss_ender_guardian")],
            desc=["Defeat the Ender Guardian."],
            deps=["guardian"], icon="ultimate:tempering_kit_8")
    return c


def phase9():
    c = Chapter("phase_9_way_back", "&d9. The Way Back", "ultimate:return_gate", GROUP_ACT5,
                subtitle="How do we get home?")
    c.quest("start", "How do we get back?", 0, 0, [check("Think about it")],
            desc=["There is no portal home. Not yet.",
                  "Old stories talk about a &dReturn Gate&r: purpur and shells, pearls, and the head of a dragon",
                  "that never lived. Only someone who has beaten the Ender Guardian can wake it."],
            deps=["phase_8_one_way:trial"], rewards=[r_xp(50)], shape="hexagon", size=1.5, icon="minecraft:writable_book")
    c.quest("head", "The Figurehead", 2, -1.5, [item("minecraft:dragon_head")],
            desc=["Every End ship carries a dragon head on its bow. Bring one back."],
            deps=["start"], rewards=[r_xp(200)], icon="minecraft:dragon_head")
    c.quest("materials", "Purpur and Pearls", 2, 1.5,
            [item("minecraft:purpur_block", 4), item("minecraft:shulker_shell", 2), item("minecraft:ender_pearl", 2)],
            desc=["The frame of the gate. Purpur from the cities, shells from shulkers, pearls from endermen."],
            deps=["start"], rewards=[r_xp(100)], icon="minecraft:purpur_pillar")
    c.quest("build", "Build the Return Gate", 4, 0, [item("ultimate:return_gate")],
            desc=["Craft the gate (see JEI) and place it at your End base."],
            deps=["head", "materials"], rewards=[r_xp(200)], icon="ultimate:return_gate")
    c.trial(9, 6.5, 0, [stage("ultimate_return_gate")],
            desc=["Wake the Return Gate (right-click it as someone who beat the Ender Guardian), then use it.",
                  "&dThis happens once, for the whole server:&r from now on the gate takes anyone home,",
                  "and the stronghold portal brings anyone straight to the gate.",
                  "Late joiners: just right-click an awake gate to finish this Trial."],
            deps=["build"], icon="ultimate:tempering_kit_9")
    return c


def phase10():
    c = Chapter("phase_10_dragon", "&d10. The Dragon", "minecraft:dragon_egg", GROUP_ACT5,
                subtitle="The dragon's island is cut off by the void.")
    c.quest("start", "Cut Off", 0, 0, [check("I tried to fly there")],
            desc=["The dragon's island is about a thousand blocks of empty void away.",
                  "Near it, wings stop working. Pearls don't reach. You need something bigger."],
            deps=["phase_9_way_back:trial"], rewards=[r_xp(50)], shape="hexagon", size=1.5, icon="minecraft:elytra")
    c.quest("airship", "&6Create:&r An End Airship", 2, -1.5,
            [item("aeronautics:propeller_bearing", 2), item("simulated:physics_assembler")],
            desc=["Build an airship that can cross the void: lift, propellers, fuel, and a place to land.",
                  "Bring blocks, food and your whole team. Ponder (&eW&r) shows how the parts work.",
                  "Levitite (check JEI) makes things float."],
            deps=["start"], rewards=[r_xp(400)], icon="aeronautics:propeller_bearing", size=1.5)
    c.quest("island", "The Dragon's Island", 4, 0, [biome("minecraft:the_end")],
            desc=["Land on the main island. The obsidian towers hold End Crystals that heal the dragon.",
                  "Break them first. Some are in iron cages: you'll have to climb."],
            deps=["airship"], rewards=[r_xp(300)], icon="minecraft:end_crystal")
    c.quest("crystals", "No More Healing", 4, 2, [check("All crystals destroyed")],
            desc=["Bows, spells, anything that reaches. No crystals, no healing."],
            deps=["island"], rewards=[r_xp(100)], optional=True, icon="minecraft:bow")
    c.quest("dragon", "&cBoss: The Ender Dragon", 6, 0, [stage("ultimate_boss_ender_dragon")],
            desc=["The last boss. Everyone within 64 blocks gets credit.",
                  "When it dies, the void winds calm down and wings work everywhere in the End."],
            deps=["island"], rewards=[r_xp(2000), r_item("minecraft:diamond_block", 2)], icon="minecraft:dragon_head", size=2.0)
    c.quest("breath", "Dragon's Breath", 8, -2, [item("minecraft:dragon_breath", 4)],
            desc=["Catch it in bottles while the dragon breathes. Tempering Kit X needs it, so grab plenty."],
            deps=["dragon"], rewards=[r_xp(100)], optional=True)
    c.quest("gateway", "Beyond", 8, 2, [check("I flew through an End Gateway")],
            desc=["The dragon's death opens small gateways at the edge of its island. They lead to the far islands."],
            deps=["dragon"], rewards=[r_xp(100)], optional=True, icon="minecraft:ender_pearl")
    c.trial(10, 10, 0, [stage("ultimate_boss_ender_dragon")],
            desc=["Defeat the Ender Dragon.",
                  "You've done it: all ten Phases. Tempering X is yours.",
                  "&dThe Dragon's Echo&r (End raids and dragon pacts) is coming in a future update."],
            deps=["dragon"], icon="ultimate:tempering_kit_10")
    return c


# ---------------------------------------------------------------- side chapters

def grid(c, entries, x0, y0, cols, deps, xp=30, step=1.5):
    """Lay out small optional quests in rows. entries: (key, title, tasks, desc, icon)."""
    for i, (key, title, tasks, desc, icon) in enumerate(entries):
        c.quest(key, title, x0 + (i % cols) * step, y0 + (i // cols) * step, tasks,
                desc=[desc] if isinstance(desc, str) else desc, deps=deps, rewards=[r_xp(xp)],
                optional=True, icon=icon)


BIOMES_OVERWORLD = [
    ("natures_spirit", "redwood_forest", "Redwood Forest", "Trees taller than your house. Taller than your neighbor's house too.", "natures_spirit:redwood_sapling"),
    ("natures_spirit", "sugi_forest", "Sugi Forest", "Japanese cedars and quiet paths.", "natures_spirit:sugi_sapling"),
    ("natures_spirit", "wisteria_forest", "Wisteria Forest", "Purple and blue flowers hanging from every branch.", "natures_spirit:blue_wisteria_sapling"),
    ("natures_spirit", "aspen_forest", "Aspen Forest", "White trunks and golden leaves.", "natures_spirit:aspen_sapling"),
    ("natures_spirit", "maple_woodlands", "Maple Woodlands", "Autumn, all year round.", "natures_spirit:red_maple_sapling"),
    ("natures_spirit", "lavender_fields", "Lavender Fields", "It smells nice. Probably.", "natures_spirit:lavender"),
    ("natures_spirit", "tropical_woods", "Tropical Woods", "Palm-like trees and warm water.", "natures_spirit:coconut"),
    ("natures_spirit", "white_cliffs", "White Cliffs", "Chalk cliffs over the sea.", "natures_spirit:white_chalk"),
    ("natures_spirit", "stratified_desert", "Stratified Desert", "Layers of colored sandstone.", "natures_spirit:pink_sandstone"),
    ("natures_spirit", "marsh", "Marsh", "Reeds, mud and frogs.", "minecraft:mud"),
    ("natures_spirit", "tundra", "Tundra", "Cold, flat and very windy.", "minecraft:snow_block"),
    ("natures_spirit", "alpine_highlands", "Alpine Highlands", "Fir trees on high meadows.", "natures_spirit:fir_sapling"),
    ("biomeswevegone", "black_forest", "Black Forest", "Dark, dense and a bit creepy.", "minecraft:spruce_sapling"),
    ("biomeswevegone", "sakura_grove", "Sakura Grove", "Pink petals everywhere.", "minecraft:cherry_sapling"),
    ("biomeswevegone", "baobab_savanna", "Baobab Savanna", "Fat trees that look like they're upside down.", "biomeswevegone:baobab_sapling"),
    ("biomeswevegone", "bayou", "Bayou", "Swamp water, cypress trees and fireflies.", "biomeswevegone:cypress_sapling"),
    ("biomeswevegone", "crag_gardens", "Crag Gardens", "Huge pillars with gardens on top.", "minecraft:moss_block"),
    ("biomeswevegone", "enchanted_tangle", "Enchanted Tangle", "A magical forest. It glows.", "minecraft:amethyst_shard"),
    ("biomeswevegone", "forgotten_forest", "Forgotten Forest", "Old, mossy and silent.", "minecraft:mossy_cobblestone"),
    ("biomeswevegone", "jacaranda_jungle", "Jacaranda Jungle", "A jungle in purple.", "biomeswevegone:jacaranda_sapling"),
    ("biomeswevegone", "pumpkin_valley", "Pumpkin Valley", "Halloween, but it's a biome.", "minecraft:pumpkin"),
    ("biomeswevegone", "red_rock_valley", "Red Rock Valley", "Red stone canyons.", "minecraft:red_sandstone"),
    ("biomeswevegone", "rainbow_beach", "Rainbow Beach", "A beach of every color.", "minecraft:sand"),
    ("biomeswevegone", "shattered_glacier", "Shattered Glacier", "Broken ice and deep cracks.", "minecraft:blue_ice"),
    ("biomeswevegone", "skyris_vale", "Skyris Vale", "Green apple trees on misty hills.", "minecraft:green_apple" if False else "minecraft:apple"),
    ("biomeswevegone", "weeping_witch_forest", "Weeping Witch Forest", "Witches live here. Don't touch the pots.", "minecraft:cauldron"),
    ("biomeswevegone", "white_mangrove_marshes", "White Mangrove Marshes", "Pale mangroves in shallow water.", "minecraft:mangrove_propagule"),
    ("biomeswevegone", "ironwood_gour", "Ironwood Gour", "Stepped pools in red stone.", "minecraft:terracotta"),
    ("windswept", "chestnut_forest", "Chestnut Forest", "Roast chestnuts by the fire.", "windswept:chestnut_sapling"),
    ("windswept", "pine_barrens", "Pine Barrens", "Sandy soil and tall pines.", "windswept:pine_sapling"),
    ("minecraft", "mushroom_fields", "Mushroom Island", "Mooshrooms and no hostile mobs. A perfect hideout.", "minecraft:red_mushroom_block"),
    ("minecraft", "cherry_grove", "Cherry Grove", "Pink trees in the mountains.", "minecraft:cherry_leaves"),
    ("minecraft", "ice_spikes", "Ice Spikes", "Giant spikes of packed ice.", "minecraft:packed_ice"),
    ("minecraft", "eroded_badlands", "Eroded Badlands", "Spiky terracotta towers. Gold in the mineshafts.", "minecraft:orange_terracotta"),
]
BIOMES_UNDERGROUND = [
    ("minecraft", "lush_caves", "Lush Caves", "Glow berries and azalea, deep under the ground.", "minecraft:glow_berries"),
    ("minecraft", "dripstone_caves", "Dripstone Caves", "Watch your head.", "minecraft:pointed_dripstone"),
    ("yungscavebiomes", "frosted_caves", "Frosted Caves", "Ice caves under the snow. Bring a warm coat.", "minecraft:ice"),
    ("yungscavebiomes", "lost_caves", "Lost Caves", "Sand caves under the desert, full of old secrets.", "minecraft:suspicious_sand"),
    ("minecraft", "deep_dark", "The Deep Dark", "Shh.", "minecraft:sculk"),
]
BIOMES_NETHER = [
    ("minecraft", "crimson_forest", "Crimson Forest", "Red fungus trees and hoglins.", "minecraft:crimson_fungus"),
    ("minecraft", "warped_forest", "Warped Forest", "Blue and quiet. Endermen love it.", "minecraft:warped_fungus"),
    ("minecraft", "soul_sand_valley", "Soul Sand Valley", "Ghasts and skeletons in a valley of souls.", "minecraft:soul_sand"),
    ("minecraft", "basalt_deltas", "Basalt Deltas", "Jagged basalt and magma cubes.", "minecraft:basalt"),
    ("incendium", "ash_barrens", "Ash Barrens", "Grey ash as far as you can see.", "minecraft:gray_concrete_powder"),
    ("incendium", "infernal_dunes", "Infernal Dunes", "Burning sand dunes.", "minecraft:red_sand"),
    ("incendium", "inverted_forest", "Inverted Forest", "Trees hanging from the ceiling.", "minecraft:shroomlight"),
    ("incendium", "quartz_flats", "Quartz Flats", "A shining white plain.", "minecraft:quartz_block"),
    ("incendium", "toxic_heap", "Toxic Heap", "Green, glowing and poisonous.", "minecraft:slime_block"),
    ("incendium", "volcanic_deltas", "Volcanic Deltas", "Lava rivers between black rock.", "minecraft:magma_block"),
    ("incendium", "weeping_valley", "Weeping Valley", "Red vines and a deep valley.", "minecraft:weeping_vines"),
    ("incendium", "withered_forest", "Withered Forest", "Dead trees and wither skeletons.", "minecraft:wither_rose"),
]
BIOMES_END = [
    ("nullscape", "crystal_peaks", "Crystal Peaks", "Spires of crystal on the outer islands.", "minecraft:amethyst_cluster"),
    ("nullscape", "shadowlands", "Shadowlands", "Dark land under a dark sky.", "minecraft:obsidian"),
    ("nullscape", "void_barrens", "Void Barrens", "Thin islands floating over nothing.", "minecraft:end_stone"),
]


def discover_biomes():
    c = Chapter("discover_biomes", "&eDiscoveries: Biomes", "naturescompass:naturescompass", GROUP_SIDE,
                subtitle="Go everywhere. Every biome is a small reward.")
    c.quest("start", "&eThe Explorer's Kit", 0, 0, [item("naturescompass:naturescompass")],
            desc=["A Nature's Compass points to any biome you pick. Try it.",
                  "There are more than a hundred biomes in this pack. You don't have to find them all... but you could."],
            deps=["phase_1_arrival:arrival"], rewards=[r_xp(50)], shape="hexagon", size=1.5)
    entries = [(f"{ns}_{b}", t, [biome(f"{ns}:{b}")], d, i) for ns, b, t, d, i in BIOMES_OVERWORLD]
    grid(c, entries, 2, -3, 8, ["start"])
    c.quest("underground", "&eUnder the Ground", 0, 4.5, [check("Got it")],
            desc=["Cave biomes, deep below. YUNG's Cave Biomes adds frosted caves and lost sand caves."],
            deps=["start"], rewards=[r_xp(20)], optional=True, icon="minecraft:dripstone_block")
    grid(c, [(f"{ns}_{b}", t, [biome(f"{ns}:{b}")], d, i) for ns, b, t, d, i in BIOMES_UNDERGROUND], 2, 4.5, 8, ["underground"])
    c.quest("nether", "&cThe Nether's Biomes", 0, 6.5, [dimension("minecraft:the_nether")],
            desc=["Incendium adds eight new Nether biomes. Bring fire resistance."],
            deps=["phase_7_fire:start"], rewards=[r_xp(50)], optional=True, icon="minecraft:netherrack")
    grid(c, [(f"{ns}_{b}", t, [biome(f"{ns}:{b}")], d, i) for ns, b, t, d, i in BIOMES_NETHER], 2, 6.5, 8, ["nether"], xp=50)
    c.quest("end", "&5The End's Biomes", 0, 10, [dimension("minecraft:the_end")],
            desc=["Nullscape reshapes the outer End: peaks, shadows and barrens."],
            deps=["phase_8_one_way:arrive"], rewards=[r_xp(50)], optional=True, icon="minecraft:end_stone")
    grid(c, [(f"{ns}_{b}", t, [biome(f"{ns}:{b}")], d, i) for ns, b, t, d, i in BIOMES_END], 2, 10, 8, ["end"], xp=80)
    return c


STRUCTURES_SURFACE = [
    ("dungeons_arise:bandit_towers", "Bandit Towers", "Wooden towers full of bandits and their loot.", "minecraft:crossbow"),
    ("dungeons_arise:illager_fort", "Illager Fort", "A walled fort. The illagers won't let you in politely.", "minecraft:iron_axe"),
    ("dungeons_arise:keep_kayra", "Keep Kayra", "A mountain keep. Climb all the way up.", "minecraft:stone_bricks"),
    ("dungeons_arise:monastery", "The Monastery", "Quiet halls high in the mountains.", "minecraft:bell"),
    ("dungeons_arise:plague_asylum", "Plague Asylum", "Nobody has left this place in a long time.", "minecraft:spider_eye"),
    ("dungeons_arise:shiraz_palace", "Shiraz Palace", "A desert palace with a lot of rooms and a lot of guards.", "minecraft:gold_block"),
    ("dungeons_arise:thornborn_towers", "Thornborn Towers", "Towers grown over with thorns.", "minecraft:sweet_berries"),
    ("dungeons_arise:coliseum", "The Coliseum", "Fight your way through the arena.", "minecraft:iron_sword"),
    ("dungeons_arise:mushroom_village", "Mushroom Village", "Houses inside giant mushrooms.", "minecraft:brown_mushroom_block"),
    ("dungeons_arise:jungle_tree_house", "Jungle Tree House", "Somebody lives up there.", "minecraft:jungle_log"),
    ("dungeons_arise:heavenly_conqueror", "Heavenly Conqueror", "A fortress in the sky. Bring slow falling.", "minecraft:feather"),
    ("dungeons_arise:small_blimp", "A Lost Blimp", "Someone built an airship before you did.", "minecraft:white_wool"),
    ("idas:castle", "The Castle", "A real castle, walls and all.", "minecraft:cobblestone_wall"),
    ("idas:haunted_manor", "Haunted Manor", "You'll hear it before you see it.", "minecraft:cobweb"),
    ("idas:wizard_tower", "Wizard Tower", "A tower of books and magic.", "minecraft:enchanting_table"),
    ("idas:necromancers_spire", "Necromancer's Spire", "Undead guard their master's tower.", "minecraft:bone"),
    ("idas:tinkers_citadel", "Tinker's Citadel", "Machines, gears and a very busy tinkerer.", "create:cogwheel"),
    ("idas:treetop_tavern", "Treetop Tavern", "A pub up in the trees. First round's on you.", "minecraft:oak_leaves"),
    ("idas:labyrinth", "The Labyrinth", "Don't get lost.", "minecraft:mossy_stone_bricks"),
    ("towns_and_towers:exclusives/village_tudor", "A Tudor Village", "Half-timbered houses, English style.", "minecraft:dark_oak_planks"),
    ("#nova_structures:taverns", "A Tavern", "Food, drink and a bed for the night (Dungeons and Taverns).", "minecraft:barrel"),
    ("#nova_structures:illager_manor", "Illager Manor", "A rich illager family lives here. Not for long.", "minecraft:totem_of_undying"),
    ("mvs:cathedral", "The Cathedral", "A huge stone church.", "minecraft:bell"),
    ("mvs:castle_ruins", "Castle Ruins", "What's left of a castle.", "minecraft:cracked_stone_bricks"),
    ("mvs:floating_islands", "Floating Islands", "Islands in the sky. How?", "minecraft:grass_block"),
    ("structory:old_manor", "Old Manor", "An empty manor at the edge of the woods.", "minecraft:spruce_door"),
    ("structory:graveyard", "Graveyard", "Rest in peace. Please.", "minecraft:cobblestone"),
    ("philipsruins:ancient_ruins", "Ancient Ruins", "Old stones, older secrets.", "minecraft:chiseled_stone_bricks"),
    ("explorify:mausoleum", "Mausoleum", "A tomb on the surface.", "minecraft:polished_andesite"),
    ("born_in_chaos_v1:dark_tower_forest", "Dark Tower", "Chaos spills out of this tower at night.", "born_in_chaos_v1:dark_metal_deposit"),
    ("illagerinvasion:illusioner_tower", "Illusioner Tower", "Nothing in here is what it looks like.", "minecraft:spyglass"),
    ("illagerinvasion:labyrinth", "Illager Labyrinth", "The illagers built a maze. Of course they did.", "minecraft:stone_bricks"),
    ("friendsandfoes:citadel", "Illusioner Citadel", "A fortress of tricks.", "minecraft:amethyst_block"),
]
STRUCTURES_DEEP = [
    ("dungeons_arise:mining_system", "Mining System", "A whole underground mine, carts and all.", "minecraft:minecart"),
    ("dungeons_arise:foundry", "The Foundry", "Molten metal and the people who guard it.", "minecraft:blast_furnace"),
    ("dungeons_arise:mushroom_mines", "Mushroom Mines", "Glowing mushrooms in the dark.", "minecraft:mushroom_stew"),
    ("idas:ancient_mines", "Ancient Mines", "Older than the mineshafts.", "minecraft:iron_pickaxe"),
    ("philipsruins:ancient_crypt", "Ancient Crypt", "Bones and treasure.", "minecraft:skeleton_skull"),
    ("#nova_structures:undead_crypt", "Undead Crypt", "Something moves under the ground.", "minecraft:zombie_head"),
    ("minecraft:trial_chambers", "Trial Chambers", "Copper, breezes and trial keys.", "minecraft:trial_key"),
]
STRUCTURES_SEA = [
    ("dungeons_arise:undead_pirate_ship", "Undead Pirate Ship", "The crew is still on board.", "minecraft:oak_boat"),
    ("dungeons_arise:illager_galley", "Illager Galley", "Illagers... on a ship.", "minecraft:dark_oak_boat"),
    ("dungeons_arise:lighthouse", "The Lighthouse", "A light on the rocks.", "minecraft:sea_lantern"),
    ("aquamirae:pirate_ship", "Ice Maze Pirate Ship", "Captain Cornelia's frozen ship. Find it in the icy seas.", "aquamirae:frozen_key"),
    ("idas:sunken_ship/sunken_ship", "Sunken Ship", "It didn't make it home.", "minecraft:chest"),
    ("philipsruins:ocean_fortress", "Ocean Fortress", "A fortress rising out of the waves.", "minecraft:prismarine_bricks"),
]
STRUCTURES_NETHER = [
    ("incendium:forbidden_castle", "The Forbidden Castle", "The biggest castle in the Nether. Forbidden for a reason.", "minecraft:red_nether_bricks"),
    ("incendium:sanctum", "The Sanctum", "A holy place of fire.", "minecraft:crying_obsidian"),
    ("incendium:piglin_village", "Piglin Village", "Piglins have towns too.", "minecraft:gold_nugget"),
    ("incendium:nether_reactor", "Nether Reactor", "Something is still running in here.", "minecraft:redstone_lamp"),
    ("#nova_structures:nether_keep", "Nether Keep", "A dark keep of blackstone.", "minecraft:polished_blackstone_bricks"),
    ("#nova_structures:piglin_donjon", "Piglin Donjon", "A piglin dungeon tower.", "minecraft:gilded_blackstone"),
    ("repurposed_structures:city_nether", "Nether City", "A whole city of nether brick.", "minecraft:nether_bricks"),
]
STRUCTURES_END = [
    ("mes:enderkeep_courtyard", "Enderkeep Courtyard", "A castle courtyard on an outer island.", "minecraft:purpur_pillar"),
    ("mes:ender_spire", "Ender Spire", "A tall spire into the dark.", "minecraft:end_rod"),
    ("mes:phantom_citadel", "Phantom Citadel", "Home of the phantoms.", "minecraft:phantom_membrane"),
    ("mes:starlight_voyager", "Starlight Voyager", "A ship that sails the void.", "minecraft:chorus_flower"),
    ("#nova_structures:end_castle", "End Castle", "A castle at the end of the world.", "minecraft:end_stone_bricks"),
    ("nullscape:dragon_skeleton", "Dragon Skeleton", "There were other dragons once.", "minecraft:bone_block"),
    ("explorify:end_shipwreck", "End Shipwreck", "Even ships in the void can sink.", "minecraft:purpur_slab"),
]


def discover_structures():
    c = Chapter("discover_structures", "&eDiscoveries: Dungeons", "explorerscompass:explorerscompass", GROUP_SIDE,
                subtitle="Castles, crypts, ships and towers. Each one has loot for every player.")
    c.quest("start", "&eThe Explorer's Compass", 0, 0, [item("explorerscompass:explorerscompass")],
            desc=["The Explorer's Compass finds any structure you pick from a list.",
                  "Every chest has its own loot for each player (Lootr), so go together or go later, it's all yours."],
            deps=["phase_1_arrival:arrival"], rewards=[r_xp(50)], shape="hexagon", size=1.5)

    def section(key, title, x, y, entries, deps, xp, desc, icon):
        c.quest(key, title, x, y, [check("Got it")], desc=[desc], deps=deps, rewards=[r_xp(20)], optional=True, icon=icon)
        grid(c, [(f"s_{sid.lstrip('#').replace(':', '_').replace('/', '_')}", t, [structure(sid)], d, i)
                 for sid, t, d, i in entries], x + 2, y, 8, [key], xp=xp)

    section("surface", "&eOn the Surface", 0, -2, STRUCTURES_SURFACE, ["start"], 60,
            "When Dungeons Arise, IDAS, Towns and Towers, Moog's structures, Structory and more.", "minecraft:oak_door")
    section("deep", "&eUnder the Ground", 0, 4, STRUCTURES_DEEP, ["start"], 60,
            "Mines, crypts and chambers.", "minecraft:iron_pickaxe")
    section("sea", "&bOut at Sea", 0, 5.5, STRUCTURES_SEA, ["start"], 80,
            "Ships, lighthouses and fortresses on the water.", "minecraft:oak_boat")
    section("nether", "&cIn the Nether", 0, 7, STRUCTURES_NETHER, ["phase_7_fire:start"], 100,
            "Incendium's castles and more.", "minecraft:nether_bricks")
    section("end", "&5In the End", 0, 8.5, STRUCTURES_END, ["phase_8_one_way:arrive"], 120,
            "Moog's End Structures, Nullscape and more.", "minecraft:purpur_block")
    return c


def kitchen():
    c = Chapter("kitchen", "&eKitchen & Farm", "farmersdelight:cooking_pot", GROUP_SIDE,
                subtitle="Good food heals more and keeps you full longer. Cook together.")
    q = lambda key, title, x, y, tasks, desc, deps, icon=None, xp=40, rewards=(): c.quest(
        key, title, x, y, tasks, desc=desc, deps=deps, rewards=[r_xp(xp)] + list(rewards), optional=True, icon=icon)
    c.quest("start", "&eA Real Kitchen", 0, 0, [item("farmersdelight:cooking_pot"), item("farmersdelight:cutting_board")],
            desc=["&eFarmer's Delight&r is the heart of cooking here. A cooking pot over a fire or stove makes soups and meals.",
                  "A cutting board and a knife slice ingredients. Meals give long-lasting buffs (Nourishment, Comfort).",
                  "AppleSkin shows how filling each food is."],
            deps=["phase_1_arrival:arrival"], rewards=[r_xp(60), r_item("farmersdelight:tomato", 4)], shape="hexagon", size=1.5)
    # Farming
    q("knife", "A Kitchen Knife", 2, -2, [item("farmersdelight:iron_knife")], ["Knives slice food and get extra drops (leather, ham) from animals."], ["start"])
    q("crops", "The Garden", 2, 2, [item("farmersdelight:tomato"), item("farmersdelight:cabbage"), item("farmersdelight:onion"), item("farmersdelight:rice")],
      ["Wild crops grow all over the world. Break them for seeds."], ["start"], icon="farmersdelight:cabbage")
    q("rich_soil", "Rich Soil", 4, 2, [item("farmersdelight:rich_soil", 4)], ["Organic compost turns into Rich Soil, which makes crops grow faster."], ["crops"])
    q("peppers", "Spice it Up", 4, 3.5, [item("rusticdelight:coffee_beans"), item("expandeddelight:chili_pepper")],
      ["Rustic Delight adds coffee and bell peppers; Expanded Delight adds chili, peanuts, cinnamon and cheese."], ["crops"], icon="expandeddelight:chili_pepper")
    q("orchard", "The Orchard", 6, 2, [item("bountifulfares:orange"), item("bountifulfares:lemon")],
      ["Bountiful Fares adds fruit trees, teas and a gristmill for flour."], ["rich_soil"], icon="bountifulfares:orange")
    q("vineyard", "The Vineyard", 6, 3.5, [item("vinery:red_grape")],
      ["Let's Do Vinery: plant grapevines on a trellis, then press and ferment them into wine."], ["peppers"], icon="vinery:red_grape")
    # Cooking
    q("meal", "A Proper Meal", 2, 0, [item("farmersdelight:beef_stew")], ["Cook a stew in the pot. Bowls go in the bottom slot."], ["start"])
    q("feast", "A Feast", 4, 0, [item("farmersdelight:roast_chicken_block")],
      ["Feasts are placed on a table and everyone can take a serving. Perfect after a boss fight."], ["meal"], xp=80)
    q("cheese", "Say Cheese", 4, -1.5, [item("expandeddelight:cheese_wheel")], ["Age milk in a cask into a wheel of cheese."], ["meal"])
    q("keg", "Brewin' and Chewin'", 6, -1.5, [item("brewinandchewin:keg"), item("brewinandchewin:beer")],
      ["A keg ferments drinks: beer, mead, rice wine... and makes cheese too."], ["cheese"], icon="brewinandchewin:keg")
    q("wine", "Fine Wine", 8, 3.5, [item("vinery:fermentation_barrel")], ["Wine gets better the longer it ages."], ["vineyard"])
    q("blockheads", "Cooking for Blockheads", 6, 0, [item("cookingforblockheads:cooking_table")],
      ["A cooking table shows every recipe you can make from the food in your kitchen. Add a fridge, an oven and a sink."], ["feast"], xp=60)
    # Create
    q("slicer", "&6Create:&r Slice & Dice", 8, -1.5, [item("sliceanddice:slicer")],
      ["The Slicer uses a knife on a cutting board for you. The Sprinkler waters your farm."], ["blockheads"], icon="sliceanddice:slicer", xp=80)
    q("central_kitchen", "&6Create:&r Central Kitchen", 8, 0, [item("create:mechanical_mixer"), item("create:basin")],
      ["With Create Central Kitchen, a mixer and a heated basin cook Farmer's Delight pot recipes on their own.",
       "Deployers can use cutting boards. Your whole kitchen can run itself."], ["blockheads"], icon="create:mechanical_mixer", xp=80)
    # Other worlds
    q("sea_food", "Food from the Sea", 0, 3.5, [item("oceansdelight:guardian_soup")],
      ["Ocean's Delight cooks squid, guardians and more."], ["phase_5_sea:start"], icon="oceansdelight:guardian_soup", xp=60)
    q("nether_food", "&cNether's Delight", 0, 5, [item("mynethersdelight:nether_stove")],
      ["Hoglins, striders and ghasts are food too, if you're brave. Cook on a Nether stove."], ["phase_7_fire:start"], xp=80)
    q("end_food", "&5End's Delight", 2, 5, [item("ends_delight:end_stove")],
      ["Chorus, shulker meat and even dragon. Cook on an End stove."], ["phase_8_one_way:arrive"], xp=100)
    return c


def create_side():
    c = Chapter("create_side", "&6Create Workshop", "create:cogwheel", GROUP_SIDE,
                subtitle="Machines that are fun to build. None of these are required.")
    c.quest("start", "&6The Workshop", 0, 0, [item("create:goggles")],
            desc=["Engineer's Goggles show the stress and speed of your machines.",
                  "Hold &eW&r over any Create item for a Ponder scene."],
            deps=["phase_1_arrival:alloy"], rewards=[r_xp(40)], shape="hexagon", size=1.5)
    entries = [
        ("windmill", "Wind Power", [item("create:windmill_bearing"), item("create:white_sail", 8)], "A windmill makes power anywhere, no water needed.", "create:windmill_bearing"),
        ("belts", "Conveyor Belts", [item("create:belt_connector", 8)], "Move items around your base. Use dried kelp, it's the recipe.", "create:belt_connector"),
        ("fan", "Bulk Processing", [item("create:encased_fan")], "A fan through lava smelts, through fire smokes, through water washes.", "create:encased_fan"),
        ("crusher", "Crushing Wheels", [item("create:crushing_wheel", 2)], "Double your ores, and get extra goodies from gravel.", "create:crushing_wheel"),
        ("farm", "Automatic Farm", [item("create:mechanical_harvester"), item("create:mechanical_plough")], "Put them on a moving contraption and drive over your fields.", "create:mechanical_harvester"),
        ("saw", "Tree Farm", [item("create:mechanical_saw")], "Saws cut whole trees at once.", "create:mechanical_saw"),
        ("fluids", "Pipes and Pumps", [item("create:mechanical_pump"), item("create:fluid_tank", 4)], "Move water, lava, honey and more.", "create:mechanical_pump"),
        ("spout", "Spouts and Drains", [item("create:spout"), item("create:item_drain")], "Fill and empty bottles, buckets and potions automatically.", "create:spout"),
        ("steam", "Steam Engine", [item("create:steam_engine")], "The strongest power in Create. Boil water on a heated tank.", "create:steam_engine"),
        ("crafter", "Mechanical Crafters", [item("create:mechanical_crafter", 4)], "Craft the big recipes automatically.", "create:mechanical_crafter"),
        ("vault", "Item Vault", [item("create:item_vault", 4)], "A big, simple storage block.", "create:item_vault"),
        ("logistics", "Stock and Packages", [item("create:stock_ticker"), item("create:packager")], "Create's logistics: order anything from your storage and have it delivered.", "create:stock_ticker"),
        ("chain", "Chain Conveyors", [item("create:chain_conveyor", 2)], "Send packages across your base on chains.", "create:chain_conveyor"),
        ("display", "Display Boards", [item("create:display_board", 4)], "Show train times, stock levels or a message for your friends.", "create:display_board"),
        ("schematic", "Schematicannon", [item("create:schematicannon")], "Let a cannon build your schematics.", "create:schematicannon"),
        ("cannon", "Potato Cannon", [item("create:potato_cannon")], "Yes, it shoots potatoes. Yes, it hurts.", "create:potato_cannon"),
        ("diving", "Diving Gear", [item("create:copper_diving_helmet"), item("create:copper_backtank")], "Breathe underwater for a long time.", "create:copper_diving_helmet"),
        ("extendo", "Extendo Grip", [item("create:extendo_grip")], "Reach far. Very useful for building.", "create:extendo_grip"),
        ("controller", "Linked Controller", [item("create:linked_controller")], "Control machines from a distance with redstone links.", "create:linked_controller"),
        ("haunted", "Haunted Bell", [item("create:haunted_bell")], "Ring it to see where mobs can spawn.", "create:haunted_bell"),
    ]
    grid(c, entries, 2, -1.5, 5, ["start"], xp=60, step=1.75)
    return c


def magic_side():
    c = Chapter("magic_side", "&9Arcane Studies", "irons_spellbooks:arcane_essence", GROUP_SIDE,
                subtitle="More spells, better books, magic helpers.")
    c.quest("start", "&9The Study", 0, 0, [item("irons_spellbooks:inscription_table")],
            desc=["Two magic mods, no classes. Iron's Spells is about finding and upgrading spells,",
                  "Ars Nouveau is about building your own."],
            deps=["phase_1_arrival:spellbook"], rewards=[r_xp(40)], shape="hexagon", size=1.5)
    irons = [
        ("iron_book", "Iron Spell Book", [item("irons_spellbooks:iron_spell_book")], "More slots for more spells.", None),
        ("gold_book", "Gold Spell Book", [item("irons_spellbooks:gold_spell_book")], "Even more slots.", None),
        ("diamond_book", "Diamond Spell Book", [item("irons_spellbooks:diamond_spell_book")], "A book for a real wizard.", None),
        ("scroll_forge", "Scroll Forge", [item("irons_spellbooks:scroll_forge")], "Write your own scrolls with ink and paper.", None),
        ("cauldron", "Alchemist Cauldron", [item("irons_spellbooks:alchemist_cauldron")], "Brew potions and break down scrolls into ink.", None),
        ("upgrade_orb", "Upgrade Orbs", [item("irons_spellbooks:upgrade_orb")], "Upgrade your mage armor at the arcane anvil.", None),
        ("mana_ring", "Ring of Mana", [item("irons_spellbooks:mana_ring")], "Rings and amulets go in your Curios slots.", None),
        ("mage_armor", "Pyromancer Robes", [item("irons_spellbooks:pyromancer_chestplate")], "Every school has its own armor: fire, ice, lightning, holy, ender, blood, evocation...", None),
        ("mithril", "Mithril", [item("irons_spellbooks:mithril_ingot")], "Rare and strong. Look deep underground for mithril ore.", None),
        ("dead_king", "&5The Dead King", [kill("irons_spellbooks:dead_king")], "Somewhere in a cursed catacomb, a king still sits on his throne.", "minecraft:wither_skeleton_skull"),
        ("archevoker", "&5The Archevoker", [kill("irons_spellbooks:archevoker")], "The greatest of the evoker mages.", "minecraft:totem_of_undying"),
    ]
    grid(c, [(k, "&9Iron's:&r " + t, ts, d, i) for k, t, ts, d, i in irons], 2, -1.5, 6, ["start"], xp=60)
    c.quest("ars_start", "&dArs Nouveau", 0, 3, [item("ars_nouveau:scribes_table")],
            desc=["Read the &eWorn Notebook&r. Glyphs are crafted at the Scribe's Table and put into your spell book."],
            deps=["start"], rewards=[r_xp(40)], optional=True, icon="ars_nouveau:worn_notebook")
    ars = [
        ("source", "Source Jar", [item("ars_nouveau:source_jar")], "Source powers everything in Ars Nouveau.", None),
        ("sourcelink", "Sourcelinks", [item("ars_nouveau:agronomic_sourcelink")], "Make source from growing plants, fire, mushrooms or potions.", None),
        ("imbuement", "Imbuement Chamber", [item("ars_nouveau:imbuement_chamber")], "Turn gems into source gems.", None),
        ("apparatus", "Enchanting Apparatus", [item("ars_nouveau:enchanting_apparatus"), item("ars_nouveau:arcane_core")], "Craft magical items on pedestals.", None),
        ("apprentice", "Apprentice Spell Book", [item("ars_nouveau:apprentice_spell_book")], "More glyphs per spell.", None),
        ("archmage", "Archmage Spell Book", [item("ars_nouveau:archmage_spell_book")], "Everything Ars Nouveau can do.", None),
        ("starbuncle", "A Starbuncle Friend", [item("ars_nouveau:starbuncle_charm")], "A little helper that carries items between chests.", None),
        ("whirlisprig", "Whirlisprig", [item("ars_nouveau:whirlisprig_charm")], "It helps your plants grow.", None),
        ("ritual", "Rituals", [item("ars_nouveau:ritual_brazier")], "Rituals change the weather, the time of day and more.", None),
        ("wilden", "&5The Wilden Chimera", [kill("ars_nouveau:wilden_boss")], "Call it with a ritual. Hunters, stalkers and guardians all in one.", "ars_nouveau:wilden_horn"),
    ]
    grid(c, [(k, "&dArs:&r " + t, ts, d, i) for k, t, ts, d, i in ars], 2, 3, 6, ["ars_start"], xp=60)
    c.quest("imbuing", "Illager Imbuing Table", 0, 6, [item("illagerinvasion:imbuing_table")],
            desc=["Illager Invasion's Imbuing Table pushes an enchantment one level past its normal max.",
                  "You need a Hallowed Gem from the Invoker."],
            deps=["start"], rewards=[r_xp(80)], optional=True)
    return c


def gear():
    c = Chapter("gear", "&6Treasure & Monsters", "artifacts:cloud_in_a_bottle", GROUP_SIDE,
                subtitle="Mini-bosses, rare finds and cool gear.")
    c.quest("start", "&6Treasure Hunter", 0, 0, [check("Let's go")],
            desc=["Loot is per player, so every chest is worth opening.",
                  "Artifacts hide in chests and in &cmimics&r (chests that bite)."],
            deps=["phase_2_ruins:start"], rewards=[r_xp(20)], shape="hexagon", size=1.5, icon="minecraft:chest")
    finds = [
        ("cloud", "Cloud in a Bottle", [item("artifacts:cloud_in_a_bottle")], "Double jump!", None),
        ("shoes", "Running Shoes", [item("artifacts:running_shoes")], "Sprint faster, step up blocks.", None),
        ("claws", "Digging Claws", [item("artifacts:digging_claws")], "Mine faster with your bare hands.", None),
        ("flippers", "Flippers", [item("artifacts:flippers")], "Swim a lot faster.", None),
        ("heart", "Crystal Heart", [item("artifacts:crystal_heart")], "More health.", None),
        ("mimic", "Not a Chest", [kill("artifacts:mimic")], "That chest had teeth.", "minecraft:chest"),
        ("runic", "Runic Tablet", [item("simplyswords:runic_tablet")], "Simply Swords' runic weapons get a random power from these.", None),
        ("netherfused", "Netherfused Gem", [item("simplyswords:netherfused_gem")], "Fuse a gem into a weapon for a special ability.", None),
        ("backpack_upgrade", "Better Backpack", [item("sophisticatedbackpacks:iron_backpack")], "Upgrade your backpack: more slots, then magnets, feeders and more.", None),
        ("dark_metal", "Dark Metal", [item("born_in_chaos_v1:dark_metal_ingot")], "Born in Chaos's monsters drop it. Their gear is nasty.", None),
        ("platinum", "Platinum", [item("illagerinvasion:platinum_chunk")], "Illager Invasion's metal, for platinum tools.", None),
        ("frozen_key", "The Frozen Key", [item("aquamirae:frozen_key")], "Opens the frozen chests of the Ice Maze.", None),
    ]
    grid(c, finds, 2, -1.5, 6, ["start"], xp=60)
    c.quest("monsters", "&cMini-Bosses", 0, 3.5, [check("Bring friends")],
            desc=["Not quest bosses, but they drop great stuff. Shared credit doesn't apply here: everyone wants the loot."],
            deps=["start"], rewards=[r_xp(20)], optional=True, icon="minecraft:zombie_head")
    bosses = [
        ("pumpkinhead", "Lord Pumpkinhead", [kill("born_in_chaos_v1:lord_pumpkinhead")], "He rides a dark horse on Halloween nights... and other nights.", "minecraft:carved_pumpkin"),
        ("bonescaller", "Supreme Bonescaller", [kill("born_in_chaos_v1:supreme_bonescaller")], "A skeleton mage that calls more skeletons.", "minecraft:bone"),
        ("chaos_knight", "Fallen Chaos Knight", [kill("born_in_chaos_v1:fallen_chaos_knight")], "A knight in black armor.", "minecraft:netherite_sword"),
        ("cornelia", "Captain Cornelia", [kill("aquamirae:captain_cornelia")], "The pirate captain of the Ice Maze.", "aquamirae:terrible_blade" if False else "aquamirae:dagger_of_greed"),
        ("maze_mother", "Maze Mother", [kill("aquamirae:maze_mother")], "Something huge lives under the frozen sea.", "aquamirae:maze_rose"),
        ("wildfire", "The Wildfire", [kill("friendsandfoes:wildfire")], "The blazes' queen. Her crown is a trophy.", "friendsandfoes:wildfire_crown"),
        ("invoker", "The Invoker", [kill("illagerinvasion:invoker")], "The strongest illager mage. Drops the Hallowed Gem.", "illagerinvasion:hallowed_gem"),
        ("warden", "The Warden", [kill("minecraft:warden")], "Do you really want to? Optional. Very optional.", "minecraft:sculk_shrieker"),
    ]
    grid(c, bosses, 2, 3.5, 6, ["monsters"], xp=150)
    return c


def life():
    c = Chapter("life", "&aLife & Travel", "waystones:waystone", GROUP_SIDE,
                subtitle="Things that make the world nicer to live in.")
    c.quest("start", "&aHome Sweet Home", 0, 0, [check("Got it")],
            desc=["Claim your land with FTB Chunks (open the map with &eM&r and drag over chunks): nobody can grief it.",
                  "Talk with proximity voice chat (Simple Voice Chat, key &eV&r to configure)."],
            deps=["phase_1_arrival:arrival"], rewards=[r_xp(20)], shape="hexagon", size=1.5, icon="minecraft:oak_door")
    entries = [
        ("sleeping_bag", "Sleeping Bag", [item("comforts:sleeping_bag_red")], "Sleep anywhere without moving your spawn point.", None),
        ("hammock", "Hammock", [item("comforts:hammock_white")], "Nap through the day.", None),
        ("furniture", "Furniture", [item("handcrafted:oak_table"), item("handcrafted:oak_chair")], "Handcrafted adds tables, chairs, couches, shelves and more.", "handcrafted:oak_chair"),
        ("sack", "Sacks and Jars", [item("supplementaries:sack"), item("supplementaries:jar")], "Supplementaries: carry things, store fireflies, decorate.", None),
        ("rope", "Rope", [item("supplementaries:rope", 16)], "Climb down and pull things up.", None),
        ("globe", "A Globe", [item("supplementaries:globe")], "Spin it.", None),
        ("quiver", "Quiver", [item("supplementaries:quiver")], "Hold many kinds of arrows at once.", None),
        ("slingshot", "Slingshot", [item("supplementaries:slingshot")], "Throw blocks where you aim.", None),
        ("warp_scroll", "Warp Scroll", [item("waystones:warp_scroll")], "Teleport to any waystone you know, once.", None),
        ("return_scroll", "Return Scroll", [item("waystones:return_scroll")], "Back to your bound waystone.", None),
        ("warp_plate", "Warp Plates", [item("waystones:warp_plate", 2)], "Step on one, appear at the other.", None),
        ("pouch", "Bigger Backpack", [item("sophisticatedbackpacks:gold_backpack")], "More space, more upgrades.", None),
        ("magnet", "Backpack Magnet", [item("sophisticatedbackpacks:magnet_upgrade")], "Pulls items into your backpack.", None),
        ("grave", "Grave Matters", [check("I know where my grave is")], "When you die, a gravestone keeps your items. Only you can open it.", "gravestone:gravestone"),
    ]
    grid(c, entries, 2, -1.5, 5, ["start"], xp=40, step=1.75)
    return c


# ---------------------------------------------------------------- ID check

IDS_FILE = ROOT / "tools/.ids.json"
OWN_NAMESPACES = {"ultimate", "ftbquests"}


def validate(chapters):
    """Refuse to write quests that point at items, mobs, structures or biomes that don't exist.
    tools/.ids.json comes from tools/mod_ids.py; re-run it after adding mods."""
    if not IDS_FILE.exists():
        print("warning: tools/.ids.json missing, run tools/mod_ids.py to check IDs", file=sys.stderr)
        return
    known = {k: set(v) for k, v in json.loads(IDS_FILE.read_text()).items() if k != "unchecked"}
    bad = []

    def need(kind, id, where):
        if id.lstrip("#").split(":")[0] not in OWN_NAMESPACES and id not in known[kind]:
            bad.append(f"{where}: unknown {kind} {id}")

    all_ids = {q["id"] for c in chapters for q in c.quests}
    for c in chapters:
        need("item", c.icon, f"chapter {c.key}")
        for q in c.quests:
            if any(d not in all_ids for d in q.get("dependencies", [])):
                bad.append(f"{c.key}: a dependency of {q['id']} points at a quest that doesn't exist")
        for q in c.quests:
            where = c.key + ":" + LANG.get("quest." + q["id"] + ".title", q["id"])
            if "icon" in q:
                need("item", q["icon"]["id"], where)
            for t in q["tasks"] + q.get("rewards", []):
                if t["type"] == "item":
                    need("item", t["item"]["id"], where)
                elif t["type"] == "kill":
                    need("entity", t["entity"], where)
                elif t["type"] in ("structure", "biome"):
                    need(t["type"], t[t["type"]], where)
    if bad:
        print("\n".join(bad), file=sys.stderr)
        sys.exit(f"{len(bad)} unknown IDs; fix them (or re-run tools/mod_ids.py if you added mods)")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    chapters = [welcome(), phase1(), phase2(), phase3(), phase4(), phase5(), phase6(),
                phase7(), phase8(), phase9(), phase10(),
                discover_biomes(), discover_structures(), kitchen(), create_side(), magic_side(), gear(), life()]
    validate(chapters)

    write(OUT / "data.snbt", {
        "default_autoclaim_rewards": "disabled",
        "default_consume_items": False,
        "default_quest_disable_jei": False,
        "default_quest_shape": "circle",
        "default_reward_team": False,
        "detection_delay": 20,
        "disable_gui": False,
        "drop_loot_crates": False,
        "emergency_items_cooldown": 300,
        "grid_scale": D(0.5),
        "icon": {"id": "ultimate:tempering_kit_10"},
        "lock_message": "",
        "pause_game": False,
        "progression_mode": "linear",
        "show_lock_icons": True,
        "version": 13,
    })
    LANG["file.0000000000000001.title"] = "Ultimate Pack"
    write(OUT / "chapter_groups.snbt", {"chapter_groups": [{"id": gid} for gid, _ in GROUPS]})
    for gid, title in GROUPS:
        LANG[f"chapter_group.{gid}.title"] = title
    for order, chapter in enumerate(chapters):
        write(OUT / "chapters" / f"{chapter.key}.snbt", chapter.to_snbt(order))
    write(OUT / "lang" / "en_us.snbt", LANG)

    total = sum(len(c.quests) for c in chapters)
    print(f"wrote {len(chapters)} chapters, {total} quests to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
