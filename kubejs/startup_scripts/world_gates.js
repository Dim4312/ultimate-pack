// Ultimate Pack — server-wide world gates.
// The Nether opens when the Harbinger is first defeated (see server_scripts/bosses.js).
// The End stays sealed until Act IV ships. Admins can override with /ultimate gate.
// Gate state lives in the server's persistent data, so it survives restarts.

const GATES = {
  'minecraft:the_nether': {
    key: 'ultimate_gate_nether',
    sealed: 'The Nether is sealed. Something in the Ancient Factory still holds the key...'
  },
  'minecraft:the_end': {
    key: 'ultimate_gate_end',
    sealed: 'The End is sealed. Its time has not come yet.'
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

// Block travel into a sealed dimension (portals, commands from non-ops, anything).
NativeEvents.onEvent('net.neoforged.neoforge.event.entity.EntityTravelToDimensionEvent', event => {
  const entity = event.getEntity()
  const server = entity.getServer()
  if (!server) return
  const target = String(event.getDimension().location())
  if (global.isGateOpen(server, target)) return
  event.setCanceled(true)
  if (entity.isPlayer()) {
    entity.setStatusMessage(Text.red(GATES[target].sealed))
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
