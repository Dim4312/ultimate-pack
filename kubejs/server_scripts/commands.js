// Ultimate Pack — admin commands (op level 2).
//   /ultimate status                     world gates + everyone's progress
//   /ultimate gate <nether|end> <open|close>
//   /ultimate arrival                     where the stronghold portal drops players in the End
//   /ultimate returngate reset            put the End back to one-way (the gate must be woken again)

const GATE_NAMES = { nether: 'minecraft:the_nether', end: 'minecraft:the_end' }

const highestTier = player => {
  for (let tier = global.TEMPERING_TIERS; tier >= 1; tier--) {
    if (player.stages.has(`ultimate_tier_${tier}`)) return tier
  }
  return 0
}

ServerEvents.commandRegistry(event => {
  const Commands = event.commands

  let gate = Commands.literal('gate')
  Object.keys(GATE_NAMES).forEach(name => {
    let node = Commands.literal(name)
    ;['open', 'close'].forEach(action => {
      const open = action === 'open'
      node = node.then(Commands.literal(action).executes(ctx => {
        const server = ctx.source.server
        global.setGateOpen(server, GATE_NAMES[name], open)
        server.tell(open ? Text.gold(`The ${name} has been opened.`) : Text.red(`The ${name} has been sealed.`))
        return 1
      }))
    })
    gate = gate.then(node)
  })

  const status = Commands.literal('status').executes(ctx => {
    const source = ctx.source
    const server = source.server
    Object.keys(GATE_NAMES).forEach(name => {
      const open = global.isGateOpen(server, GATE_NAMES[name])
      source.sendSystemMessage(Text.gray(`${name}: `).append(open ? Text.green('open') : Text.red('sealed')))
    })
    const returnGate = global.returnGate(server)
    source.sendSystemMessage(Text.gray('return gate: ').append(returnGate
      ? Text.green(`awake at ${returnGate.x} ${returnGate.y} ${returnGate.z}`) : Text.red('not awake (the End is one-way)')))
    source.sendSystemMessage(Text.gray('ender dragon: ').append(server.persistentData.getBoolean('ultimate_dragon_dead')
      ? Text.green('dead') : Text.red('alive')))
    server.players.forEach(player => {
      source.sendSystemMessage(Text.gray(`${player.username}: `)
        .append(Text.white(`Phase ${highestTier(player)} Trial done`)))
    })
    return 1
  })

  const returnGate = Commands.literal('returngate').then(Commands.literal('reset').executes(ctx => {
    global.clearReturnGate(ctx.source.server)
    ctx.source.server.tell(Text.red('The Return Gate has gone cold. The End is one-way again.'))
    return 1
  }))

  event.register(Commands.literal('ultimate')
    .requires(source => source.hasPermission(2))
    .then(status)
    .then(gate)
    .then(returnGate)
    .then(Commands.literal('arrival').executes(ctx => {
      try {
        const spot = global.endArrival(ctx.source.server)
        ctx.source.sendSystemMessage(Text.gray('End arrival island: ').append(Text.white(`${spot.x} ${spot.y} ${spot.z}`)))
        return 1
      } catch (e) {
        console.error(`ultimate arrival failed: ${e}`)
        ctx.source.sendSystemMessage(Text.red(`Could not find the End arrival island: ${e}`))
        return 0
      }
    })))
})
