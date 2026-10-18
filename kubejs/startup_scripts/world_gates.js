// Ultimate Pack — server-wide world gates.
// The Nether opens when the Harbinger is first defeated, the End when Ignis is first defeated
// (see server_scripts/bosses.js). Admins can override with /ultimate gate.
// Gate state lives in the server's persistent data, so it survives restarts.
//
// The End is one-way (Act IV) until someone wakes a Return Gate (Act V, server_scripts/the_end.js):
// - the stronghold portal drops you on an outer island far from the dragon, not on the main island;
// - nothing takes you back to the Overworld (portals, waystones, commands), except dying.
// Once the Return Gate is awake, the stronghold portal leads to the gate and travel home is free.

const GATES = {
  'minecraft:the_nether': {
    key: 'ultimate_gate_nether',
    sealed: 'The Nether is sealed. Something in the Ancient Factory still holds the key...'
  },
  'minecraft:the_end': {
    key: 'ultimate_gate_end',
    sealed: 'The End is sealed. Ignis, in the Burning Arena of the Nether, still guards its fire...'
  }
}

global.isGateOpen = (server, dimension) => {
  const gate = GATES[dimension]
  if (!gate) return true
  return server.persistentData.getBoolean(gate.key)
}

global.setGateOpen = (server, dimension, open) => {
  server.persistentData.putBoolean(GATES[dimension].key, open)
}

global.gateDimensions = () => Object.keys(GATES)

// ---- The Return Gate (server-wide) ----
global.returnGate = server => {
  const data = server.persistentData
  if (!data.getBoolean('ultimate_return_gate')) return null
  return { x: data.getInt('ultimate_return_gate_x'), y: data.getInt('ultimate_return_gate_y'), z: data.getInt('ultimate_return_gate_z') }
}

global.setReturnGate = (server, x, y, z) => {
  const data = server.persistentData
  data.putBoolean('ultimate_return_gate', true)
  data.putInt('ultimate_return_gate_x', x)
  data.putInt('ultimate_return_gate_y', y)
  data.putInt('ultimate_return_gate_z', z)
}

global.clearReturnGate = server => server.persistentData.putBoolean('ultimate_return_gate', false)

const exempt = player => player.isCreative() || player.isSpectator()

// KubeJS turns level.dimension into a property (the dimension id), so level.dimension() is not callable.
global.dimensionId = level => {
  const dim = level.dimension
  return String(typeof dim === 'function' ? level.dimension().location() : dim)
}

// Block travel into a sealed dimension (portals, commands from non-ops, anything),
// and out of the End while it is still one-way.
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.EntityTravelToDimensionEvent', event => {
  const entity = event.getEntity()
  const server = entity.getServer()
  if (!server) return
  const target = String(event.getDimension().location())
  if (!global.isGateOpen(server, target)) {
    event.setCanceled(true)
    if (entity.isPlayer()) entity.setStatusMessage(Text.red(GATES[target].sealed))
    return
  }
  if (global.dimensionId(entity.level) === 'minecraft:the_end' && entity.isPlayer() && !exempt(entity) && !global.returnGate(server)) {
    event.setCanceled(true)
    entity.setStatusMessage(Text.lightPurple('The End holds on to you. There is no way home... yet.'))
  }
})

// ---- Arriving in the End ----
// The arrival island is found once (from the world's terrain noise, so no chunks are generated),
// then saved: everyone lands in the same place and can build a base there together.
const Heightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')
const ARRIVAL_MIN_RADIUS = 1200
const ARRIVAL_MAX_RADIUS = 2400
const PORTAL_ARRIVAL_RADIUS = 300 // the vanilla obsidian platform is at 100 49 0

const surfaceAt = (level, x, z) => {
  const source = level.getChunkSource()
  return source.getGenerator().getBaseHeight(x, z, Heightmap.WORLD_SURFACE_WG, level, source.randomState())
}

// Land at the spot and 12 blocks around it: a real island, not a sliver.
const isIsland = (level, x, z) => {
  for (let dx = -12; dx <= 12; dx += 12) {
    for (let dz = -12; dz <= 12; dz += 12) {
      if (surfaceAt(level, x + dx, z + dz) < 40) return false
    }
  }
  return true
}

const findArrival = level => {
  for (let r = ARRIVAL_MIN_RADIUS; r <= ARRIVAL_MAX_RADIUS; r += 100) {
    for (let deg = 0; deg < 360; deg += 15) {
      let x = Math.round(r * Math.cos(deg * Math.PI / 180))
      let z = Math.round(r * Math.sin(deg * Math.PI / 180))
      if (isIsland(level, x, z)) return { x: x, y: surfaceAt(level, x, z) + 1, z: z }
    }
  }
  // No island found (very unusual terrain): build a small end stone landing.
  for (let dx = -4; dx <= 4; dx++) {
    for (let dz = -4; dz <= 4; dz++) level.getBlock(1500 + dx, 64, dz).set('minecraft:end_stone')
  }
  return { x: 1500, y: 65, z: 0 }
}

const endLevel = server => {
  let found = null
  server.getAllLevels().forEach(level => {
    if (global.dimensionId(level) === 'minecraft:the_end') found = level
  })
  return found
}

global.endArrival = server => {
  const level = endLevel(server)
  const data = server.persistentData
  if (!data.getBoolean('ultimate_end_arrival')) {
    let spot = findArrival(level)
    data.putBoolean('ultimate_end_arrival', true)
    data.putInt('ultimate_end_arrival_x', spot.x)
    data.putInt('ultimate_end_arrival_y', spot.y)
    data.putInt('ultimate_end_arrival_z', spot.z)
  }
  return { x: data.getInt('ultimate_end_arrival_x'), y: data.getInt('ultimate_end_arrival_y'), z: data.getInt('ultimate_end_arrival_z') }
}

NativeEvents.onEvent('net.neoforged.neoforge.event.entity.player.PlayerEvent$PlayerChangedDimensionEvent', event => {
  const player = event.getEntity()
  if (String(event.getTo().location()) !== 'minecraft:the_end' || exempt(player)) return
  // Only portal arrivals (they land near the main island); a waystone trip goes where it was aimed.
  if (player.x * player.x + player.z * player.z > PORTAL_ARRIVAL_RADIUS * PORTAL_ARRIVAL_RADIUS) return
  const server = player.getServer()
  const gate = global.returnGate(server)
  const spot = gate ? { x: gate.x, y: gate.y + 1, z: gate.z } : global.endArrival(server)
  server.runCommandSilent(`execute in minecraft:the_end run tp ${player.getGameProfile().getName()} ${spot.x + 0.5} ${spot.y} ${spot.z + 0.5}`)
  if (!gate) {
    player.tell(Text.lightPurple('The portal throws you far out into the void. The dragon is somewhere far away.'))
    player.tell(Text.gray('There is no way back from here. Settle in, and look for a way home.'))
  }
})

// Stop nether portals from lighting while the Nether is sealed.
NativeEvents.onEvent('net.neoforged.neoforge.event.level.BlockEvent$PortalSpawnEvent', event => {
  const level = event.getLevel()
  const server = level.getServer()
  if (!server || global.isGateOpen(server, 'minecraft:the_nether')) return
  event.setCanceled(true)
  const pos = event.getPos()
  server.getPlayerList().getPlayers().forEach(player => {
    if (player.blockPosition().distSqr(pos) < 16 * 16) {
      player.setStatusMessage(Text.red(GATES['minecraft:the_nether'].sealed))
    }
  })
})
