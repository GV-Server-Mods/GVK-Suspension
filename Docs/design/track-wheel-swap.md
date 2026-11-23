---
title: Track wheel swap (few suspension blocks, track wheels shown on demand)
covers:
  - Content/Models/TankWheel*.mwm
  - Content/Data/TankTracks.ini
  - Content/Models/LG_3x3_Lifted_Suspension_ZANTULO.mwm
  - Content/Data/CubeBlocks_Suspension_LiftedVanilla_Regular.sbc
  - Content/Data/CubeBlocks_Suspension_LiftedVanilla_Offroad.sbc
  - Content/Data/CubeBlocks_RealWheels_Tracks.sbc
  - Content/Data/CubeBlocks_TrackWheelBlocks.sbc
  - Content/Data/BlockVariantGroups.sbc
  - Content/Data/BlockCategories.sbc
---

# Track wheel swap: plan

On `main`. Status 2026-11-22:
- **Passed in game (owner, 2026-11-22: "everything looks good"):** Part A (all six models at vanilla radius, attach point and collision sphere; the tank styles retuned), and the Lifted Short swaps for all four sizes (Part B step 3, pulled forward so Lifted Short tracks never show off-line tires). Keen's Short Suspension 1x1 shows no swap, as planned (see Part B, "Keen's own suspensions").
- **Zantulo and Offroad Lifted (built 2026-11-22, not tested in game):** the 2x2/3x3 wheel mount moved to Keen's spot, and all 16 large blocks swap like Keen's suspensions (Part B, "Zantulo on Keen's line").
- **Unused models deleted (2026-11-22):** `TankWheel1x1_Lifted`, `TankWheel5x5_Lifted`, `TankWheelBlock1x1_Lifted` and `TankWheelBlock3x3_Lifted` (made for the old Zantulo line), and `LG_1x1_Lifted_Suspension_ZANTULO*` (the large 1x1 blocks borrow the 2x2/3x3 model): 34 files.

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

Keen's own suspension blocks keep their SBC. Since the Morue pack was replaced ([gvk-treads.md](gvk-treads.md)), TankTracks.ini gives the large ones the Kharak swap styles.

| Suspension | Sizes | Styles |
|---|---|---|
| Lifted Short | 1x1, 2x2, 3x3, 5x5, both sides | Over-the-tire (no swap) plus the Kharak `_Swap` styles |
| Offroad Lifted Short (added 2026-11-22, owner: "just reuse the same suspension base model and pop the offroad wheels on") | 1x1, 2x2, 3x3, 5x5, both sides, large grid | Over-the-tire plus the Kharak `_Swap_Offroad` styles |
| Keen's large suspensions | 1x1, 2x2, 3x3, 5x5 | Kharak `_Swap` (offroad tires: `_Swap_Offroad`) |
| Zantulo Lifted / Offroad Lifted, large | 1x1, 2x2, 3x3, 5x5 | Over-the-tire plus Keen's Kharak styles (`_Swap` / `_Swap_Offroad`) |
| Small grid | all | No change: there are no small track wheels |

- 21 new `*_Swap` styles (1x1, 2x2, 5x5, for 7 tank designs; the 3x3 ones exist).
- Offroad tires are a little bigger than vanilla ones, so offroad swap styles need Y = tank Y + (vanilla radius - offroad radius): 2x2 -0.022, 3x3 -0.033, 5x5 -0.042. The OTT pack overrides the offroad 1x1 radius to 1.23, so the offroad 1x1 needs +0.048.
- A checker script runs first: it reads the GVK, OTT and Morue ini files and reports any block with two styles of one design.

### Center groove line (owner, 2026-11-21: "I still want swapped models to all be aligned at their center groove")

