# Ultimate Pack

[![Server boot test](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml/badge.svg)](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml)

A co-op **combat + magic + Create** modpack for Minecraft **1.21.1 / NeoForge** for a group of about 10 friends on one always-on server.

**One world, play together, create — don't grind.**

- **No classes.** Everyone can use swords *and* spells (Simply Swords, Better Combat, Iron's Spells, Ars Nouveau).
- **Clear direction.** A quest book (FTB Quests) leads you through 10 phases. JEI and Create's Ponder explain the machines.
- **Upgrades = materials + a quest.** There's no drop-rate grind: beat a phase's Trial, craft a Tempering Kit, and upgrade any weapon or staff.
- **Bosses you can beat in an evening.** They have real mechanics (Mowzie's Mobs, L_Ender's Cataclysm) and scale with group size. Everyone nearby gets credit. Echoes let anyone fight a boss again.
- **A world worth exploring:** Tectonic terrain, Nature's Spirit + Oh The Biomes We've Gone biomes, Windswept for richer snowy and forest areas, YUNG's Cave Biomes underground. Distant Horizons shows mountains kilometres away (optional; untick it on the first-launch screen if your PC struggles).
- **Runs well:** Sodium (+ Sodium Extra, Reese's Sodium Options), Lithium, ModernFix, FerriteCore, ImmediatelyFast, Entity Culling, More Culling, Cull Leaves, BadOptimizations, Dynamic FPS, Particle Core, Structure Layout Optimizer, AI Improvements, Clumps, FastFurnace/FastWorkbench/FastSuite, ScalableLux (lighting), Noisium (worldgen), Async Locator (compasses and `/locate` don't freeze the server), Ksyxis (faster world loading), Let Me Despawn. New players get light default video settings.
- **Adventure everywhere:** When Dungeons Arise, IDAS, Dungeons and Taverns, Moog's structures, Towns and Towers, Repurposed Structures, Incendium, Nullscape, YUNG's, Born in Chaos, Aquamirae, Illager Invasion, Friends and Foes, Artifacts.
- **Cooking and farming:** Farmer's Delight with Expanded, Rustic, Ocean's, Nether's and End's Delight, Brewin' and Chewin', Vinery, Bountiful Fares, Cooking for Blockheads, and Create Central Kitchen / Slice and Dice to automate it.
- **Three worlds only:** Overworld, Nether, End. No extra dimensions to split the server.
- **Late joiners catch up.** Loot is per player (Lootr), boss credit is shared, and server-wide gates move the story forward for everyone.

See [DESIGN.md](DESIGN.md) for the full design.

## Status — v0.3

| | |
|---|---|
| ✅ **Act I — The Land** | Phase 1 Arrival · Phase 2 Ruins · Phase 3 The Deep (Ferrous Wroughtnaut) |
| ✅ **Act II — The Frontier** | Phase 4 Far Lands (beat 2 of 4: Frostmaw, Umvuthi, Maledictus, Ancient Remnant) · Phase 5 The Sea (Leviathan) · Phase 6 The Forge (Harbinger) |
| ✅ **Act III — The Nether** | Phase 7 The Fire (Netherite Monstrosity + Ignis). Opens when the Harbinger first falls. |
| ✅ **Act IV — The End: New World** | Phase 8 One Way (Ender Guardian). Opens when Ignis first falls. The portal drops you on a far outer island and there is no way home. |
| ✅ **Act V — The End: The Way Back** | Phase 9 The Way Back (build and wake the Return Gate) · Phase 10 The Dragon (wings fail near its island; build an airship) |
| ✅ **Side quests** | Biome and dungeon discoveries, Kitchen & Farm, Create Workshop, Arcane Studies, Treasure & Monsters, Life & Travel. All optional. |
| 🔜 Later | The Dragon's Echo: End raids and dragon pacts after the dragon is dead. |

## Playing (Prism Launcher)

1. Install [Prism Launcher](https://prismlauncher.org/).
2. Download **UltimatePack-client.zip** from the [latest release](https://github.com/Dim4312/ultimate-pack/releases/latest). All mods are already inside.
3. In Prism, **Add Instance → Import** and pick the zip, or paste this URL:
   `https://github.com/Dim4312/ultimate-pack/releases/latest/download/UltimatePack-client.zip`
4. Launch. Every launch checks this repo and downloads only what changed.

The instance uses 6 GB of RAM by default. Change it in *Edit → Settings → Java*. Prism downloads Java 21 for you if you don't have it.

If the game stutters, open *Options → Video Settings*. Lower the render distance, or open the Distant Horizons button and turn off rendering. Distant Horizons is the heaviest mod in the pack.

## Hosting the server

You need Java 21 and about 6 GB of RAM for the server.

Download **UltimatePack-server.zip** from the [latest release](https://github.com/Dim4312/ultimate-pack/releases/latest) and unzip it into an empty folder. It already contains all server mods, configs and scripts.

```bash
cd ultimate-server
echo eula=true > eula.txt      # you accept https://aka.ms/MinecraftEULA
./start.sh                      # Linux/macOS. MEMORY=8G ./start.sh for more RAM
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

## Systems in short

- **Tempering:** completing the Phase N Trial teaches *Tempering N*. Craft a *Tempering Kit N* and hold it in one hand with any melee weapon or staff in the other, then right-click. Each level gives +12% damage and +6% spell power (max X ≈ 2.2×). That is the whole power curve.
- **Boss Echoes:** craft one from an echo shard and themed blocks, then right-click it where that boss lives (Overworld, Nether or End) to call it. The Leviathan only answers in water. A Harbinger Echo used on a dormant Harbinger wakes it.
- **Spawn-safe zone:** Phase 4+ bosses never appear within 1000 blocks of spawn. Echo-called bosses are exempt.
- **Boss scaling:** with N players within 48 blocks, a boss takes `1 / (1 + 0.65·(N−1))` damage.
- **The End is one-way:** the stronghold portal throws you onto an outer island (the same one for everyone) and nothing takes you back, except death. Someone who beat the Ender Guardian wakes a craftable Return Gate. After that the gate takes anyone home, and the portal brings anyone to the gate. Elytra don't work within 1000 blocks of the dragon's island until the dragon is dead.
- **Overworld Blaze Burner:** the Nether is sealed through Act II, so Create's Blaze Burner can be crafted from magma blocks, a lava bucket and a coal block instead.

## Developing

The pack is managed with [packwiz](https://packwiz.infra.link/).

```bash
packwiz modrinth add <mod>     # add a mod
python3 tools/gen_quests.py    # regenerate the quest book from code
python3 tools/gen_textures.py  # regenerate item textures
packwiz refresh                # always run before committing
git tag v0.x.0 && git push --tags   # GitHub builds UltimatePack-client.zip + UltimatePack-server.zip into the release
```

The quest book is generated from `tools/gen_quests.py`, so edit that file instead of the SNBT. Gameplay logic lives in `kubejs/` (Tempering, bosses, gates, recipes). Every push boots a real server in GitHub Actions (`.github/workflows/server-test.yml`) and fails on crashes or KubeJS errors.

## Credits & license

Pack files (scripts, quests, configs, textures, tools) are MIT-licensed. Every mod is downloaded from Modrinth or CurseForge by its authors' official files and keeps its own license. Nothing is redistributed here.
