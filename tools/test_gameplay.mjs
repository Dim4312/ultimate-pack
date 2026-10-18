// Event-level regression checks. Real NeoForge/KubeJS compatibility is checked
// separately by the server boot workflow; these mocks do not emulate Minecraft.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import vm from 'node:vm'
import test from 'node:test'

const root = fileURLToPath(new URL('../', import.meta.url))
const richText = value => ({ value: String(value), append(other) { this.value += other.value; return this } })
const Text = new Proxy({}, { get: () => richText })
const data = () => {
  const values = new Map()
  return {
    getBoolean: key => Boolean(values.get(key)), putBoolean: (key, value) => values.set(key, value),
    getInt: key => values.get(key) || 0, putInt: (key, value) => values.set(key, value)
  }
}
const makePlayer = (name, distance = 0) => ({
  username: name, x: 0, y: 64, z: 0, distance,
  stages: { known: new Set(), has(key) { return this.known.has(key) }, add(key) { this.known.add(key) } },
  isPlayer: () => true, isSpectator: () => false, isCreative: () => false,
  distanceTo() { return this.distance }, tell() {}, setStatusMessage(message) { this.message = message.value },
  getLookAngle: () => ({ x: () => 1, z: () => 0 }),
  getGameProfile() { return { getName: () => this.username } }
})

function harness(script, extra = {}) {
  const events = new Map()
  const register = new Proxy({}, { get: (_, type) => (...args) => events.set(`${type}:${args.length > 1 ? args[0] : ''}`, args.at(-1)) })
  const server = {
    persistentData: data(), commands: [], result: 1, tell() {},
    runCommandSilent(command) { this.commands.push(command); return this.result }
  }
  const context = vm.createContext({
    Text, EntityEvents: register, ItemEvents: register, BlockEvents: register, PlayerEvents: register,
    NativeEvents: { onEvent: (type, callback) => events.set(type, callback) },
    Java: { loadClass: () => ({}) },
    global: { dimensionId: level => level.dimension, isGateOpen: () => true, setGateOpen() {} },
    ...extra
  })
  vm.runInContext(readFileSync(root + script, 'utf8'), context, { filename: script })
  return { events, server, context }
}

function echoEvent(server, dimension = 'minecraft:overworld') {
  const player = makePlayer('Pilot')
  player.level = { dimension }
  player.isInWater = () => true
  return { server, player, item: { count: 1, shrink(n) { this.count -= n } }, cancel() { this.cancelled = true } }
}

test('failed summon keeps the Echo; successful summon consumes one', () => {
  const { events, server } = harness('kubejs/server_scripts/bosses.js')
  const summon = events.get('rightClicked:ultimate:echo_wroughtnaut')
  server.result = 0
  const failed = echoEvent(server)
  summon(failed)
  assert.equal(failed.item.count, 1)
  assert.match(failed.player.message, /kept/)
  server.result = 1
  const success = echoEvent(server)
  summon(success)
  assert.equal(success.item.count, 0)
  assert.match(server.commands[1], /ferrous_wroughtnaut/)
})

test('wrong dimension and dry land keep the Echo', () => {
  const { events, server } = harness('kubejs/server_scripts/bosses.js')
  const wrongDimension = echoEvent(server)
  events.get('rightClicked:ultimate:echo_ignis')(wrongDimension)
  assert.equal(wrongDimension.item.count, 1)
  const dry = echoEvent(server)
  dry.player.isInWater = () => false
  events.get('rightClicked:ultimate:echo_leviathan')(dry)
  assert.equal(dry.item.count, 1)
  assert.equal(server.commands.length, 0)
})

test('an already awake Harbinger does not consume another Echo', () => {
  const { events, server } = harness('kubejs/server_scripts/bosses.js')
  const event = echoEvent(server)
  event.target = { type: 'cataclysm:the_harbinger', nbt: { getBoolean: () => true }, mergeNbt() { assert.fail('already awake') } }
  events.get('entityInteracted:ultimate:echo_harbinger')(event)
  assert.equal(event.item.count, 1)
})

test('dragon credit covers the arena but excludes distant spectators', () => {
  const { events, server } = harness('kubejs/server_scripts/bosses.js')
  const players = [makePlayer('Tower', 150), makePlayer('Distant', 220), makePlayer('Spectator', 20)]
  players[2].isSpectator = () => true
  const entity = { type: 'minecraft:ender_dragon', level: { players }, getDisplayName: () => ({ getString: () => 'Dragon' }) }
  events.get('death:')({ entity, server })
  assert.ok(players[0].stages.has('ultimate_boss_ender_dragon'))
  assert.ok(!players[1].stages.has('ultimate_boss_ender_dragon'))
  assert.ok(!players[2].stages.has('ultimate_boss_ender_dragon'))
  assert.ok(server.persistentData.getBoolean('ultimate_dragon_dead'))
})

test('ranged killer receives credit beyond the normal boss radius', () => {
  const { events, server } = harness('kubejs/server_scripts/bosses.js')
  const archer = makePlayer('Archer', 90)
  const entity = { type: 'mowziesmobs:frostmaw', level: { players: [archer] }, getDisplayName: () => ({ getString: () => 'Frostmaw' }) }
  events.get('death:')({ entity, server, source: { getEntity: () => archer } })
  assert.ok(archer.stages.has('ultimate_boss_frostmaw'))
})