Every swapped wheel on one suspension family puts its center groove on one line. Groove distance from the hull face after Part A (suspension attach point + groove distance from the wheel's attach point: 1x1 2.462, 2x2 2.463, 3x3 2.469, 5x5 4.597), and its distance past a 2.5 m grid line:

| Family | 1x1 | 2x2 | 3x3 | 5x5 |
|---|---|---|---|---|
| Lifted Short (and Lifted Short Track) | 5.137 (0.137) | 5.138 (0.138) | 5.144 (0.144) | 10.128 (0.128) |
| Zantulo Lifted and Offroad Lifted, large (before 2026-11-22) | 6.401 (1.401) | 7.359 (2.359) | 7.365 (2.365) | 12.474 (2.474) |

Wheel mount along the axle (`electric_motor` dummy y, measured in the `.mwm` files):

| Suspension model | 1x1 | 2x2, 3x3 | 5x5 |
|---|---|---|---|
| Keen's regular (`MotorSuspension*.mwm`) | 2.635 | 2.635 | 4.127 |
| Zantulo before 2026-11-22 | 1.439 | 2.396 | 4.127 |
| Zantulo after 2026-11-22 | 2.635 (the 2x2/3x3 model) | 2.635 | 4.127 |

- **Lifted Short:** the Part A models line up within 1.6 cm, swapped or not. No extra models.
- **Keen's line:** Keen's 1x1/2x2/3x3 sit within 0.04 m of the Lifted Short line and the 5x5 0.15 m from it (mod 2.5 m), so Keen's suspensions share the swap models and the Track Wheel idlers.

### Zantulo on Keen's line (built 2026-11-22)

The owner pointed out that the Zantulo suspensions reach out from the hull as far as Keen's regular ones (owner, 2026-11-22: "the zantulo suspension extend out from the vehicle body the same distance as vanilla regular suspension"). Measured, the 5x5 mounts exactly where Keen's does, the 2x2/3x3 0.24 m nearer the hull, and the 1x1 1.2 m nearer. So instead of Zantulo-only models, the 2x2/3x3 mount moved to Keen's spot (owner, 2026-11-22: "Yes, move it"), and Zantulo uses Keen's Kharak styles. This replaces the shifted swap models (D10), the Zantulo idlers (D11) and the plan for separate Zantulo designs.
1. **Wheel mount:** `LG_3x3_Lifted_Suspension_ZANTULO.mwm` (used by every large Lifted and Offroad Lifted size but the 5x5) has its `electric_motor` y moved from 2.396 to 2.635, Keen's value; nothing else in the file changed. Only the main model holds the dummy.
2. **Track styles:** the 16 large Zantulo and Offroad Lifted lines list Digi's over-the-tire style plus `KharakTread_Large_<size>_Swap` and `KharakDoubleTread_Large_<size>_Swap` (Offroad Lifted: `_Swap_Offroad`), the same as Keen's suspensions. The `KharakTread_Large_<size>_Zantulo` styles are gone.
3. **1x1:** Zantulo's 1x1 used the old dedicated 1x1 suspension arm; Keen's 1x1 moved onto the 2x2/3x3 arm years ago (its own file, `MotorSuspension1x1.mwm`, now mounts exactly where `MotorSuspension.mwm` does) (owner, 2026-11-22: "I'd like to borrow the zantulo 2x2/3x3 suspension block and replace the 1x1 model"). The four large Zantulo 1x1 blocks (Lifted and Offroad Lifted, left and right) now use LG_3x3_Lifted_Suspension_ZANTULO and its build stages; their size and offset were already the same. The two Right blocks also had their Left mount point written as a second Right one, so they could not attach by their Left face; fixed. The LG_1x1_Lifted_Suspension_ZANTULO* files are unused on large grid. Small grid (SG_1x1) is unchanged.

What players see:
- Wheels on Zantulo and Offroad Lifted 2x2/3x3 vehicles already built sit 0.24 m further out on each side after a restart. Built 1x1s change to the 2x2/3x3 arm: their wheels sit 1.2 m further out, and the axle drops 0.58 m, so the vehicle rides about 0.58 m higher on them, the same lift as the 2x2/3x3. A saved wheel starts at its old spot and the suspension pulls it over on the first load, so a 1x1 with armor or fenders built close to its old wheel may hit them.
- Kharak tracks on Zantulo blocks show road wheels instead of tires, and every Zantulo size can share a track with Keen's, Lifted Short and Short Track suspensions and the Track Wheel idlers.
- The arm's hub ends 0.10 m past the old mount, so a tire now sits about 0.14 m beyond it. Whether the tire's own hub hides that gap is not checked yet.
- Like every swap, it needs the swap crash fix, in Digi's Workshop Tank Tracks since v1.1.6 (2026-11-22; hub #345).

In-game test (restart the game fully first: the game keeps a model's wheel mount until it closes):
1. A Zantulo Lifted 3x3 next to Keen's Suspension 3x3 on one hull face, same tire. Pass: the tires line up, and the arm's hub meets the tire with no visible gap.
2. A Zantulo Lifted 1x1, Left and Right. Pass: it looks like the 2x2/3x3 arm, its tire lines up with Keen's 1x1, it rides at the 2x2/3x3 lift, and the Right block attaches by every side face.
3. A Kharak Tread over Zantulo 1x1 + 2x2 + 3x3 with a Track Wheel Block 3x3 idler, then the same with Kharak Double Tread. Pass: road wheels instead of tires, every groove and the idler on one line; removing the track brings the tires back.
4. The same on Offroad Lifted. Pass: the tread rests on the tires, no gap and no sinking.
5. An older Zantulo vehicle from the save. Pass: it loads, and its wheels sit on the new spot without jumping or breaking off.

## Part C: hide Short Track and Lifted Short Track

Done 2026-11-22 (owner: "Hide them now"), passed in game (owner, 2026-11-22: "E18 all passes"): the 4 variant groups and the 48 category entries are gone; all 16 definitions stay. The owner still found them by searching the G menu (2026-11-22: "those need to be fully hidden"), so they and the two Short Track Wheel blocks now also have `<Public>false</Public>`. The Track Wheel 1x1 and 3x3 blocks are hidden the same way (owner, 2026-11-22: "Hide it too"; the 3x3 had been the one track block still in the block list), so players can no longer place new static idlers; built ones keep working in their tracks.

The Short Track Wheel 1x1 and 3x3 blocks (`ShortTankWheelBlock1x1/3x3`, deleted 2026-11-21) are back the same way: hidden, with the Track Wheel blocks' models, track line, `[Blocks]` styles and `WheelOverride` values, so built ones keep their place in a track (owner, 2026-11-22: "just for backwards compatibility so player grids aren't missing tracks or suspension").

- Remove the 4 variant groups (Short Track and Lifted Short Track, left and right) from `BlockVariantGroups.sbc`.
- Remove the 16 blocks from the GVK, Large Blocks and Propulsion categories in `BlockCategories.sbc`. Without that they show as 16 loose blocks when browsing those categories.
- Never delete the definitions: a block with no definition disappears from grids with no refund. With `GuiVisible` false a block is out of the menu but the G menu's text search still lists it; `Public` false takes it out of search too (`MyGuiScreenToolbarConfigBase.AddCubeDefinitionsToBlocks`). Built ones stay: the game strips non-public blocks from a grid only under a debug flag that is off (`MyFakes.REMOVE_NON_PUBLIC_BLOCKS`), and the projector does not check `Public`, so projections still weld. Seen in game: built ones stayed after a reload and a projection welded (E18).
- Visible GVK suspension families go from 5 to 3.

## Existing grids and the player change note

- Short Track and Lifted Short Track 3x3 and 5x5 vehicles ride 0.35 / 0.45 m lower and run about 9% / 7% slower, the same as Lifted Short on tires.
- Lifted Short, Keen and Zantulo tracks show track wheels instead of tires under a Kharak track. Saved tracks pick up the new styles on load; no rebuild is needed.
- Built 1x1 and 2x2 tracks on Lifted Short move about 0.47 / 0.65 m outward onto the shared line.
- Short Track and Lifted Short Track leave the G menu; built ones keep working.

## Limits that stay

- Every client and the server need a Tank Tracks build with the swap crash fix before any of this ships. Stock 1.1.5 crashes.
- A destroyed track leaves the other wheels showing the swap until their next model refresh. If a new track is built on them before that, a 5x5 steers around a pivot 0.26 m off, on that client only.
- Swapped wheels leave tire trails (trails follow the wheel block, not the model).
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
4. Part B for Zantulo and Offroad Lifted: their 2x2/3x3 mount moved to Keen's, then Keen's swap styles (built 2026-11-22); tests 2 and 5.
5. Part C, tests 7 and 8.
6. Tests 6 and 9, then the README, the wiki and the player change note. Publish only after the dry run and the owner's "go".

## Open decisions

- **D3. Decided: yes** (owner, 2026-11-21: "two models are fine"). The large Zantulo and Offroad Lifted blocks swap to track wheels; their tracks change look to the GVK tank styles.
- **D5. Done:** offroad tires get their own _Swap_Offroad styles with the offroad drops ([gvk-treads.md](gvk-treads.md)), on Keen's offroad suspensions and Offroad Lifted alike.
- **D6.** 7x7: leave it search-only with no tracks, or retire it?
- **D7.** Static Track Wheel blocks: keep as they are, or put the 1x1 and 3x3 in one visible group?
- **D9.** Small grid: no swaps for now, or a hub issue to model small track wheels?
- **D10. Superseded 2026-11-22** by moving the Zantulo mount (Part B, "Zantulo on Keen's line"); the 1x1 now uses the 2x2/3x3 model. Earlier pick: the shifted swap model (owner, 2026-11-21: "two models are fine"). Was: Zantulo and Offroad Lifted 1x1: a swap model shifted 0.96 m onto the line (it shows away from the tire it rides on), or hide those two 1x1 suspensions instead (owner, 2026-11-21: "I almost want to just delete that one")?
- **D11. Superseded 2026-11-22:** with the mount moved, the normal Track Wheel blocks fit Zantulo tracks. Earlier pick: make them (owner, 2026-11-21: "Yes, make them"). Was: static idlers for the Zantulo line: two new Track Wheel blocks (1x1, 3x3) 0.28 m nearer the hull, or keep one pair and accept a 0.28 m offset on Zantulo tracks?
