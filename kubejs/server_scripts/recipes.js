// Ultimate Pack — recipes for Tempering Kits and Boss Echoes.
// Kits use what each phase naturally gives you: Create parts for the builders,
// arcane essence for the casters, and loot from that phase's places for the explorers.

ServerEvents.recipes(event => {
  const kit = tier => `ultimate:tempering_kit_${tier}`

  // Phase 1 — Arrival: first Create parts.
  event.shaped(kit(1), [' I ', 'ACA', ' I '], {
    I: 'minecraft:iron_ingot', A: 'create:andesite_alloy', C: 'minecraft:copper_ingot'
  })
  // Phase 2 — Ruins: brass and the first magic.
  event.shaped(kit(2), [' B ', 'IEI', ' M '], {
    B: 'create:brass_ingot', I: 'minecraft:iron_ingot', E: 'irons_spellbooks:arcane_essence', M: 'minecraft:amethyst_shard'
  })
  // Phase 3 — The Deep: diamonds from the caves.
  event.shaped(kit(3), [' D ', 'BEB', ' D '], {
    D: 'minecraft:diamond', B: 'create:brass_ingot', E: 'irons_spellbooks:arcane_essence'
  })
  // Phase 4 — Far Lands: trade goods and electronics.
  event.shaped(kit(4), [' M ', 'DTD', ' E '], {
    M: 'minecraft:emerald', D: 'minecraft:diamond', T: 'create:electron_tube', E: 'irons_spellbooks:arcane_essence'
  })
  // Phase 5 — The Sea.
  event.shaped(kit(5), ['PDP', 'DED', 'PDP'], {
    P: 'minecraft:prismarine_crystals', D: 'minecraft:diamond', E: 'irons_spellbooks:arcane_essence'
  })
  // Phase 6 — The Forge.
  event.shaped(kit(6), ['DGD', 'MEM', 'DGD'], {
    D: 'minecraft:diamond', G: 'minecraft:gold_block', M: 'create:precision_mechanism', E: 'irons_spellbooks:arcane_essence'
  })

  // The Nether is sealed through Act II, but Create's brass needs a Blaze Burner.
  // Overworld path: magma instead of netherrack, and magma + lava instead of a captured blaze.
  // (Quartz already comes from crushing diorite.)
  event.shaped('create:empty_blaze_burner', [' I ', 'IMI', ' I '], {
    I: '#c:plates/iron', M: 'minecraft:magma_block'
  }).id('ultimate:empty_blaze_burner_from_magma')
  event.shapeless('create:blaze_burner', [
    'create:empty_blaze_burner', 'minecraft:magma_block', 'minecraft:magma_block', 'minecraft:lava_bucket', 'minecraft:coal_block'
  ]).id('ultimate:blaze_burner_overworld')

  // Boss Echoes. Echo shards come from Ancient Cities (Phase 3). No boss drops needed,
  // so anyone can call a boss even if someone else already beat the one in the world.
  const echo = (id, items) => event.shapeless(`ultimate:echo_${id}`, ['minecraft:echo_shard'].concat(items))
  echo('wroughtnaut', ['minecraft:iron_block', 'minecraft:iron_block', 'minecraft:chain'])
  echo('frostmaw', ['minecraft:blue_ice', 'minecraft:blue_ice', 'minecraft:snow_block'])
  echo('umvuthi', ['minecraft:gold_block', 'minecraft:sunflower', 'minecraft:honeycomb'])
  echo('maledictus', ['minecraft:packed_ice', 'minecraft:bone_block', 'minecraft:chain'])
  echo('ancient_remnant', ['minecraft:chiseled_sandstone', 'minecraft:gold_block', 'minecraft:bone_block'])
  echo('leviathan', ['minecraft:heart_of_the_sea', 'minecraft:prismarine_crystals', 'minecraft:prismarine_crystals'])
  echo('harbinger', ['create:precision_mechanism', 'minecraft:redstone_block', 'minecraft:iron_block'])
})
