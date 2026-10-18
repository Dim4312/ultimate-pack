# Ultimate Pack — Design Document

A living document. If the pack and this file disagree, fix one of them.

## Vision

**One world, play together, create — don't grind.**

- No classes. Everyone can swing a sword *and* cast spells. Each step of progression
  gives you a weapon upgrade and a magic upgrade at the same time — you choose where to
  lean, and you can change your mind later. *Something for everyone, everything for everyone.*
- Progress means **new places you can reach and new things you can do**, not bigger numbers.
- Every upgrade is **materials + a completed quest** (go somewhere / beat someone).
  No 1-in-500 drop chances, no 300-hour gear treadmill.
- Bosses are **adventures with mechanics**, not gear checks. A group with sensible gear
  and a plan should win in an evening.
- Everyone stays in **three worlds**: the Overworld, the Nether and the End.
  No extra dimensions that split the server.
- A player who joins late should catch up in about a week, playing *with* everyone else.

## The structure: 5 acts, 10 phases

Each phase ends with a **Trial** quest. Completing it teaches you the next level of
**Tempering** (see Systems). 10 phases → Tempering I–X.

| Act | Phase | What you do | Main threat | Create / travel |
|---|---|---|---|---|
| **I. The Land** | 1. Arrival | Settle in, first machines, first fights, first spells | Normal mobs | Water wheels, andesite machines |
| | 2. Ruins | Surface dungeons, villages, outposts, ruins | Dungeon mobs, pillagers | Brass, automation |
| | 3. The Deep | Caves, mineshafts, ancient cities | **Ferrous Wroughtnaut** | Mechanical drills |
| **II. The Frontier** | 4. Far Lands | Expeditions to distant biomes — **pick 2 of 4** | **Frostmaw / Umvuthi / Maledictus / Ancient Remnant** | Trains, waystone network |
| | 5. The Sea | The sunken city | **The Leviathan** | First airships |
| | 6. The Forge | The ancient factory; beating it opens the Nether for everyone | **The Harbinger** | Advanced contraptions |
| **III. The Nether** | 7. The Fire | Fortresses, bastions, the soul blacksmith | **Netherite Monstrosity**, **Ignis** | Lava and fuel processing |
| **IV. The End — New World** | 8. One Way | Arrive on an outer End island. No way home. | **Ender Guardian** | — |
| **V. The End — The Way Back** | 9. Return Gate | Build a two-way portal home | Puzzle + End cities | Airship across the void |
| | 10. The Dragon | Find a way to the dragon's island | **Ender Dragon** | — |

Optional bosses along the way (no Tempering required, just glory and loot):
the Sculptor (Mowzie's Mobs), Scylla (Cataclysm), dungeon mini-bosses.

### The End in two phases (Acts IV–V, not built yet)

- **Phase 8 — New World.** The stronghold portal is a one-way trip. You land on an outer
  island, not next to the dragon. The dragon is far away and out of reach. Bring
  supplies or settle in. A grave mod keeps your items safe when you die.
- **Phase 9 — How do we get back?** Quests give hints, not answers. The clues are in End
  cities and the Ruined Citadel. Players assemble and activate a **Return Gate**
  (End materials + a key from the Ender Guardian). Once activated it is a permanent
  **two-way portal**: stronghold portal ↔ the End base. This is a **server-wide moment**:
  built once, used by everyone after, including late joiners.
- **Phase 10 — How do we reach the dragon?** The dragon's island is cut off by the void.
  The answer is **an airship built in the End** from End materials. The Create path and
  the combat path end at the same place.

### "The last boss, but not the last" — The Dragon's Echo (not built yet)

1. **The End reaches into the Overworld.** After the dragon dies, End creatures raid
   player bases from time to time. Everything you built gets a new purpose: walls,
   Create turrets, magic wards.
2. **Dragon Pacts.** The dragon can be summoned again. Before each fight players pick
   modifiers ("no elytra", "+2 crystals", "the dragon heals"). More modifiers → better
   trophies and cosmetics, **never more damage**.

## Systems

### Tempering (the upgrade system)

- **Tempering** is a special enchantment (`ultimate:tempered`, levels I–X). Each level gives
  **+12% weapon damage** and **+6% spell power** while the item is in your main hand.
  Tempering X ≈ 2.2× damage. That is the whole power curve. No infinite numbers.
- It works on **any** melee weapon or staff: vanilla, Simply Swords, Iron's Spells weapons
  and staves, Mowzie's and Cataclysm weapons, and so on.
- **How to temper:** craft a **Tempering Kit** of the right tier (normal materials).
  Hold the weapon in one hand and the kit in the other, then right-click.
- **The rule:** you can only use a Tier N kit once you have **completed the Phase N Trial**
  (it teaches you Tempering N). *Materials + a completed quest.*
- Found a cooler weapon? Craft another kit and temper it. Your knowledge doesn't go away,
  so switching weapons only costs materials.
- Tempering is not obtainable from the enchanting table, loot or villagers.

### Shared boss credit

When a quest boss dies, **every player within 64 blocks** gets credit for it, not just the one
who landed the last hit. Late joiners catch up by fighting alongside veterans.

### Boss scaling

Boss damage taken is scaled by the number of players within 48 blocks:
`damage × 1 / (1 + 0.65 × (players − 1))`. A boss is fair for 1 player and still a
fight for 5.

### Boss Echoes (re-fightable bosses)

Every quest boss has a craftable **Echo**. Right-click it to call that boss to you.
Nobody is locked out because "someone already killed it". The Leviathan Echo only works
in water, because the Leviathan can't be hurt on land. Right-clicking a dormant Harbinger
(in the Ancient Factory) with a Harbinger Echo wakes it up. Normally that needs a Nether
Star, but the Nether is still locked during Act II.

### World gates (server-wide)

- **The Nether** is sealed until someone kills **the Harbinger** for the first time (end of
  Act II). Then it opens for the whole server.
- **The End** is sealed until Act IV is released.
- Admins: `/ultimate gate nether open|close`, `/ultimate gate end open|close`, `/ultimate status`.

### Personal progress, shared world

- Each player has their own quest progress (FTB Quests). Friends can form an FTB Teams party
  to share it.
- Loot chests are per player (Lootr), so latecomers still find loot in dungeons.
- World gates are server-wide, so the shared story moves forward together.
- No mob scaling by distance or day, no leveling/stat mods, no infinite enchant stacking.

## What makes people come back

1. An unfinished project they care about: the airship, the town, the rail line.
2. Something unexplored on the map that they saw and haven't reached yet.
3. Friends online: scheduled events such as boss nights, airship races and build contests.
4. Short sessions are worth it. 30 minutes should build or find something.

## Status

- **v0.1 (this release):** Acts I–II (the Overworld, Phases 1–6) are playable.
  The Nether and End are sealed.
- **Next:** Act III (Nether) quests and Tempering VII. Then the custom End mod
  (one-way arrival, Return Gate, cut-off dragon island), then the Dragon's Echo.
