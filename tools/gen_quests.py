#!/usr/bin/env python3
"""Generate the FTB Quests book for Ultimate Pack.

Run from the repo root:  python3 tools/gen_quests.py
Writes config/ftbquests/quests/. Quest IDs are derived from stable keys, so
re-running keeps everyone's progress. Never rename a quest key once released.
"""
import hashlib
import shutil
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
GROUPS = [(GROUP_ACT1, "&aAct I — The Land"), (GROUP_ACT2, "&bAct II — The Frontier")]


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
                "The Nether and the End are &csealed&r for now. You will open them together.",
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
                "Every quest boss has a craftable &dEcho&r. Right-click it in the Overworld to call that boss to you.",
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
                  "This is the end of Act II. The Nether is open. Act III is coming in the next update."],
            deps=["harbinger"], icon="ultimate:tempering_kit_6")
    return c


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    chapters = [welcome(), phase1(), phase2(), phase3(), phase4(), phase5(), phase6()]

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
        "icon": {"id": "ultimate:tempering_kit_6"},
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
