// Ultimate Pack — what counts as a weapon for Tempering.
// The JSON tag covers common tags; this adds every sword, axe, trident, mace and staff
// by class, so weapons from any mod work without listing them by hand.

const BuiltInRegistries = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')

const loadClassOrNull = name => {
  try {
    return Java.loadClass(name)
  } catch (e) {
    return null
  }
}

const WEAPON_CLASSES = [
  'net.minecraft.world.item.SwordItem',
  'net.minecraft.world.item.AxeItem',
  'net.minecraft.world.item.TridentItem',
  'net.minecraft.world.item.MaceItem',
  'io.redspace.ironsspellbooks.item.weapons.StaffItem'
].map(loadClassOrNull).filter(cls => cls !== null)

ServerEvents.tags('item', event => {
  BuiltInRegistries.ITEM.keySet().forEach(id => {
    const item = BuiltInRegistries.ITEM.get(id)
    if (WEAPON_CLASSES.some(cls => item instanceof cls)) {
      event.add('ultimate:temperable', String(id))
    }
  })
})

ServerEvents.tags('block', event => {
  event.add('minecraft:mineable/pickaxe', 'ultimate:return_gate')
})
