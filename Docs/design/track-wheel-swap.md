---
title: Track wheel swap (few suspension blocks, track wheels shown on demand)
covers:
  - Content/Models/TankWheel*.mwm
  - Content/Data/TankTracks.ini
  - Content/Data/CubeBlocks_RealWheels_Tracks.sbc
  - Content/Data/CubeBlocks_TrackWheelBlocks.sbc
  - Content/Data/BlockVariantGroups.sbc
  - Content/Data/BlockCategories.sbc
---

# Track wheel swap: plan

Branch `wheel-swap`. Status 2026-11-22:
- **Passed in game (owner, 2026-11-22: "everything looks good"):** Part A (all six models at vanilla radius, attach point and collision sphere; the tank styles retuned), and the Lifted Short swaps for all four sizes (Part B step 3, pulled forward so Lifted Short tracks never show off-line tires). Keen's Short Suspension 1x1 shows no swap, as planned (see Part B, "Keen's own suspensions").
- **Models made, not wired up:** the Zantulo swap models `TankWheel1x1_Lifted` and `TankWheel5x5_Lifted`, and the Zantulo static idler models `TankWheelBlock1x1_Lifted` and `TankWheelBlock3x3_Lifted`. They still need their block definitions, icons and track mappings (Part B step 4). Their track styles wait for [gvk-treads.md](gvk-treads.md), which replaces the Morue pack first.

### Part A in-game test (passed 2026-11-22)

Restart the game fully first (collision and attach points only reload on a restart), then load GV Kharak S11 NPC Dev.

1. Build two rovers side by side, one on **Short Track Suspension 3x3** and one on **Lifted Short Suspension 3x3** (3 per side each). Pass: same top speed at the same speed limit, since both use the same collision sphere. Lifted Short stands higher only by its own lift. Repeat with 5x5.
2. Put a track on each (any tank design). Pass: the track sits on the tread with no gap and no sinking, and on the Lifted Short rover the tires show the track wheel.
3. On a Lifted Short Track rover, build a track over 1x1, 2x2 and 3x3 wheels in one row. Pass: all three grooves on one line, and the track runs in them.
4. Do the same on Lifted Short (tires). Pass: the swapped wheels sit exactly where the Track version sits, and removing the track brings back the tires.
5. Add a **Track Wheel Block 3x3** and a 1x1 as idlers in one of those tracks. Pass: same track height as the suspension wheels.
6. Look at an older track built before this change (if the save has one). Pass: still there, on the line.
 Built so far: the 3x3 swap prototype (Lifted Short 3x3, passed in game).

## Goal

- Suspensions show a normal tire until a track is built on them. Building a track swaps the tire's look to the GVK track wheel (Digi's `ReplaceWheelModel`). Removing the track swaps it back.
- That lets most suspension variants leave the G menu.
- **Same size, same physics (owner, 2026-11-21):** no version of a wheel size may ride higher or run faster than another version of the same size.

## How the swap works (Tank Tracks, read in code)

- The swap changes only the picture, on each client. The wheel keeps its own collision.
- Tank Tracks measures each wheel's size before the swap, so the track wraps the tire's size, not the swap model's.
- Tank Tracks' offsets (`SegmentOffset` per track style; `Radius`, `Width`, `OutOffset` per wheel block) move the track. Nothing moves or scales the swap model: it draws exactly where the tire attaches.
- Each suspension picks its own track style for the design the player chose, so a mixed track can swap some wheels and not others.

## Part A: rebuild the four track wheels to vanilla tire specs

One model per size then works on the Track suspensions and as the swap, with no shifted copies and no height fixes.

### A1. Radius

The tread grows outward to the vanilla tire's radius. Width and groove line stay.

| Size | Now | New |
|---|---|---|
| 1x1 | 1.250 | 1.278 |
| 2x2 | 2.494 | 2.553 |
| 3x3 | 3.750 | 3.829 |
| 5x5 | 6.250 | 6.337 |

The static Track Wheel blocks 1x1 and 3x3 get the same growth. `[WheelOverride:Wheel/TankWheelBlock1x1] Radius` goes from 1.3 to 1.278.

### A2. Attach point

Each wheel's `wheel` dummy moves to the vanilla tire's spot. The mesh moves by the same amount inside the model, so on the Short Track and Lifted Short Track suspensions the wheel stays where it is now, on the shared track line.

| Size | Now | New (vanilla) | Change |
|---|---|---|---|
| 1x1 | -2.370 | -1.901 | 0.469 |
| 2x2 | -1.775 | -1.129 | 0.646 |
| 3x3 | -1.718 | -1.711 | 0.007 |
| 5x5 | -3.810 | -4.071 | -0.261 |

### A3. Collision

