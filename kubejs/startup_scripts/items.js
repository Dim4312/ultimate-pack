// Ultimate Pack — custom items.
// Tempering Kits (one per phase) and Boss Echoes (summon a quest boss again).
// Gameplay logic lives in server_scripts/tempering.js and server_scripts/bosses.js.

const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

// Phases that are released. Raise this when a new act ships.
const TEMPERING_TIERS = 6
global.TEMPERING_TIERS = TEMPERING_TIERS

const BOSS_ECHOES = [
  { id: 'wroughtnaut', name: 'Ferrous Wroughtnaut', hint: 'Only hurts when struck from behind.' },
  { id: 'frostmaw', name: 'Frostmaw', hint: 'Fight it somewhere cold.' },
  { id: 'umvuthi', name: 'Umvuthi', hint: 'The sun-masked chieftain.' },
  { id: 'maledictus', name: 'Maledictus', hint: 'The cursed warrior of the frosted prison.' },
  { id: 'ancient_remnant', name: 'Ancient Remnant', hint: 'The sand king. Use it in a desert.' },
  { id: 'leviathan', name: 'The Leviathan', hint: 'Must be used while standing in water.' },
  { id: 'harbinger', name: 'The Harbinger', hint: 'Use on a dormant Harbinger to wake it.' }
]

StartupEvents.registry('item', event => {
  for (let tier = 1; tier <= TEMPERING_TIERS; tier++) {
    event.create(`ultimate:tempering_kit_${tier}`)
      .displayName(`Tempering Kit ${ROMAN[tier]}`)
      .rarity(tier >= 5 ? 'rare' : tier >= 3 ? 'uncommon' : 'common')
      .maxStackSize(16)
      .tooltip(Text.gray(`Requires: Phase ${tier} Trial completed`))
      .tooltip(Text.darkGray('Hold a weapon or staff in the other hand, then right-click.'))
  }

  BOSS_ECHOES.forEach(boss => {
    event.create(`ultimate:echo_${boss.id}`)
      .displayName(`Echo of ${boss.name}`)
      .rarity('epic')
      .maxStackSize(1)
      .glow(true)
      .tooltip(Text.gray('Right-click to call this boss to you.'))
      .tooltip(Text.darkGray(boss.hint))
  })
})
