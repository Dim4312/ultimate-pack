# Ultimate Pack

[![Server boot test](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml/badge.svg)](https://github.com/Dim4312/ultimate-pack/actions/workflows/server-test.yml)

A co-op **combat + magic + Create** modpack for Minecraft **1.21.1 / NeoForge** for a group of about 10 friends on one always-on server.

**One world, play together, create — don't grind.**

- **No classes.** Everyone can use swords *and* spells (Simply Swords, Better Combat, Iron's Spells, Ars Nouveau).
- **Clear direction.** A quest book (FTB Quests) leads you through 10 phases. JEI and Create's Ponder explain the machines.
- **Upgrades = materials + a quest.** There's no drop-rate grind: beat a phase's Trial, craft a Tempering Kit, and upgrade any weapon or staff.
- **Bosses you can beat in an evening.** They have real mechanics (Mowzie's Mobs, L_Ender's Cataclysm) and scale with group size. Everyone nearby gets credit. Echoes let anyone fight a boss again.
- **Three worlds only:** Overworld, Nether, End. No extra dimensions to split the server.
- **Late joiners catch up.** Loot is per player (Lootr), boss credit is shared, and server-wide gates move the story forward for everyone.

See [DESIGN.md](DESIGN.md) for the full design.

## Status — v0.1

| | |
|---|---|
| ✅ **Act I — The Land** | Phase 1 Arrival · Phase 2 Ruins · Phase 3 The Deep (Ferrous Wroughtnaut) |
| ✅ **Act II — The Frontier** | Phase 4 Far Lands (beat 2 of 4: Frostmaw, Umvuthi, Maledictus, Ancient Remnant) · Phase 5 The Sea (Leviathan) · Phase 6 The Forge (Harbinger) |
| 🔒 Act III — The Nether | Sealed. The first Harbinger kill opens it for everyone. Quests for it are not written yet. |
| 🔒 Acts IV–V — The End | Sealed. Coming later: one-way arrival, the Return Gate, a cut-off dragon island. |

## Playing (Prism Launcher)

1. Install [Prism Launcher](https://prismlauncher.org/).
2. **Add Instance → Import**, then paste this URL:
   `https://github.com/Dim4312/ultimate-pack/releases/latest/download/UltimatePack-prism.zip`
3. Launch. On the first launch a small window downloads all mods (this takes a minute). Later launches update the pack automatically.

The instance uses 6 GB of RAM by default. Change it in *Edit → Settings → Java*. Prism downloads Java 21 for you if you don't have it.

## Hosting the server

You need Java 21 and about 6 GB of RAM for the server.

```bash
mkdir ultimate-server && cd ultimate-server
curl -fsSLO https://raw.githubusercontent.com/Dim4312/ultimate-pack/main/server/start.sh
chmod +x start.sh
echo eula=true > eula.txt      # you accept https://aka.ms/MinecraftEULA
./start.sh                      # MEMORY=8G ./start.sh for more RAM
```

On the first run, `start.sh` installs NeoForge 21.1.262 and writes sensible `server.properties`: `allow-flight=true` (so Create contraptions don't kick players) and `spawn-protection=0`. On **every** run it syncs server-side mods, configs and scripts from this repo. Client-only mods such as Sodium are skipped.

If your host runs a panel such as Pterodactyl and can't run scripts, install NeoForge 21.1.262 with the panel. Then add `java -jar packwiz-installer-bootstrap.jar -g -s server https://raw.githubusercontent.com/Dim4312/ultimate-pack/main/pack.toml` as a startup step, or run it once over SSH or SFTP.

### Admin commands (op level 2)

| Command | What it does |
|---|---|
| `/ultimate status` | Shows Nether/End gate state and every online player's latest Trial |
| `/ultimate gate nether open\|close` | Opens or seals the Nether manually |
| `/ultimate gate end open\|close` | Opens or seals the End manually |

## Systems in short

- **Tempering:** completing the Phase N Trial teaches *Tempering N*. Craft a *Tempering Kit N* and hold it in one hand with any melee weapon or staff in the other, then right-click. Each level gives +12% damage and +6% spell power (max X ≈ 2.2×). That is the whole power curve.
- **Boss Echoes:** craft one from an echo shard and themed blocks, then right-click it in the Overworld to call that boss. The Leviathan only answers in water. A Harbinger Echo used on a dormant Harbinger wakes it.
- **Boss scaling:** with N players within 48 blocks, a boss takes `1 / (1 + 0.65·(N−1))` damage.
- **Overworld Blaze Burner:** the Nether is sealed through Act II, so Create's Blaze Burner can be crafted from magma blocks, a lava bucket and a coal block instead.

## Developing

The pack is managed with [packwiz](https://packwiz.infra.link/).

```bash
packwiz modrinth add <mod>     # add a mod
python3 tools/gen_quests.py    # regenerate the quest book from code
python3 tools/gen_textures.py  # regenerate item textures
packwiz refresh                # always run before committing
python3 tools/build_prism.py   # build dist/UltimatePack-prism.zip
```

The quest book is generated from `tools/gen_quests.py`, so edit that file instead of the SNBT. Gameplay logic lives in `kubejs/` (Tempering, bosses, gates, recipes). Every push boots a real server in GitHub Actions (`.github/workflows/server-test.yml`) and fails on crashes or KubeJS errors.

## Credits & license

Pack files (scripts, quests, configs, textures, tools) are MIT-licensed. Every mod is downloaded from Modrinth or CurseForge by its authors' official files and keeps its own license. Nothing is redistributed here.