- A new collision sphere for each wheel at the vanilla tire's radius: 1.1, 2.278, 3.4 and 5.8 m. It's centered under the visible wheel, built in SEUT instead of copied from the old models (`post_export.py` stops copying collision; it still copies the other dummies).
- 1x1 and 2x2 already use these sizes, so they don't change in game.
- 3x3 and 5x5 drop 0.35 / 0.45 m and lose about 9% / 7% of top speed (the speed cap uses the block size, so a smaller sphere covers less ground per turn). They then drive exactly like a Lifted Short on vanilla tires.
- Everything else (grip, power, suspension) comes from the block definitions, and RealWheel and RealTrackWheel are already identical apart from the model.
- Like vanilla tires, the wheels and tracks sit about 0.4 m into flat ground.

### A4. Track styles

- The tank styles (`*_Track`) shift sideways by the attach point change, so built tracks stay on the line. Their X goes from .085 to 0.554 (1x1), .68 to 1.326 (2x2), .75 to 0.757 (3x3) and .79 to 0.529 (5x5).
- Since the sizes now match, a swap style is its tank style plus `ReplaceWheelModel` and `ReplaceWheelModelConstruction` (the BS2 model), with no height fix. The 3x3 prototype's Y of -0.03 goes back to 0.05.

### A5. Export and checks

- SEUT export of Main, LOD1-3 and BS1-3 for each of the six models. Checkpoint the .blend first.
- In mwminfo, each file shows the new radius, the new `wheel` dummy and the sphere size. Then MDK2 build and a check of the deployed copy.
- Restart the game fully: collision and dummy changes don't reload otherwise.

## Part B: roll the swap out

Keen's own suspensions (Suspension, Short, Offroad, Offroad Short, large and small) stay untouched and get no GVK swap styles. The Morue pack already maps them to the same designs, and a second style of the same design on one block breaks the builder.

| Suspension | Sizes | Styles |
|---|---|---|
| Lifted Short | 1x1, 2x2, 3x3, 5x5, both sides | Over-the-tire (no swap) plus the 7 `*_Swap` styles |
| Zantulo Lifted, large | 1x1, 2x2, 3x3, 5x5 | Decision D3 |
| Offroad Lifted, large | 1x1, 2x2, 3x3, 5x5 | Decision D5 |
| Small grid | all | No change: there are no small track wheels |

- 21 new `*_Swap` styles (1x1, 2x2, 5x5, for 7 tank designs; the 3x3 ones exist).
- Offroad tires are a little bigger than vanilla ones, so offroad swap styles need Y = tank Y + (vanilla radius - offroad radius): 2x2 -0.022, 3x3 -0.033, 5x5 -0.042. The OTT pack overrides the offroad 1x1 radius to 1.23, so the offroad 1x1 needs +0.048.
- A checker script runs first: it reads the GVK, OTT and Morue ini files and reports any block with two styles of one design.

### Center groove line (owner, 2026-11-21: "I still want swapped models to all be aligned at their center groove")

