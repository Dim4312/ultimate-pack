// Ultimate Pack — Tempering.
// A Tier N kit raises a weapon's Tempering enchantment to level N, but only if the player
// has completed the Phase N Trial (FTB Quests grants the stage `ultimate_tier_N`).
// The enchantment itself is data-driven: kubejs/data/ultimate/enchantment/tempered.json

const Registries = Java.loadClass('net.minecraft.core.registries.Registries')
const ResourceKey = Java.loadClass('net.minecraft.resources.ResourceKey')
const ResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
const EnchantmentHelper = Java.loadClass('net.minecraft.world.item.enchantment.EnchantmentHelper')

const TEMPER_ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
const TEMPERABLE = Ingredient.of('#ultimate:temperable')

const temperingHolder = server => server.registryAccess()
  .lookupOrThrow(Registries.ENCHANTMENT)
  .getOrThrow(ResourceKey.create(Registries.ENCHANTMENT, ResourceLocation.parse('ultimate:tempered')))

// Returns a message for the player; never throws for normal "no" cases.
const tryTemper = (player, server, kitHand, tier) => {
  const kitInMainHand = String(kitHand) === 'MAIN_HAND'
  const kit = kitInMainHand ? player.getMainHandItem() : player.getOffhandItem()
  const weapon = kitInMainHand ? player.getOffhandItem() : player.getMainHandItem()

  if (!player.stages.has(`ultimate_tier_${tier}`)) {
    return Text.red(`You haven't learned Tempering ${TEMPER_ROMAN[tier]} yet. Complete the Phase ${tier} Trial.`)
  }
  if (weapon.isEmpty() || !TEMPERABLE.test(weapon)) {
    return Text.yellow('Hold a melee weapon or a staff in your other hand.')
  }

  const holder = temperingHolder(server)
  const current = EnchantmentHelper.getItemEnchantmentLevel(holder, weapon)
  if (current >= tier) {
    return Text.yellow(`This weapon is already Tempered ${TEMPER_ROMAN[current]}.`)
  }

  weapon.enchant(holder, tier)
  if (!player.isCreative()) kit.shrink(1)
  server.runCommandSilent(`playsound minecraft:block.smithing_table.use player ${player.username} ~ ~ ~ 1 1`)
  return Text.gold(`${weapon.getHoverName().getString()} is now Tempered ${TEMPER_ROMAN[tier]}!`)
}

// A function per tier: Rhino doesn't give loop variables a fresh binding per iteration.
const registerKit = tier => {
  ItemEvents.rightClicked(`ultimate:tempering_kit_${tier}`, event => {
    if (!event.server) return
    event.player.setStatusMessage(tryTemper(event.player, event.server, event.hand, tier))
    event.cancel()
  })
}
for (let tier = 1; tier <= global.TEMPERING_TIERS; tier++) registerKit(tier)

// Tell players what they just learned.
PlayerEvents.stageAdded(event => {
  const match = /^ultimate_tier_(\d+)$/.exec(String(event.stage))
  if (!match) return
  const tier = parseInt(match[1])
  event.player.tell(Text.gold(`You learned Tempering ${TEMPER_ROMAN[tier]}! `)
    .append(Text.gray(`Craft a Tempering Kit ${TEMPER_ROMAN[tier]} and use it on any weapon or staff.`)))
})
