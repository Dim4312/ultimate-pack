// Ultimate Pack — bosses.
// - Shared credit: everyone near a quest boss when it dies gets its stage (`ultimate_boss_<id>`).
//   Quests check the stage, so a late joiner who helped a friend counts too.
// - The first Harbinger kill opens the Nether for the whole server.
// - Boss scaling: bosses take less damage when more players are fighting them.
// - Echoes: craftable items that summon a quest boss again.
// - Spawn-safe zone: Phase 4+ bosses that generate near world spawn are removed,
//   so nobody meets Frostmaw on day one. Echo-called bosses are tagged and exempt.

const CREDIT_RADIUS = 64
const SCALING_RADIUS = 48
const SCALING_PER_EXTRA_PLAYER = 0.65
const SPAWN_SAFE_RADIUS = 1000
const ECHO_TAG = 'ultimate_echo'

// entity id -> boss id (stage suffix). Optional bosses give a stage too, for glory quests.
const BOSSES = {
  'mowziesmobs:ferrous_wroughtnaut': 'wroughtnaut',
  'mowziesmobs:frostmaw': 'frostmaw',
  'mowziesmobs:umvuthi': 'umvuthi',
  'mowziesmobs:sculptor': 'sculptor',
  'cataclysm:maledictus': 'maledictus',
  'cataclysm:ancient_remnant': 'ancient_remnant',
  'cataclysm:the_leviathan': 'leviathan',
  'cataclysm:the_harbinger': 'harbinger',
  'cataclysm:scylla': 'scylla',
  'cataclysm:netherite_monstrosity': 'netherite_monstrosity',
  'cataclysm:ignis': 'ignis',
  'cataclysm:ender_guardian': 'ender_guardian',
  'minecraft:wither': 'wither',
  'minecraft:ender_dragon': 'ender_dragon'
}

// echo item id suffix -> how to summon it
const ECHOES = {
  wroughtnaut: { entity: 'mowziesmobs:ferrous_wroughtnaut' },
  frostmaw: { entity: 'mowziesmobs:frostmaw' },
  umvuthi: { entity: 'mowziesmobs:umvuthi' },
  maledictus: { entity: 'cataclysm:maledictus' },
  ancient_remnant: { entity: 'cataclysm:ancient_remnant' },
  leviathan: { entity: 'cataclysm:the_leviathan', needsWater: true },
  harbinger: { entity: 'cataclysm:the_harbinger', nbt: 'Is_Act:1b' }
}

// Bosses of the Far Lands and later: they belong far from spawn.
const FAR_BOSSES = ['frostmaw', 'umvuthi', 'maledictus', 'ancient_remnant', 'leviathan', 'harbinger', 'scylla']

const bossName = entity => entity.getDisplayName().getString()

const playersNear = (entity, radius) => {
  const near = []
  entity.level.players.forEach(player => {
    if (!player.isSpectator() && player.distanceTo(entity) <= radius) near.push(player)
  })
  return near
}

// ---- Shared credit + world gates ----
EntityEvents.death(event => {
  const entity = event.entity
  const id = BOSSES[String(entity.type)]
  if (!id || !event.server) return
  const server = event.server
  const stage = `ultimate_boss_${id}`

  const credited = playersNear(entity, CREDIT_RADIUS)
  credited.forEach(player => {
    if (!player.stages.has(stage)) {
      player.stages.add(stage)
      player.tell(Text.gold(`You helped defeat ${bossName(entity)}!`))
    }
  })
  if (credited.length > 0) {
    server.tell(Text.yellow(`${bossName(entity)} has fallen to `)
      .append(Text.white(credited.map(p => p.username).join(', ')))
      .append(Text.yellow('!')))
  }

  if (id === 'harbinger' && !global.isGateOpen(server, 'minecraft:the_nether')) {
    global.setGateOpen(server, 'minecraft:the_nether', true)
    server.tell(Text.darkRed('The Harbinger is silent. Somewhere deep below, the Nether stirs...'))
    server.tell(Text.gold('The Nether is now open for everyone.'))
    server.runCommandSilent('playsound minecraft:block.end_portal.spawn master @a ~ ~ ~ 1 0.6')
  }
})

// ---- Spawn-safe zone ----
EntityEvents.spawned(event => {
  const entity = event.entity
  const id = BOSSES[String(entity.type)]
  if (!id || FAR_BOSSES.indexOf(id) < 0 || entity.tags.contains(ECHO_TAG)) return
  if (String(entity.level.dimension().location()) !== 'minecraft:overworld') return
  const spawn = entity.level.getSharedSpawnPos()
  const dx = entity.x - spawn.x
  const dz = entity.z - spawn.z
  if (dx * dx + dz * dz < SPAWN_SAFE_RADIUS * SPAWN_SAFE_RADIUS) event.cancel()
})

// ---- Boss scaling ----
// damage x 1 / (1 + 0.65 x (players - 1)): fair for one player, still a fight for five.
EntityEvents.beforeHurt(event => {
  const entity = event.entity
  if (!BOSSES[String(entity.type)]) return
  const players = playersNear(entity, SCALING_RADIUS).length
  if (players <= 1) return
  event.setDamage(event.damage / (1 + SCALING_PER_EXTRA_PLAYER * (players - 1)))
})

// ---- Echoes ----
const summonInFront = (player, server, echo) => {
  const look = player.getLookAngle()
  const x = (player.x + look.x() * 6).toFixed(1)
  const z = (player.z + look.z() * 6).toFixed(1)
  const y = player.y.toFixed(1)
  const nbt = `{Tags:["${ECHO_TAG}"]${echo.nbt ? ',' + echo.nbt : ''}}`
  server.runCommandSilent(`execute in minecraft:overworld run summon ${echo.entity} ${x} ${y} ${z} ${nbt}`)
}

Object.keys(ECHOES).forEach(echoId => {
  const echo = ECHOES[echoId]
  const itemId = `ultimate:echo_${echoId}`

  ItemEvents.rightClicked(itemId, event => {
    const player = event.player
    const server = event.server
    const item = event.item
    if (!server) return
    let message
    if (String(player.level.dimension().location()) !== 'minecraft:overworld') {
      message = Text.red('The echo is silent here. Use it in the Overworld.')
    } else if (echo.needsWater && !player.isInWater()) {
      message = Text.red('The Leviathan only answers from the water. Stand in the sea.')
    } else {
      summonInFront(player, server, echo)
      if (!player.isCreative()) item.shrink(1)
      server.runCommandSilent(`playsound minecraft:entity.warden.emerge hostile @a[distance=..48] ${player.x} ${player.y} ${player.z} 2 0.8`)
      server.tell(Text.lightPurple(`${player.username} called an echo. A boss has answered.`))
      message = Text.lightPurple('Something answers the call...')
    }
    player.setStatusMessage(message)
    event.cancel()
  })
})

// A Harbinger Echo wakes a dormant Harbinger in the Ancient Factory
// (normally that needs a Nether Star, but the Nether is still sealed in Act II).
ItemEvents.entityInteracted('ultimate:echo_harbinger', event => {
  const player = event.player
  const target = event.target
  const item = event.item
  if (!event.server || String(target.type) !== 'cataclysm:the_harbinger') return
  target.mergeNbt({ Is_Act: true })
  if (!player.isCreative()) item.shrink(1)
  player.setStatusMessage(Text.darkRed('The Harbinger awakens.'))
  event.cancel()
})
