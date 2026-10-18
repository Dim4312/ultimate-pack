// Ultimate Pack — the End (Acts IV–V).
// Travel rules and the arrival island live in startup_scripts/world_gates.js.
// - Return Gate: placed in the End, woken by someone who beat the Ender Guardian.
//   Once awake (server-wide, forever) it takes you home, and the stronghold portal leads to it.
// - The dragon's island is cut off: wings (elytra) don't work within 1000 blocks of it
//   until the dragon is dead. Cross the void with an airship.

const Heightmap = Java.loadClass('net.minecraft.world.level.levelgen.Heightmap$Types')
const WINGLESS_RADIUS = 1000
const GATE_STAGE = 'ultimate_return_gate'

const inEnd = entity => String(entity.level.dimension().location()) === 'minecraft:the_end'

const sendHome = (player, server) => {
  const overworld = server.overworld()
  const spawn = overworld.getSharedSpawnPos()
  const y = overworld.getHeight(Heightmap.MOTION_BLOCKING_NO_LEAVES, spawn.x, spawn.z)
  server.runCommandSilent(`execute in minecraft:overworld run tp ${player.username} ${spawn.x + 0.5} ${y} ${spawn.z + 0.5}`)
}

BlockEvents.rightClicked('ultimate:return_gate', event => {
  const player = event.player
  const block = event.block
  const server = event.level.getServer()
  if (!server || String(event.hand) !== 'MAIN_HAND') return
  if (!inEnd(player)) {
    player.setStatusMessage(Text.red('The Return Gate only works in the End.'))
  } else if (!global.returnGate(server)) {
    if (!player.stages.has('ultimate_boss_ender_guardian')) {
      player.setStatusMessage(Text.red('The gate is cold. Only someone who has beaten the Ender Guardian can wake it.'))
    } else {
      global.setReturnGate(server, block.x, block.y, block.z)
      player.stages.add(GATE_STAGE)
      server.tell(Text.lightPurple(`${player.username} woke the Return Gate! `)
        .append(Text.gold('The End is two-way now: the stronghold portal leads to the gate, and the gate leads home.')))
      server.runCommandSilent('playsound minecraft:block.end_portal.spawn master @a ~ ~ ~ 1 1.2')
    }
  } else {
    if (!player.stages.has(GATE_STAGE)) player.stages.add(GATE_STAGE)
    sendHome(player, server)
  }
  event.cancel()
})

PlayerEvents.tick(event => {
  const player = event.player
  if (!player.isFallFlying() || !inEnd(player)) return
  if (player.x * player.x + player.z * player.z > WINGLESS_RADIUS * WINGLESS_RADIUS) return
  if (event.server.persistentData.getBoolean('ultimate_dragon_dead')) return
  player.stopFallFlying()
  player.setStatusMessage(Text.lightPurple('The void winds around the dragon tear at your wings. You need a ship.'))
})
