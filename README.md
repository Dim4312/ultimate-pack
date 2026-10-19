# Ultimate Pack

[![Server boot test](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml/badge.svg)](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml)

A co-op **combat + magic + Create** modpack for Minecraft **1.21.1 / NeoForge** for a group of about 10 friends on one always-on server.

**One world, play together, create — don't grind.**

- **No classes.** Everyone can use swords *and* spells (Simply Swords, Better Combat, Iron's Spells, Ars Nouveau).
- **Clear direction.** 430 quests in 24 chapters cover 10 story phases, flight lessons, storage, cooking, magic, wildlife, boss hunting, shared builds and life after the dragon. JEI and Create's Ponder explain the machines.
- **Upgrades = materials + a quest.** There's no drop-rate grind: beat a phase's Trial, craft a Tempering Kit, and upgrade any weapon, staff or Ars spellbook.
- **Bosses you can beat in an evening.** They have real mechanics (Mowzie's Mobs, L_Ender's Cataclysm, Legendary Monsters, Bosses'Rise, Bosses of Mass Destruction) and take less damage per extra player, so a group still gets a real fight. Multiplayer Bosses gives every player their own loot bag, and Enhanced Boss Bars shows who you're fighting. Everyone nearby gets credit. Echoes let anyone fight a boss again.
- **A world worth exploring:** Tectonic terrain with taller mountains (world height up to Y448), Terralith's 95+ biomes (canyons, Yellowstone, volcanoes, floating islands), William Wythers' Overhauled Overworld for huge, realistic vanilla forests, Nature's Spirit + Oh The Biomes We've Gone biomes, Windswept for richer snowy and forest areas, Falling Leaves and Snow Under Trees, YUNG's Cave Biomes underground. Distant Horizons shows mountains kilometres away (optional; untick it on the first-launch screen if your PC struggles).
- **Runs well:** Sodium (+ Sodium Extra, Reese's Sodium Options), Lithium, ModernFix, FerriteCore, ImmediatelyFast, Entity Culling, More Culling, Cull Leaves, BadOptimizations, Dynamic FPS, Particle Core, Structure Layout Optimizer, AI Improvements, Clumps, FastFurnace/FastWorkbench/FastSuite, Noisium (worldgen), Async Locator (compasses and `/locate` don't freeze the server), Ksyxis (faster world loading), Let Me Despawn, C2ME (multi-threaded chunk loading), Flerovium, Fast Paintings, Krypton Reno (network). The server also runs ServerCore (backs off view distance and mob caps when it lags), Immersive Optimization (distant mobs tick less; Create, airships and bosses are excluded), Alternate Current (redstone) and Leaves Be Gone. Neruina stops one broken mob or block from crashing the world. New players get light default video settings.
- **Wildlife and monsters:** Alex's Mobs and Alex's Caves (Continued; the nuke is half size and Tremorzilla's beam doesn't break blocks), Critters and Companions, Hybrid Aquatic, Creeper Overhaul and Enderman Overhaul (a different creeper and enderman for each biome), Nyf's Spiders, Spawn Animations.
- **Adventure everywhere:** When Dungeons Arise, IDAS, Dungeons and Taverns, Moog's structures, Towns and Towers, Repurposed Structures, Incendium, Nullscape, YUNG's, Born in Chaos, Aquamirae, Illager Invasion, Friends and Foes, Artifacts.
- **Cooking and farming:** Farmer's Delight with Expanded, Rustic, Ocean's, Nether's and End's Delight, Brewin' and Chewin', Vinery, Bountiful Fares, Cooking for Blockheads, and Create Central Kitchen / Slice and Dice to automate it.
- **A shared workshop:** Storage Drawers handles bulk materials; Create logistics handles stock lists, orders and deliveries. Flight School teaches a first ship before the End expedition.
- **Three worlds only:** Overworld, Nether, End. No extra dimensions to split the server.
- **Late joiners catch up.** Loot is per player (Lootr), boss credit is shared, and server-wide gates move the story forward for everyone.

See [DESIGN.md](DESIGN.md) for the full design, [REVIEW.md](REVIEW.md) for the v0.4 audit,
and [WORLDGEN.md](WORLDGEN.md) for the terrain investigation and measured profile comparison.

## Status — v0.4

| | |
|---|---|
| ✅ **Act I — The Land** | Phase 1 Arrival · Phase 2 Ruins · Phase 3 The Deep (Ferrous Wroughtnaut) |
| ✅ **Act II — The Frontier** | Phase 4 Far Lands (beat 2 of 4: Frostmaw, Umvuthi, Maledictus, Ancient Remnant) · Phase 5 The Sea (Leviathan) · Phase 6 The Forge (Harbinger) |
| ✅ **Act III — The Nether** | Phase 7 The Fire (Netherite Monstrosity + Ignis). Opens when the Harbinger first falls. |
| ✅ **Act IV — The End: New World** | Phase 8 One Way (Ender Guardian). Opens when Ignis first falls. The portal drops you on a far outer island and there is no way home. |
| ✅ **Act V — The End: The Way Back** | Phase 9 The Way Back (build and wake the Return Gate) · Phase 10 The Dragon (wings fail near its island; build an airship) |
| ✅ **Side quests** | Biome and dungeon discoveries, Kitchen & Farm, Create Workshop, Arcane Studies, Treasure & Monsters, Life & Travel, Flight School, Storage & Logistics, Our Shared World. All optional. |
| ✅ **After the Dragon** | Dragon resummoning and breath supplies, optional bosses, beacons, a fleet and shared projects. |
| 🔜 Later | The Dragon's Echo: End raids and dragon pacts after the dragon is dead. |

## Playing (Prism Launcher)

1. Install [Prism Launcher](https://prismlauncher.org/).
2. Download **UltimatePack-client.zip** from the [latest release](https://github.com/Dim4312/ultimate-pack/releases/latest). All mods are already inside.
3. In Prism, **Add Instance → Import** and pick the zip, or paste this URL:
   `https://github.com/Dim4312/ultimate-pack/releases/latest/download/UltimatePack-client.zip`
4. Launch. Every launch checks this repo and downloads only what changed.

**Shaders (optional):** tick *Iris*, *Euphoria Patches* and *Complementary Reimagined* on the first-launch screen, then pick the shader under Options → Video Settings → Shader Packs. They need a strong GPU, and Create airships can look glitchy with shaders on.

**Testing alone?** Download **UltimatePack-solo.zip** instead and import it the same way. It has every client *and* server mod, so you can play singleplayer without hosting a server. It is a fixed snapshot of that release and doesn't auto-update. Iris and the shaders are preinstalled but stay off until you pick a shader pack. It uses 8 GB of RAM by default. Pre-releases (tags like `v0.5.0-test.1`) are test builds from the `dev` branch.

The instance uses 6 GB of RAM by default. Change it in *Edit → Settings → Java*. Prism downloads Java 21 for you if you don't have it.

If the game stutters, open *Options → Video Settings*. Lower the render distance, or open the Distant Horizons button and turn off rendering. Distant Horizons is the heaviest mod in the pack.

Particle Rain is an optional cosmetic mod, off by default. On new installs, Iron's spell wheel is **X** and casting is **Z**; **R** is dodge and **V** opens voice chat. Existing players keep their key settings; change them in *Options → Controls* if needed.

## Hosting the server

You need Java 21. The server launcher allocates 8 GB of RAM by default; leave additional memory for the operating system.

Download **UltimatePack-server.zip** from the [latest release](https://github.com/Dim4312/ultimate-pack/releases/latest) and unzip it into an empty folder. It already contains all server mods, configs and scripts.

```bash
cd ultimate-server
echo eula=true > eula.txt      # you accept https://aka.ms/MinecraftEULA
./start.sh                      # Linux/macOS. MEMORY=10G ./start.sh for more RAM
```

On Windows, write `eula=true` into `eula.txt` and double-click `start.bat`.

On the first run, the start script installs NeoForge 21.1.262 and writes sensible `server.properties`: `allow-flight=true` (so Create contraptions don't kick players) and `spawn-protection=0`. On **every** run it syncs server-side mods, configs and scripts from this repo. Client-only mods such as Sodium are skipped.

If your host runs a panel such as Pterodactyl and can't run scripts, install NeoForge 21.1.262 with the panel. Then add `java -jar packwiz-installer-bootstrap.jar -g -s server https://raw.githubusercontent.com/Dim4312/ultimate-pack/main/pack.toml` as a startup step, or run it once over SSH or SFTP.

### Admin commands (op level 2)

| Command | What it does |
|---|---|
| `/ultimate status` | Shows Nether/End gate state and every online player's latest Trial |
| `/ultimate gate nether open\|close` | Opens or seals the Nether manually |
| `/ultimate gate end open\|close` | Opens or seals the End manually |
| `/ultimate returngate reset` | Puts the Return Gate back to sleep (the End becomes one-way again) |
| `/ultimate arrival` | Shows the outer island where the End portal drops players |
| `/ultimate terrain` | Checks the active Tectonic pack and displays the effective terrain settings |

## Systems in short

- **Tempering:** claim the Phase N Trial rewards to learn *Tempering N*. Hold a *Tempering Kit N* in one hand and a melee weapon, staff or Ars spellbook in the other, then right-click. Each level gives +12% melee damage, +6% Iron's spell power and +6% Ars spell damage (up to +120% / +60% / +60% at X). Equipment keeps its own stats and effects.
- **Boss Echoes:** craft one from an echo shard and themed blocks, then right-click it where that boss lives (Overworld, Nether or End) to call it. Two amethyst shards, two copper ingots and a sculk block craft two echo shards, so refights do not depend on finite chest loot. The Leviathan only answers in water. A Harbinger Echo used on a dormant Harbinger wakes it. Failed summons keep the Echo.
- **Spawn-safe zone:** Phase 4+ bosses never appear within 1000 blocks of spawn. Echo-called bosses are exempt.
- **Boss scaling:** with N players within 48 blocks, a boss takes `1 / (1 + 0.65·(N−1))` damage.
- **The End is one-way:** the stronghold portal throws you onto an outer island (the same one for everyone) and nothing takes you back, except death. Someone who beat the Ender Guardian wakes a craftable Return Gate. After that the gate takes anyone home, and the portal brings anyone to the gate. Elytra don't work within 1000 blocks of the dragon's island until the dragon is dead.
- **Overworld Blaze Burner:** the Nether is sealed through Act II, so Create's Blaze Burner can be crafted from magma blocks, a lava bucket and a coal block instead.
- **Return Gate recovery:** leave two air blocks above it. If it is removed or obstructed, portal arrivals use the original outer island and travel home stays unlocked. Use a replacement gate to register its position. Late joiners can complete Phase 9 using the existing gate.
- **Exploration spacing:** decorative structures keep Sparse Structures' wider spacing. Required story destinations retain their normal spacing in new chunks.
- **Terrain:** an explicit Tectonic profile creates more frequent elevation changes while keeping the existing world-height limits. Restart after updating and test in new chunks or a fresh world; previously generated terrain keeps its shape. In multiplayer the server controls this setting. See [WORLDGEN.md](WORLDGEN.md).

## Developing

The pack is managed with [packwiz](https://packwiz.infra.link/).

```bash
packwiz modrinth add <mod>     # add a mod
python3 tools/gen_quests.py    # regenerate the quest book from code
python3 tools/mod_ids.py       # collect IDs from the pinned mod jars
python3 tools/gen_quests.py --check  # validate IDs, graph and generated files
python3 -m unittest discover -s tools -p 'test_*.py'
node --test tools/test_gameplay.mjs
python3 tools/gen_textures.py  # regenerate item textures
packwiz refresh                # always run before committing
git tag v0.x.0 && git push --tags   # GitHub builds UltimatePack-client.zip + UltimatePack-server.zip into the release
```

The quest book is generated from `tools/gen_quests.py`, so edit that file instead of the SNBT. IDs stay stable to preserve existing progress. Gameplay logic lives in `kubejs/` (Tempering, bosses, gates, recipes). CI validates the generated book and runs progression checks before booting a real server; crashes and KubeJS errors fail the workflow (`.github/workflows/server-test.yml`). Event tests use mocks and complement the server test; they do not establish in-game compatibility or performance.

CI downloads the pinned Packwiz installer release asset directly, then skips the bootstrap's GitHub API update lookup. Server launchers accept `PACKWIZ_BOOTSTRAP_NO_UPDATE=1` when a nonempty `packwiz-installer.jar` has already been supplied. Pack synchronization still runs normally.

## Credits & license

Pack files (scripts, quests, configs, textures, tools) are MIT-licensed. Every mod is downloaded from Modrinth or CurseForge by its authors' official files and keeps its own license. Nothing is redistributed here.
