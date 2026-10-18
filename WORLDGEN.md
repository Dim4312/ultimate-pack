# Terrain investigation

The reported symptom was terrain that felt too flat. The existing world was not available,
so the investigation used the pack's pinned jars and fresh worlds with fixed test seeds.

## Findings

- **Tectonic owns Overworld terrain.** It loads a built-in terrain datapack. Nature's Spirit,
  Oh The Biomes We've Gone, Windswept and YUNG's Cave Biomes do not ship a competing
  Overworld noise-settings or dimension replacement in their root data. Tectonic explicitly
  supports biome mods using TerraBlender. This does not prove every worldgen interaction
  in the full pack is compatible, but there is no direct terrain-data overwrite here.
- **The pack had no Tectonic profile.** Its defaults use broad landforms, flat-terrain skew
  `0.1`, vertical scale `1.125` and no elevation boost. The mountain/ridge noise scales
  are both `0.25`. Broad lowlands are consistent with those settings; they do not show
  that the biome mods have disabled mountains.
- **Incendium and Nullscape affect different dimensions.** They replace Nether and End
  generation respectively, and do not replace Tectonic's Overworld terrain.
- **A separate feature-order conflict was already addressed.** An older local server log
  records a cycle involving vanilla plains and Ars Nouveau's Archwood Forest when Nature's
  Spirit's plains override was enabled. The current `natures_spirit-common.toml` already
  disables that override and the vanilla-tree replacement. That crash is distinct from
  the flat-terrain report; those settings remain disabled.

## Terrain change

`config/tectonic.json` now ships an explicit profile:

| Setting | Tectonic default | Pack profile | Purpose |
|---|---:|---:|---|
| Vertical scale | 1.125 | 1.35 | Increase relief above sea level |
| Elevation boost | 0 | 0.1 | Give mountains and plateaus more height |
| Erosion scale | 0.25 | 0.5 | Shorten the distance between changes in mountain terrain |
| Ridge scale | 0.25 | 0.5 | Shorten the distance between ridge/valley changes |
| Flat-terrain skew | 0.1 | -0.15 | Favor raised plateaus over flattened lowlands |

World height remains **-64 to 320**. Continents scale, ocean offset, caves and biome-noise
settings retain their defaults. Ultrasmooth remains off; it has documented issues with
deep oceans and windswept terrain. There are still lower, flatter places to build a town
and rail network.

## Measurements

Four isolated NeoForge 21.1.262 server runs used the pinned Tectonic 3.0.28 and
Lithostitched 1.8.1. Each sampled the generator's undecorated `WORLD_SURFACE_WG` height
at 289 points: X/Z -2048 through 2048, spaced 256 blocks apart. Ocean samples are included.
These are coarse terrain samples, not screenshots, measurements of every block or performance tests.

| Seed | Profile | Surface range | Mean height | Mean difference between adjacent sample points |
|---|---|---:|---:|---:|
| 12345 | Default | 63–294 | 85.8 | 17.8 |
| 12345 | Pack | 63–302 | 95.0 | 28.7 |
| 8675309 | Default | 63–264 | 81.5 | 15.5 |
| 8675309 | Pack | 63–282 | 80.3 | 18.8 |

Both seeds have more local height variation with the pack profile. The second seed's mean
height falls slightly: the objective is varied terrain, not uniformly higher ground.
None of these sample points reached Y318 or higher. This is a limited check against
ceiling clipping, not a guarantee about every mountain in every seed.

A separate test loaded the main biome and dimension stack together: Nature's Spirit,
Oh The Biomes We've Gone, Windswept, YUNG's Cave Biomes, TerraBlender, Incendium,
Nullscape and YUNG's Better End Island, with Tectonic and their dependencies
(19 mod jars including the test tools). For seed 8675309, all 289 sampled surface heights
were identical to the Tectonic-only pack-profile run. Those biome mods did not flatten
the sampled terrain. Three separated Overworld regions each completed generation of
81 chunks without a feature-order failure.

The combined test's Nether task did not finish within four minutes and was stopped;
the End task was not reached. The logs did not establish its cause. That run put too
much pressure on this machine's memory, so no further local server runs will be used.
Full-pack and Nether/End compatibility remain unverified by this local investigation.

To reproduce a height sample, copy `tools/sample_terrain.js` into a disposable test server's
`kubejs/server_scripts/`, start it with a fixed `level-seed` and run
`ultimate_terrain_sample` from the console. The log records a JSON report with all sample
coordinates and heights. Use a separate fresh world and restart for each profile.

## Applying and checking it

Update the pack and restart the server. In multiplayer, the **server's** terrain config
controls generation. For a local single-player world, use that instance's config.

Run **`/ultimate terrain`** as an operator. It reports whether Tectonic's terrain pack is
enabled and displays the effective settings. The pack profile should show vertical scale
`1.35`, elevation boost `0.1`, flat-terrain skew `-0.15` and erosion/ridge scales `0.5/0.5`.

**Existing chunks keep their shape.** Compare a fresh test world or explore beyond all
previously generated and pregenerated chunks. Changing the profile can produce visible
transitions at old/new terrain boundaries.

CI is configured to check the active terrain pack, record a height sample and require completed chunk
generation in three separated Overworld regions, one Nether region and one outer End region.
Feature-order failures and unfinished generation fail the workflow. This replaces the old
spawn-only test, which only warned when generation did not finish.

## Sources

- [Tectonic compatibility](https://modrinth.com/mod/tectonic) and [configuration reference](https://github.com/Apollounknowndev/tectonic/wiki/Config).
- [Tectonic configuration source](https://github.com/Apollounknowndev/tectonic/blob/rewrite-squared/src/common/main/java/dev/worldgen/tectonic/config/ConfigState.java); field names were also checked against the pinned jar and effective settings in a running server.
- [Chunky commands](https://github.com/pop4959/Chunky/wiki/Commands) for the expanded generation smoke test.
