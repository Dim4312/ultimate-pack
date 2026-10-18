# Pack review — v0.4

The pack's strongest idea is a shared adventure where combat, magic and Create support
the same expeditions. Its main gaps were in connecting those systems and keeping the
story repeatable for a group. Adding another dimension or large technology tree would
work against the existing design, so this update adds one focused content mod and expands
the guidance around the systems already installed.

## Findings and changes

| Finding | Change |
|---|---|
| Boss refights consumed Echo Shards obtained from finite Ancient City chests. A ten-player server needs a reliable supply. | Added a named recipe: two amethyst shards, two copper ingots and one sculk block produce two shards. The existing Deep chapter explains Silk Touch and sculk farming. |
| A failed summon consumed an Echo, and interacting with an already awake Harbinger could consume another. | Consume only on successful summoning or awakening. |
| Phase 9 required every late joiner to craft another Return Gate, despite describing a shared unlock. | The Trial now depends on the chapter introduction and existing gate-use stage. The original crafting route remains available for the first builders. |
| Portal arrivals trusted saved gate coordinates even after the block was removed or covered. | Validate the block and headroom; fall back to the original outer island while keeping travel unlocked. Any player can register a replacement after the first awakening. |
| The airship finale checked a bearing and assembler without teaching a working ship. Its description also implied End materials were sufficient. | Added ten Flight School quests covering hull, lift, propulsion, portable power, controls, loaded testing and the End supply chain. Expanded the packing checklist. Bridges and magic can also complete the main crossing. |
| Tempering improved Iron's spell power, but offered no matching benefit to Ars spell damage or Ars books. | Ars spellbooks are temperable. The Ars spell-damage event applies +6% per tier from the casting tool, capped at X. |
| A 64-block dragon-credit radius could miss players working on towers; ranged finishers could also miss normal boss credit. | The dragon uses 192 blocks. The credited player attacker also receives credit outside the proximity radius. Spectators remain excluded. |
| Dragon's Breath became available in the quest book only after the dragon died. | Moved it alongside the fight. The new postgame chapter explains vanilla dragon resummoning and replenishing breath. |
| Broad item accumulation had little support for a shared warehouse. | Added Storage Drawers and nine storage/logistics quests that connect bulk storage to Create ordering and deliveries. |
| Builders, cooks and hosts had little direction after the boss chain. | Added ten community quests and nine post-dragon quests using existing systems. Build checkmarks explicitly require players to confirm their own work. |
| Sparse Structures used its default factor of 2 for required destinations as well as scenery. | Added factor-1 exceptions for story structures, villages, ancient cities and End cities. Existing chunks are unchanged. |
| Default Iron's spell keys overlapped dodge and voice chat; cosmetic weather was mandatory. | New installs use X for the spell wheel and Z for casting. Particle Rain is optional and off by default. Existing custom bindings are preserved. |
| The generator skipped dependency checks without its resource cache and deleted the live book before validating. | Always validate IDs for uniqueness, dependency existence, cycles and choice counts. Render in a temporary directory before replacing files; `--check` detects stale output. CI runs resource and progression checks before the server boot. |

The book grows from **323 to 362 quests**, across **18 to 22 chapters**. Existing chapter,
quest, task and reward IDs are retained. No existing content mod is removed, so this update
does not intentionally delete placed mod blocks or inventory items from existing worlds.
Back up a live world before applying any pack update.

## Validation and limits

Local checks cover resource IDs from the pinned jars, dependency validity, generated-file
consistency, JavaScript syntax, progression regressions and event behavior with mocked
Minecraft objects. The packwiz index and pack hashes must be refreshed after editing.
The real NeoForge boot and chunk-generation workflow remains the integration check.

The follow-up [terrain investigation](WORLDGEN.md) used an isolated Java 21 runtime and
fresh NeoForge servers to compare fixed-seed terrain profiles. A fresh boot of the entire
pack and a multiplayer playthrough remain unverified locally. The new native Ars event
and Storage Drawers need the full-server check; loaded ship handling, boss balance,
other key conflicts and performance need in-game testing. The optional-boss quests use
the mods' existing encounters; they do not introduce automatic raids or dragon pacts.

## Upstream references

- [Storage Drawers](https://modrinth.com/mod/storagedrawers): pinned NeoForge 1.21.1 release 13.11.4.
- [Sparse Structures source](https://github.com/MaxenceDC/SparseStructures/tree/1.21): configuration was checked against the schema shipped in the pinned 3.0 jar, whose entries use `structure` and `factor`.
- [Ars spell damage event](https://github.com/baileyholl/Ars-Nouveau/blob/1.21.x/src/main/java/com/hollingsworth/arsnouveau/api/event/SpellDamageEvent.java) and [spell context](https://github.com/baileyholl/Ars-Nouveau/blob/1.21.x/src/main/java/com/hollingsworth/arsnouveau/api/spell/SpellContext.java): the damage hook reads the actual casting tool.
