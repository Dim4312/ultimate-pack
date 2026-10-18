// CI-only KubeJS script. Copy into a disposable server's kubejs/server_scripts/.
// Samples the generator's undecorated surface on a fixed 4 km grid without
// generating chunks. This measures terrain shape, not feature compatibility.
const SampleTerrainHeightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')

ServerEvents.commandRegistry(event => {
  event.register(event.commands.literal('ultimate_terrain_sample')
    .requires(source => source.hasPermission(2))
    .executes(ctx => {
      const level = ctx.source.server.overworld()
      const source = level.getChunkSource()
      const generator = source.getGenerator()
      const rows = []
      const heights = {}
      let total = 0
      let minimum = 10000
      let maximum = -10000
      for (let x = -2048; x <= 2048; x += 256) {
        for (let z = -2048; z <= 2048; z += 256) {
          let height = generator.getBaseHeight(x, z, SampleTerrainHeightmap.WORLD_SURFACE_WG, level, source.randomState())
          rows.push([x, z, height])
          heights[`${x},${z}`] = height
          total += height
          minimum = Math.min(minimum, height)
          maximum = Math.max(maximum, height)
        }
      }
      let difference = 0
      let pairs = 0
      rows.forEach(row => {
        ;[[256, 0], [0, 256]].forEach(offset => {
          let neighbor = heights[`${row[0] + offset[0]},${row[1] + offset[1]}`]
          if (neighbor !== undefined) {
            difference += Math.abs(row[2] - neighbor)
            pairs++
          }
        })
      })
      console.info('ULTIMATE_TERRAIN_SAMPLE ' + JSON.stringify({
        seed: String(level.getSeed()), spacing: 256, samples: rows.length,
        min: minimum, max: maximum, mean: total / rows.length,
        mean_neighbor_difference: difference / pairs, heights: rows
      }))
      return 1
    }))
})