test('boss scaling retains the documented curve', () => {
  const { events } = harness('kubejs/server_scripts/bosses.js')
  const event = { entity: { type: 'cataclysm:ignis', level: { players: [makePlayer('A'), makePlayer('B'), makePlayer('C')] } }, damage: 100,
    setDamage(value) { this.damage = value } }
  events.get('beforeHurt:')(event)
  assert.ok(Math.abs(event.damage - 100 / 2.3) < 0.00001)
})

test('Ars Tempering uses the original casting tool and caps its damage bonus', () => {
  const { events, server } = harness('kubejs/startup_scripts/ars_tempering.js', {
    Java: { loadClass: name => name.endsWith('EnchantmentHelper')
      ? { getItemEnchantmentLevel: (_, tool) => tool.tier }
      : { ENCHANTMENT: 'enchantment', create: (_, id) => id, parse: id => id } }
  })
  server.registryAccess = () => ({ lookupOrThrow: () => ({ getOrThrow: id => id }) })
  const caster = makePlayer('Mage')
  caster.getServer = () => server
  const spell = tier => ({ caster, context: { getCasterTool: () => ({ tier, isEmpty: () => false }) }, damage: 100 })
  const handler = events.get('com.hollingsworth.arsnouveau.api.event.SpellDamageEvent$Pre')
  for (const [tier, damage] of [[0, 100], [1, 106], [10, 160], [20, 160]]) {
    const event = spell(tier)
    handler(event)
    assert.ok(Math.abs(event.damage - damage) < 0.00001)
  }
})

function arrivalHarness(gateBlock, obstruction = false) {
  const h = harness('kubejs/startup_scripts/world_gates.js')
  const { server } = h
  const gate = { x: 1800, y: 70, z: 40 }
  const level = { dimension: 'minecraft:the_end', getBlock: (x, y, z) => ({
    id: y === gate.y ? gateBlock : obstruction ? 'minecraft:stone' : 'minecraft:air',
    getBlockState: () => ({ isAir: () => !obstruction && y !== gate.y })
  }) }
  server.getAllLevels = () => [level]
  server.persistentData.putBoolean('ultimate_end_arrival', true)
  server.persistentData.putInt('ultimate_end_arrival_x', 1500)
  server.persistentData.putInt('ultimate_end_arrival_y', 65)
  h.context.global.setReturnGate(server, gate.x, gate.y, gate.z)
  const player = makePlayer('Traveler')
  player.getServer = () => server
  const event = { getEntity: () => player, getTo: () => ({ location: () => 'minecraft:the_end' }) }
  h.events.get('net.neoforged.neoforge.event.entity.player.PlayerEvent$PlayerChangedDimensionEvent')(event)
  return h
}

test('portal uses the registered gate when it is safe', () => {
  const h = arrivalHarness('ultimate:return_gate')
  assert.match(h.server.commands[0], /1800.5 71 40.5/)
})

test('missing or obstructed gate falls back without resealing the End', () => {
  for (const [block, obstructed] of [['minecraft:air', false], ['ultimate:return_gate', true]]) {
    const h = arrivalHarness(block, obstructed)
    assert.match(h.server.commands[0], /1500.5 65 0.5/)
    assert.ok(h.context.global.returnGate(h.server))
  }
})

function gateHarness({ awake = false, guardian = false, clear = true } = {}) {
  let gate = awake ? { x: 1800, y: 70, z: 40 } : null
  const h = harness('kubejs/server_scripts/the_end.js', { global: {
    dimensionId: level => level.dimension,
    returnGate: () => gate,
    setReturnGate: (_, x, y, z) => { gate = { x, y, z } }
  } })
  const { server } = h
  const level = { dimension: 'minecraft:the_end', getServer: () => server,
    getBlock: () => ({ getBlockState: () => ({ isAir: () => clear }) }) }
  server.overworld = () => ({ getSharedSpawnPos: () => ({ x: 0, z: 0 }), getHeight: () => 70 })
  const player = makePlayer('Traveler')
  player.level = level
  if (guardian) player.stages.add('ultimate_boss_ender_guardian')
  const event = { server, player, level, hand: 'MAIN_HAND', block: { x: 2000, y: 80, z: 60 }, cancel() {} }
  return { ...h, event, getGate: () => gate, click: () => h.events.get('rightClicked:ultimate:return_gate')(event) }
}

test('first gate needs Guardian credit and safe headroom', () => {
  for (const options of [{}, { guardian: true, clear: false }]) {
    const h = gateHarness(options)
    h.click()
    assert.equal(h.getGate(), null)
    assert.ok(!h.event.player.stages.has('ultimate_return_gate'))
  }
})

test('first awakening persists the gate and awards its stage', () => {
  const h = gateHarness({ guardian: true })
  h.click()
  assert.equal(h.getGate().x, 2000)
  assert.ok(h.event.player.stages.has('ultimate_return_gate'))
})

test('a late joiner can use and relocate an already-awake gate', () => {
  const h = gateHarness({ awake: true })
  h.click()
  assert.equal(h.getGate().x, 2000)
  assert.ok(h.event.player.stages.has('ultimate_return_gate'))
  assert.match(h.server.commands[0], /minecraft:overworld run tp Traveler 0.5 70 0.5/)
})
