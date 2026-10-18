// Ars uses its own damage pipeline rather than Iron's spell-power attribute.
// Use the casting tool from the spell context, including delayed projectiles;
// swapping to a stronger weapon after casting must not amplify an old spell.
const ArsRegistries = Java.loadClass('net.minecraft.core.registries.Registries')
const ArsResourceKey = Java.loadClass('net.minecraft.resources.ResourceKey')
const ArsResourceLocation = Java.loadClass('net.minecraft.resources.ResourceLocation')
const ArsEnchantmentHelper = Java.loadClass('net.minecraft.world.item.enchantment.EnchantmentHelper')

NativeEvents.onEvent('com.hollingsworth.arsnouveau.api.event.SpellDamageEvent$Pre', event => {
  const caster = event.caster
  if (!caster || !caster.isPlayer() || !event.context) return
  const server = caster.getServer()
  if (!server) return
  const tool = event.context.getCasterTool()
  if (!tool || tool.isEmpty()) return
  const holder = server.registryAccess().lookupOrThrow(ArsRegistries.ENCHANTMENT)
    .getOrThrow(ArsResourceKey.create(ArsRegistries.ENCHANTMENT, ArsResourceLocation.parse('ultimate:tempered')))
  const tier = ArsEnchantmentHelper.getItemEnchantmentLevel(holder, tool)
  if (tier > 0) event.damage *= 1 + 0.06 * Math.min(tier, 10)
})
