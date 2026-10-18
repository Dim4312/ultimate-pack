// Ultimate Pack — custom items.
// Tempering Kits (one per phase), Boss Echoes (summon a quest boss again) and the Return Gate.
// Gameplay logic lives in server_scripts/tempering.js, bosses.js and the_end.js.

const ROMAN = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']

// Phases that are released. Raise this when a new act ships.
const TEMPERING_TIERS = 10
global.TEMPERING_TIERS = TEMPERING_TIERS

const BOSS_ECHOES = [
  { id: 'wroughtnaut', name: 'Ferrous Wroughtnaut', hint: 'Only hurts when struck from behind.' },
  { id: 'frostmaw', name: 'Frostmaw', hint: 'Fight it somewhere cold.' },
  { id: 'umvuthi', name: 'Umvuthi', hint: 'The sun-masked chieftain.' },
  { id: 'maledictus', name: 'Maledictus', hint: 'The cursed warrior of the frosted prison.' },
  { id: 'ancient_remnant', name: 'Ancient Remnant', hint: 'The sand king. Use it in a desert.' },
  { id: 'leviathan', name: 'The Leviathan', hint: 'Must be used while standing in water.' },
  { id: 'harbinger', name: 'The Harbinger', hint: 'Use on a dormant Harbinger to wake it.' },
  { id: 'netherite_monstrosity', name: 'the Netherite Monstrosity', hint: 'Only answers in the Nether.' },
  { id: 'ignis', name: 'Ignis', hint: 'Only answers in the Nether.' },
  { id: 'ender_guardian', name: 'the Ender Guardian', hint: 'Only answers in the End.' }
]

StartupEvents.registry('item', event => {
  for (let tier = 1; tier <= TEMPERING_TIERS; tier++) {
    event.create(`ultimate:tempering_kit_${tier}`)
      .displayName(`Tempering Kit ${ROMAN[tier]}`)
      .rarity(tier >= 8 ? 'epic' : tier >= 5 ? 'rare' : tier >= 3 ? 'uncommon' : 'common')
      .maxStackSize(16)
      .tooltip(Text.gray(`Requires: Phase ${tier} Trial completed`))
      .tooltip(Text.darkGray('Hold a weapon, staff or Ars spellbook in the other hand, then right-click.'))
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

StartupEvents.registry('block', event => {
  // Act V: built once in the End, it becomes a two-way door home for everyone.
  event.create('ultimate:return_gate')
    .displayName('Return Gate')
    .hardness(5.0)
    .resistance(1200.0)
    .item(item => item
      .rarity('epic')
      .glow(true)
      .tooltip(Text.gray('Place it in the End. Someone who beat the Ender Guardian must wake it.'))
      .tooltip(Text.darkGray('Once awake: right-click to go home. The stronghold portal leads back here.')))
})