Every swapped wheel on one suspension family puts its center groove on one line. Groove distance from the hull face after Part A (suspension attach point + groove distance from the wheel's attach point: 1x1 2.462, 2x2 2.463, 3x3 2.469, 5x5 4.597), and its distance past a 2.5 m grid line:

| Family | 1x1 | 2x2 | 3x3 | 5x5 |
|---|---|---|---|---|
| Lifted Short (and Lifted Short Track) | 5.137 (0.137) | 5.138 (0.138) | 5.144 (0.144) | 10.128 (0.128) |
| Zantulo Lifted and Offroad Lifted, large | 6.401 (1.401) | 7.359 (2.359) | 7.365 (2.365) | 12.474 (2.474) |

- **Lifted Short:** the Part A models line up within 1.6 cm, swapped or not. No extra models.
- **Zantulo and Offroad Lifted:** their 1x1 suspension attaches the wheel 0.96 m nearer the hull, and their 5x5 0.11 m further out, than the 2x2/3x3. So they need their own swap models, used only by their swap styles: `TankWheel1x1_Zantulo` (mesh 0.961 m outward) and `TankWheel5x5_Zantulo` (mesh 0.110 m inward). Each is 5 files (base, BS2, LOD1-3) with no collision, since the swap keeps the tire's collision. Their swap styles' X moves by the same amounts so the track follows. The swapped 1x1 then shows 0.96 m outward of the tire it rides on (decision D10).
- **Between families:** the Lifted Short line sits 0.14 m past a grid line and the Zantulo line 0.14 m short of one, so the 0.28 m gap between the two families stays (decided earlier). One track should use one family.
- **Static idlers:** the two Track Wheel blocks sit on the Lifted Short line, so on a Zantulo or Offroad Lifted track they show 0.28 m off. Matching idlers need two new static blocks (1x1 and 3x3) with the wheel 0.28 m nearer the mounting face. There is room: the inner rubber sits about 1.2 m from the flange. Each is a full model (Main, LOD1-3, BS1-3, convex hull collision), a block definition, an icon and a TankTracks mapping with `OutOffset` -0.14 instead of 0.14 (decision D11).
- **New models in all (owner, 2026-11-21: "two models are fine"):** the 6 existing models are rebuilt (Part A), plus 2 swap-only Zantulo models (1x1, 5x5), plus 2 Zantulo static idlers if D11 is yes.
- Test 2 checks the groove line for every size on each family.

## Part C: hide Short Track and Lifted Short Track

- Remove the 4 variant groups (Short Track and Lifted Short Track, left and right) from `BlockVariantGroups.sbc`.
- Remove the 16 blocks from the GVK, Large Blocks and Propulsion categories in `BlockCategories.sbc`. Without that they show as 16 loose blocks when browsing those categories.
- Never delete the definitions: a block with no definition disappears from grids with no refund. Hidden blocks stay buildable from projections, pastes and search, and keep their toolbar slots.
- Visible GVK suspension families go from 5 to 3.

## Existing grids and the player change note

- Short Track and Lifted Short Track 3x3 and 5x5 vehicles ride 0.35 / 0.45 m lower and run about 9% / 7% slower, the same as Lifted Short on tires.
- Lifted Short tracks (and Zantulo, if D3) show track wheels instead of tires under the track. Saved tracks pick up the new styles on load; no rebuild is needed.
- Built 1x1 and 2x2 tracks on Lifted Short move about 0.47 / 0.65 m outward onto the shared line.
- Short Track and Lifted Short Track leave the G menu; built ones keep working.

## Limits that stay

- Every client and the server need a Tank Tracks build with the swap crash fix before any of this ships. Stock 1.1.5 crashes.
- A destroyed track leaves the other wheels showing the swap until their next model refresh. If a new track is built on them before that, a 5x5 steers around a pivot 0.26 m off, on that client only.
- Swapped wheels leave tire trails (trails follow the wheel block, not the model).
- The Zantulo 1x1 sits about 1 m off the line of the Zantulo 2x2/3x3 (different suspension model).
- Small grid has no track wheels.

## In-game tests

1. A Short Track and a Lifted Short of the same size side by side: same height and top speed, for 3x3 and 5x5.
2. Tracks on each size stay on the line after Part A; mixed 1x1 + 2x2 + 3x3 on Lifted Short sit on one line.
3. The 3x3 swap again with the new models; then 1x1, 2x2 and 5x5 swaps.
4. Static Track Wheel blocks in a mixed track: same track height as the suspension wheels.
5. Offroad tire swaps (if D5), including the offroad 1x1.
6. Weld from a projection (BS2, then the full model), paint and skin, drive fast, grind one wheel, steer after a rebuild.
7. G menu: hidden blocks gone from every category, found by search.
8. A save from before the change loads with all its tracks.
9. Two clients see the same swap.

## Order

1. Part A, with tests 1 to 4.
2. The checker script.
3. Part B for Lifted Short (1x1, 2x2, 5x5), test 3.
4. Part B for Zantulo and Offroad Lifted, after D3, D5 and D10, with their two shifted swap models; tests 2 and 5.
5. Part C, tests 7 and 8.
6. Tests 6 and 9, then the README, the wiki and the player change note. Publish only after the dry run and the owner's "go".

## Open decisions

- **D3. Decided: yes** (owner, 2026-11-21: "two models are fine"). The large Zantulo and Offroad Lifted blocks swap to track wheels; their tracks change look to the GVK tank styles.
- **D5.** Offroad Lifted: their own offroad swap styles with the small height fixes above, or share the vanilla ones and accept a 2 to 5 cm gap?
- **D6.** 7x7: leave it search-only with no tracks, or retire it?
- **D7.** Static Track Wheel blocks: keep as they are, or put the 1x1 and 3x3 in one visible group?
- **D9.** Small grid: no swaps for now, or a hub issue to model small track wheels?
- **D10. Decided: the shifted swap model** (owner, 2026-11-21: "two models are fine"). Was: Zantulo and Offroad Lifted 1x1: a swap model shifted 0.96 m onto the line (it shows away from the tire it rides on), or hide those two 1x1 suspensions instead (owner, 2026-11-21: "I almost want to just delete that one")?
- **D11. Decided: make them** (owner, 2026-11-21: "Yes, make them"). Was: static idlers for the Zantulo line: two new Track Wheel blocks (1x1, 3x3) 0.28 m nearer the hull, or keep one pair and accept a 0.28 m offset on Zantulo tracks?
