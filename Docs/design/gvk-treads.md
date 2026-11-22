---
title: GVK treads (replace the Morue track pack)
covers:
  - Content/Models/KharakTread*.mwm
  - Content/Models/KharakDoubleTread*.mwm
  - Content/Models/TankWheel*Double*.mwm
  - Content/Data/TankTracks.ini
  - Content/Data/Icons.sbc
---

# GVK treads: plan

Status 2026-11-22: blockout round 2 built from the owner's link concept (`reference/link_concept_owner_2026-11-22.webp`, AI-made, so its layout counts and its exact proportions do not; owner, 2026-11-22: "the proportions may not be exact, that was concept art made by AI"), stretched across the 2.80 m tread at two lengths for the owner to pick: A, 0.49 m plate on a 0.52 m pitch (CV90 size), and B, 0.75 m on a 0.78 m pitch. Traced: outer wedge, upper and lower diagonal pads, small bottom pad, center rib with two slots, three hinge knuckles at the +Y end and three matching notches at the -Y end. Round 1 is kept hidden in the .blend. **Owner picked B for 3x3** (2026-11-22: "on the 3x3 wheel I like how B looks"), and asked for knuckles that protrude further so the links read as interlocked, and for the raised pads extended toward the side edges with even gaps all around them. Round 3: the pad layout is now a set of cells that fill the plate, each inset so every gap between raised parts is 0.04 m and every margin to the plate edge and notches is 0.04 m; the outer wedge and the diagonal pads reach the side edges. Knuckles are 0.17 m barrels standing 0.025 m above the pads, reaching 0.09 m past the plate edge into the next link's notch (pivots at +0.464 and -0.316; Tank Tracks recenters them). Round 4 (owner markup, 2026-11-22: "I don't like these very skinny bits", and the rib slots too close to the top): no pad wraps the side notches any more, so the plate stays plain round them as in the concept, and the two rib slots sit centered between the plate's top edge and the center notch. Round 5 (owner markup: "I want the bridges between the middle rectangles to be thicker and equal"): the rib's three bridges (above, between and below the slots) are each 0.09 m, and the slots are 0.12 m long. Round 6 (owner: bridges "too thick now"; pads closer to the side hinge gaps "so the pad distance around the hinge gap matches the middle one, but no super thin pads"): bridges 0.06 m, slots 0.166 m; the lower pad wraps each side notch at the same 0.04 m margin as the rib round the center notch. To keep every part of it at least 0.08 m wide, the side notches and their knuckles moved 0.06 m inward, and the groove under the upper diagonal pad moved 0.045 m up. Round 7 follows the owner's own pattern markup (2026-11-22: "here is the pattern i want, green are the deboss gaps, red are the hinges (widened on the outer ones)"), per half: a top strip pad in the outer corner, a side strip pad down the outer edge, a large recessed triangle between them and the upper diagonal pad, the upper diagonal pad with its foot down to the corner hinge gap, the lower pad, the small bottom pad, and the center rib unchanged. The side notches became open corner notches 0.386 m wide, and the outer knuckles widen to fill them (0.36 m). Gaps stay 0.04 m. Round 8 (owner: "I want the gaps around those pads to be equal between them and also the edges of the tread"): the plate edge has its own 12 mm bevel, so a 0.04 m edge margin read narrower than a 0.04 m groove between two bevelled pads. Edge and notch margins are now 0.052 m (groove + one bevel), so every gap shows a 0.04 m floor and a 0.064 m opening. The corner strips moved in 12 mm to keep their widths (0.057 and 0.086 m). Round 9 (owner markup: pads "too close to the edges" at the bottom corners, "a little notch that isn't needed", and "simplify how the hinges attach so there aren't so many extra triangles"): the upper diagonal pad's foot now keeps the 0.052 m edge margin above the corner notch (it was 0.02 m), and the split between it and the lower pad moved so the lower pad's outer edge is one straight line. Each knuckle is now one rounded profile merged into the plate: a 0.093 m radius barrel flush with the plate's underside that meets the plate's top edge directly, with no lug block, step or seam. Pivots at +0.456 and -0.324. Main is 750 vertices with bevels. Round 10 (owner, 2026-11-22: "reduce the gaps between the pads and edges by about 25%", and "you have unnecessary bevels underneath the pads"): every gap opening is 0.048 m (was 0.064), a 0.024 m groove floor between pads and a 0.036 m margin to the plate edge and notches, with the groove centerlines unchanged, so the pads grow. Pads and the center rib have no bottom face, so their base meets the plate with a sharp corner and no bevel. The small chamfer at the top corner of each small bottom pad is gone (it was a 9 mm sliver). Main is 670 vertices. The owner also asked for the pads in a different material from the plate; the owner picked `PaintedMetal_VeryDark` for the plate and `RubberScratched` for the pads from four vanilla pairs (`review/materials_r10.png`). Round 11 (owner, 2026-11-22: "I want the pads to be 50% thicker, and the two rectangles at the center should just show the metal treadplate instead of being a dip in the rubber"): pads and rib are 0.075 m thick (top at 0.215 m), and the rib's two slots go through the rubber, so the plate's metal shows at their floor. `track_collider` now covers 0 to 0.215 m. Signed off for detailing (owner, 2026-11-22: "Yes, detail it"); LODs, construction model and export are in [Detailing and LODs](#detailing-and-lods-plan-2026-11-22), and the ini wiring in [TankTracks.ini](#tanktracksini). Files: `Source/KharakTread/KharakTread.blend`, renders in `Source/KharakTread/review/`, reference picture in `Source/KharakTread/reference/`). Blockout r1, modelled at 3x3 size (SegmentScale 1 on 3x3): plate 2.80 x 0.20 m, 0.49 m long on a 0.52 m pitch; two raised pads per link with chamfered corners and a center channel between them; a trapezoid tab on each edge; a guide horn 0.40 wide and 0.44 deep that runs in the wheel's 0.57 m groove; hinge knuckles at the ends; `track_pivot1/2` at +-0.26, `track_collider` over the plate. Owner, 2026-11-22: "I want to do that, i don't want to keep the same names though because I don't want to be accused of stealing or copying. Besides I want to do a track in the style of the original DoK game." Done before the Zantulo wiring in [track-wheel-swap.md](track-wheel-swap.md), so the track styles are written once.

## Goal

- GVK draws every tank track with its own tread model, in the style of the original Deserts of Kharak tracks: wide flat plates with a raised pattern, dark worn metal. All geometry is modelled for GVK; nothing comes from the original game or the Morue pack.
- New design names, so nothing reads as a copy of Morue's.
- The Morue pack (Workshop 3225398014) leaves the mod list.

## What uses Morue today

- **Large grid:** the seven `<family>_Large_<size>_Track` styles inherit Morue's TigerOne, T14, T55MORUE, Abrams, Leopard2, T80 and CV90mk4 styles, and the seven `_Swap` styles inherit those. The Zantulo and Offroad Lifted blocks list the Morue styles directly.
- **Small grid:** the `SG_*` Lifted blocks list 14 Morue small styles (the seven above plus Leclerc, Sherman and five `Plus*`).
- **Keen's suspensions:** Morue maps all 64 of Keen's suspension subtypes to its designs.
- **Stays:** the `LiftedOTT_*` over-the-tire styles inherit Digi's own vanilla pack (Workshop 3209008231, `VanillaOTT_*`), not Morue.

## What happens to tracks already built

A saved track stores its design id. On load, a design that no longer exists makes the track skip loading, and the save keeps it in the block's storage (`TrackHandler.cs:351-358` in Tank Tracks); it would come back only if that design id returned. With new names, every track built on a Morue design disappears and has to be rebuilt. The server is not live, so this hits only test worlds now. Doing it after launch would hit every player's tracks.

## How a design is defined (Tank Tracks)

- `[Design:<Id>]`: `DisplayName` and `Icon` (a transparent material from `Icons.sbc`). This is what the player picks in the track builder, and what a saved track remembers.
- `[Track:<Id>]`: `Design`, `SegmentModel`, `SegmentScale` (X width, Y thickness, Z length), `SegmentOffset` (X lateral, + outward; Y radial, + outward), `SegmentPivotDistance` or pivot empties in the model, `SegmentConstruction`, `SegmentFlip`, `RotatePart`, `GroundCollide`, `DestroyParticle`, `DestroySound`, `ReplaceWheelModel(Construction)`. `Inherit` copies another style (`DefinitionsInternal.cs:168-184`).
- A design is visual only. Grip, speed and collision stay the wheels' own.
- Two styles of the same design on one block break the builder. New GVK design ids never collide with Morue's or Digi's, so this limit no longer blocks Keen's suspensions (decision T3).

## The tread model

- **How Tank Tracks reads a link** (`DefinitionsInternal.cs:272-327`): the first two empties whose names start with `track_pivot` are the hinges; only their Z (Blender Y) counts, and link pitch = pivot gap x `SegmentScale` Z. A `track_collider` empty's box, scaled the same way, is the ground-contact box for the track's terrain raycasts (`GroundCollide`); without it the whole model box is used. Model axes: +Y outward from the wheel, Z along the track, X across it.
- **Reference links** (measured 2026-11-22 from the `.mwm` files; vertex counts [SOFT], read with a quick parser):

  | Link | Model size W x T x L (m) | Pivot gap | Vertices (Main / LODs) |
  |---|---|---|---|
  | Morue CV90mk4 | 0.525 x 0.183 x 0.148 | 0.146 | about 380, no LODs |
  | Morue Abrams | | | about 1,660 / 830 / 180 |
  | Digi vanilla `Segment` | 1.097 x 0.301 x 0.592 | 0.495 | about 3,400 / 1,340 / 690 / 130; construction model with 2 LODs |

  CV90mk4 in game: pitch 0.51 m on 1x1 to 3x3, 1.17 m on 5x5; collider 0.269 x 0.052 x 0.075 in the model.
- **Budget:** Main about 1,500 vertices at most, LOD1 about 700, LOD2 about 300, LOD3 about 130, so a long track stays cheaper than Digi's own vanilla segment.
- **Shape:** a wide flat plate with a raised pattern, guide teeth on the inside running in the wheel groove, and a short hinge at each end. Built to the DoK look in the owner's screenshot (2026-11-22), modelled from scratch.
- **Files:** `KharakTread.mwm` with LOD1-3 and a construction model (`KharakTread_Construction`), both with two `track_pivot` empties at the hinges and one `track_collider` empty over the ground face. No collision and no block definition: Tank Tracks only draws the model.
- **Materials:** vanilla SE materials only, no new textures, none paintable (T2). Plate, hinges and guide horn `PaintedMetal_VeryDark`; raised pads and center rib `RubberScratched` (owner pick, 2026-11-22, from four pairs in `review/materials_r10.png`). Tiling UVs at 0.5 UV per metre.
- **Target size (owner, 2026-11-22: "around the size of the morue cv90 mk4 roughly"):** the Morue CV90mk4 link is 0.525 x 0.183 x 0.148 m in the model (width x thickness x length, read from the `.mwm` bounding box), scaled in game by its styles:

  | Size | CV90mk4 SegmentScale | In game (W x T x L, m) |
  |---|---|---|
  | 1x1 | 5, 3.5, 3.5 | 2.63 x 0.64 x 0.52 |
  | 2x2 | 6.5, 3.5, 3.5 | 3.41 x 0.64 x 0.52 |
  | 3x3 | 7, 3.5, 3.5 | 3.68 x 0.64 x 0.52 |
  | 5x5 | 13, 8, 8 | 6.83 x 1.46 x 1.18 |

  The Kharak Tread aims for about 0.52 m pitch and 0.64 m thickness on 1x1 to 3x3, and about twice that on 5x5. Width follows each GVK wheel's tread, not the CV90's.
- **Sizes:** one link scaled per wheel size through `SegmentScale`, matching each size's tread width. If the 5x5 stretch makes the pattern look wrong, add a wide 5x5 link (decision T5).
- **Icon:** one builder icon per design, added to `Icons.sbc`.

### Detailing and LODs (plan, 2026-11-22)

The blockout was signed off after round 11 (owner, 2026-11-22: "Yes, detail it"). The concept art shows a plain plate, raised pads and hinge knuckles, with wear but no bolts, seams or markings, so detailing finishes what is there rather than adding parts. Main is 670 vertices now, against a 1,500 budget.

| Step | What | Checkpoint |
|---|---|---|
| 1. Shading | Done 2026-11-22. Weighted normals on every part, so the flat plate and pad faces shade flat beside their bevels (the round 11 renders show gradients down the pad sides). Guide horn edges get the same 12 mm bevel as the plate. | Close-up renders |
| 2. UVs | One planar map per part, all running the same way along the track, 0.5 UV per metre; sides by box projection. Checked in EEVEE at 3x3 and at the 5x5 stretch (about 2.1x across). | Renders, both sizes |
| 3. Edge wear | None (DT1). | |
| 4. Decals | None (DT2). | |
| 5. LODs | Built 2026-11-22 from the same build script. LOD1 at 15 m, 358 vertices: plate bevels kept, pads and rib without bevels, knuckles 8 steps round. LOD2 at 30 m, 222: no bevels, knuckles 4 steps. LOD3 at 60 m, 120: knuckles 2 steps, pads and rib as flat tops only, no rib slots. Distances were Digi's vanilla `Segment` (15 / 30 / 60 m, read from its `.mwm`); moved in to 10 / 20 / 40 m (owner, 2026-11-22: "lets do the lod sooner for now"), because the full link costs about 2,240 vertices per metre of track against about 745 for the Morue CV90mk4 link. Trimming the Main model (fewer knuckle sides, no pad bevels) stays an option. | `review/lods_main_1_2_3.png` |
| 6. Construction model | Built 2026-11-22 as its own SEUT scene, `KharakTread_Construction`: the full plate outline, knuckles and guide horn without the pads and rib, so it fills the same outline and only the detail grows. Same pivots and collider (`track_pivot1.c`, `track_pivot2.c`, `track_collider.c`: Tank Tracks matches the start of the name, `DefinitionsInternal.cs:361, 371`). LOD1 at 15 m and LOD2 at 40 m (were 25 / 60 m, as Digi's construction segment; moved in with the Main LODs). | `review/construction_main_1_2.png` |
| 7. Export | Done 2026-11-22 (SEUT I007 for both scenes, no SBC): `Content/Models/KharakTread.mwm` with `_LOD1-3`, and `KharakTread_Construction.mwm` with `_LOD1-2`. Read back from the files: bounding box 2.80 x 0.655 x 0.924 m; `track_pivot1` at Z +0.456 and `track_pivot2` at -0.324 (pitch 0.78 m), both at Y 0.093; `track_collider` box 2.80 x 0.215 x 0.75 m at Y 0.108; LOD distances 15 / 30 / 60 m and 25 / 60 m (re-exported the same day at 10 / 20 / 40 m and 15 / 40 m, read back from the files); materials as planned. Vertices as stored in the files (split at hard edges and UV seams, the same count as the reference table): Main 1,748, LOD1 917, LOD2 573, LOD3 216. That is under Digi's segment at every level except LOD3 (130), and over this doc's first budget (1,500 / 700 / 300 / 130). | Not seen in game |

The TankTracks.ini styles, icon and in-game test follow in [Order](#order).

Decisions for detailing:
- **DT1, edge wear: decided, none** (owner, 2026-11-22, from four options in `review/wear_options_close.png`: none, scratched edges, rusty edges, scratched edges and hinge barrels). The plate stays plain `PaintedMetal_VeryDark`; only the rubber pads look worn.
- **DT2, decals: recommended none.** The art shows none, and every size stretches the link unevenly (5x5 about 2.1x across), which would stretch a decal too.
- **DT3, hinge pins: recommended none.** The art shows plain knuckles. A pin cap on each knuckle end would be new detail the art does not show.

## TankTracks.ini

1. New design `KharakTread_Large`, display name "Kharak Tread" (T1). Large grid only (T4).
2. Full styles per size, with no Morue inheritance: `_Track` (1x1, 2x2, 3x3, 5x5), `_Static` for the track wheel blocks, and `_Swap` (inherit `_Track`, plus `ReplaceWheelModel`).
3. Retune `SegmentOffset` Y for the new link's thickness, so the tread sits on the vanilla-spec wheels from Part A. X keeps the groove line from track-wheel-swap.md.
4. Remap `[Blocks]`: every GVK suspension and track wheel block lists `LiftedOTT_*` (over the tire) plus the GVK designs. Keen's large-grid suspensions get Kharak Tread `_Swap` styles (T3). Small-grid lines drop their Morue styles and keep `LiftedOTT_Small_*` only (T4).
5. Then wire the Zantulo swaps (track-wheel-swap.md, Part B step 4) on the GVK styles.

Done 2026-11-22 (steps 1 to 4; not seen in game). The Morue-based `_Track` and `_Swap` styles are gone, and the ini no longer names a Morue style.

| Style | SegmentScale | SegmentOffset | Why |
|---|---|---|---|
| `KharakTread_Large_1x1_Track`, `_2x2_`, `_3x3_` | 1.03, 1, 1 | .554 / 1.326 / .757, 0, 0 | Link modelled at 3x3 size, and 1x1 to 3x3 share the 3x3 tread width (2.80 m). X 1.03 makes it 2.88 m, about 4 cm past each wheel edge (owner, 2026-11-22: "hang a few cms past the edges of the wheel"; was 1, flush). X is the groove line the old tank styles used after Part A. |
| `KharakTread_Large_5x5_Track` | 2.16, 2.13, 2.13 | .529, 0, 0 | 5.96 m wheel / 2.80 m link, kept in proportion (pitch 1.66 m); X 2.16 makes it 6.05 m, about 4 cm past each edge (was 2.13). |
| `KharakTread_Large_1x1_Static`, `_3x3_Static` | as 1x1 / 3x3 | 0, 0, 0; `AllowOnRotors` | The Track Wheel blocks' `OutOffset` 0.14 already puts the groove on the line. |
| `KharakTread_Large_<size>_Swap` | as `_Track` | as `_Track` | Plus `ReplaceWheelModel` TankWheel<size> and its BS2. |
| `KharakTread_Large_<size>_Swap_Offroad` | as `_Track` | X as `_Track`; Y +0.048 / -0.022 / -0.033 / -0.042 | Offroad tire radius fix (D5 in track-wheel-swap.md), for Keen's Offroad and Offroad Short. |

- **Y is 0:** the link's origin is on the plate's underside, and Tank Tracks puts the middle of each link's chord on the roller radius (`Roller.cs:191-196`), so the plate rests on the tire. The hinge axes sit 0.093 m above the chord (Tank Tracks ignores pivot Y, `DefinitionsInternal.cs:293-305`), so on a curve the knuckles part by about 2 cm on a 3x3 and 6 cm on a 1x1; the in-game test checks it.
- **`[Blocks]`:** Zantulo and Offroad Lifted list `LiftedOTT_*` plus `_Track` until their swap models exist (step 5); Short Track and Lifted Short Track list `_Track`; Lifted Short lists `_Swap`; Keen's 32 large suspensions list only the Kharak swap (Digi's vanilla track stays from his own pack, since block mappings add up across mods, `DefinitionsInternal.cs:34-39`); the Track Wheel blocks list `VanillaOTT_*_Static` plus `_Static`; small grid keeps `LiftedOTT_Small_*` only.
- **Icon:** `Content/Textures/Icons/KharakTread.dds` (256 px BC7 sRGB, as Digi's), rendered from five links on the 3x3 curve (`Source/KharakTread/review/icon_r1.png`); material `KharakTread_Icon` in the new `Content/Data/Icons.sbc`.
- **Build:** MDK2 Release build passed; the deployed `Mods\GVK_Suspension` copy has the new ini, `Icons.sbc`, icon and all seven link models, byte-identical to the repo.

## Order

1. Commit Part A of track-wheel-swap.md. The work sits on branch `wheel-swap`; ask the owner about merging it into `main` first (GVK rule: work on `main`).
2. Reference measurements in Blender (checkpoint first).
3. Model the link, LODs and construction model. Owner reviews renders before export.
4. Export, icon, ini rewrite, MDK2 build, check the deployed copy. Done 2026-11-22.
5. Remove Morue (3225398014) from the NPC Dev test world (`Sandbox.sbc` and `Sandbox_config.sbc`), the S11 config in gvk-server-config and the Workshop collection. NPC Dev world done 2026-11-22: it loaded Morue as the local folder `TankTracks_Morue_Local`, and that `ModItem` is gone from both files (43 mods left; backup taken first). gvk-server-config has no S11 world config yet; only the S10 save lists Morue (3225398014), and that is a past season, so it stays. The Workshop collection is the owner's to change.
6. In-game test (below).
7. Player change note (load elements-of-style): tracks built on the old designs disappear and need rebuilding.
8. Wiki decision page; se-dev-kharak if a current fact changes. No new blocks, so no block owner entries.

## In-game test

First look in game (owner, 2026-11-22): "this new tread looks SO good, and it fits perfectly around the wheels". Covers the look and the fit on the wheel (part of test 1). **Passed in game, all six tests** (owner, 2026-11-22: "all checks pass 1x1 and 5x5 look great, no issues"), including the hinge gap on the 1x1 curve, the 2.13x 5x5 link, the 10 / 20 / 40 m LODs, the construction model and rebuilding a swapped track. The NPC Dev world also loads the local `TankTracks_SwapFix` copy, so the rebuild check says nothing about Digi's Workshop build.

1. Build a track on each GVK suspension size, 1x1 to 5x5. Pass: the tread sits on the tread line, no gap, no sinking, links bend at the hinge with no gaps on the curve.
2. Mixed 1x1/2x2/3x3 track. Pass: one tread width, guide teeth in the grooves.
3. Lifted Short swap with the GVK design. Pass: same as the Part A swap.
4. Drive at speed and turn. Pass: no visible link popping; LODs switch cleanly at distance.
5. Build-stage track (place, then weld). Pass: the construction model shows, then the finished tread.
6. Load the test world without Morue. Pass: no definition errors in the Tank Tracks log; Keen's suspensions still offer Digi's vanilla track.

## Kharak Double Tread (built 2026-11-22, not seen in game)

A second track design that looks like the twin tracks on the larger Deserts of Kharak cruisers: two road wheels bolted side by side under one tread with two bands, just under 5 m across so it fits between blocks (owner, 2026-11-22). It is visual only: every wheel keeps its own tire's collision, grip and radius (owner, 2026-11-22: "I'm ok with it being mostly visual and keeping the original wheel block's collision").

### How it works in Tank Tracks (read in code, v1.1.5)

- New design `KharakDoubleTread_Large`, picked in the track builder like any other. Each wheel then uses its own block's style for that design (`Roller.cs:62-86`), so a wheel looks double only on a track built with this design. The same wheel shows the single tread when the player picks Kharak Tread.
- Every style swaps the wheel model (`ReplaceWheelModel`); the swap keeps the tire's collision (`Roller.cs:123-140`).
- The Track Wheel blocks swap too: on a static wheel the "wheel" is the block itself (`Roller.cs:256-257`), so the double idlers are swap models of the two Track Wheel block models. No new blocks, SBC or block owners.
- The track is drawn with the biggest wheel's style (`Track.cs:285-306`). Every double is the same width, so a mixed 1x1/2x2/3x3 double track looks the same whichever wheel leads.
- Risk: the whole look rides on the wheel swap, so it carries Digi's swap crash (rebuilding a track on swapped wheels; see track-wheel-swap.md). The NPC Dev world loads a patched local Tank Tracks (`TankTracks_SwapFix`); the server needs the same before this ships.

### Size (proposal)

| Part | Width | Notes |
|---|---|---|
| Double wheel | 4.78 m | Two bands of 2.24 m with a 0.30 m spacer between them (round 2) |
| Each band | 2.24 m | The single road wheel scaled 0.80 across, with its own groove (0.45 m) |
| Tread | 4.96 m | 9 cm past each outer wheel edge (round 2; the single hangs 4 cm) |

- **Centered between grid lines:** on the Lifted Short line the groove sits 0.137 m past a grid line, so the double's mesh moves that far toward the hull inside the swap model, and its styles' X moves with it. The wheel then spans exactly two cells.
- **Keen's suspensions:** the 1x1 to 3x3 sit within 0.01 m of that line, so the same models fit. The Keen 5x5 sits 0.13 m off the Lifted Short line, so its 10 m double would be about 0.1 m off the cells.
- **Zantulo and Offroad Lifted:** their line is 0.28 m off. No double styles there until they get their own shifted models, as with their single swaps.

### Models

| Model | Built from | Files |
|---|---|---|
| `TankWheelDouble1x1`, `2x2`, `3x3`, `5x5` (10 m) | Two copies of each road wheel from `abrams_build.py`, scaled to band width, with a spacer between them (scratchpad `double_build.py`; SEUT scenes in `Source/TrackWheels/TrackWheelStudy.blend`) | Main, LOD1-3 at 25 / 50 / 100 m (as the single wheels), BS1 (the bare steel wheel) for construction; no collision (the swap keeps the tire's); the single wheel's dummies copied in |
| `TankWheelBlockDouble1x1`, `3x3` | The double with the Track Wheel block's post and flange; centered 2.5 m out from the flange, so the inner lip sits 7 cm off the block face and the whole wheel stays inside the 1x1x2 / 3x3x2 block | Main, LOD1-3, BS1; no collision (the block keeps its own) |
| `KharakDoubleTread` | Two bands of the Kharak Tread at 0.864 width (2.42 m each), 1.27 m either side of center; same 0.78 m pitch and pivots, one `track_collider` 4.96 m wide over both bands (SEUT scenes in `Source/KharakTread/KharakTread.blend`) | Main and LOD1-3 at 10 / 20 / 40 m; construction model `KharakDoubleTread_Construction` with LOD1-2 at 15 / 40 m |

Detail: each double link level is two copies of the single link one level down, so it costs about what two single links at the next LOD cost: Main from the single LOD1 (716 vertices in Blender), LOD1 from LOD2 (444), LOD2 from LOD3 (240), LOD3 the LOD3 plate and pads only (200). The construction model is two copies of the single construction model at each level. Each double wheel is 6,481 faces at Main, 3,345 / 2,352 / 1,568 at LOD1-3.

The spacer between the two bands is a plain steel channel down to the groove floor, without the groove's bevels or rubber wear strips (owner, 2026-11-22: "doesn't need those extra bevels and the black rubber wear strips in there", then "yeah thats better", `review/double_r3_front.png`). Each band's own groove keeps them.

### TankTracks.ini

- `[Design:KharakDoubleTread_Large]`, display name "Kharak Double Tread", icon `KharakDoubleTread_Icon` (`Content/Textures/Icons/KharakDoubleTread.dds`, 256 px BC7 sRGB, from five double links on the 3x3 curve, `review/icon_double_r1.png`; material in `Icons.sbc`).
- Swap styles only (no plain `_Track`): `KharakDoubleTread_Large_<size>_Swap` and `_Swap_Offroad` (the offroad Y fix) for every size, plus `_1x1_Static` and `_3x3_Static`. Link SegmentScale 1 on 1x1 to 3x3 and 2.01, 2.13, 2.13 on the 5x5 (DD2).
- SegmentOffset X is the single style's X less the mesh's shift toward the hull: .417 / 1.188 / .613 / .401 for 1x1 / 2x2 / 3x3 / 5x5, and -.14 / -.132 on the Track Wheel blocks. That assumes + X is outward, as in Tank Tracks' notes; the in-game test confirms the sign (a wrong sign puts the tread about 0.28 m off the wheels).
- `[Blocks]`: the matching double style added to every line that lists a Kharak Tread style, except Zantulo and Offroad Lifted (58 lines). Short Track and Lifted Short Track get `_Swap` too, so their track wheels swap to the double under a double track.
- Done 2026-11-22: models exported (SEUT I007, every file read back: LOD distances, dummies, materials, bounding boxes), ini written, MDK2 Release build passed, and the deployed `Mods\GVK_Suspension` copy matches the repo (40 files hashed). Not seen in game.

### Order

1. Owner reviews this plan and the decisions below.
2. Build the 3x3 double wheel and a few double links on it in Blender; owner reviews renders. Round 1 built 2026-11-22 (`Source/KharakTread/review/double_r1_*.png`); round 2 narrows the wheel bands (DD1), waiting for the owner's review (`double_r2_three_quarter.png`, `double_r2_front.png`):
   - Wheel `TankWheelDouble3x3_wip` in `Source/TrackWheels/TrackWheelStudy.blend` (scene `Double_wip`), from the scratchpad script `double_build.py` on top of `abrams_build.py`: the inner wheel's hull-side cup with the axle stub, four rubber rings, the spacer with the groove's profile, and the outer wheel's cup and hub with its bolts. The cup lips past the rubber are cut to 0.04 m, so lip to lip it is 4.96 m, the same as the tread. 8,406 vertices in Blender against 5,382 for the single 3x3; LODs not built yet.
   - Link `KharakDoubleTread` in `KharakTread.blend` (scene `KDT_review`): two copies of the single link's LOD1 at 0.864 width (2.42 m each), 0.12 m apart over the spacer, 4.96 m in all; 716 vertices in Blender, about the single link's Main once stored.
   Round 3 (owner, 2026-11-22): the spacer became a plain channel ("yeah thats better").
3. The 1x1, 2x2 and 5x5 doubles and both Track Wheel block doubles. Done 2026-11-22.
4. The double link's LODs and construction model; the icon. Done 2026-11-22.
5. Export, ini, MDK2 build, check the deployed copy. Done 2026-11-22.
6. In-game test. First look (owner, 2026-11-22): "oh man this is good". The six tests above on the double design, plus: the tread sits on both bands (checks the X sign), a mixed 1x1/2x2/3x3 double track, a Track Wheel block idler, Keen's and an offroad suspension, a 10 m 5x5 double, and a fit check between two blocks.

### Decisions

- **DD1, widths: decided** (owner, 2026-11-22: "Yes, 0.20 spacer"): 4.88 m wheel, 0.20 m spacer, 2.34 m bands, 4.96 m tread. Round 2 (owner, 2026-11-22: "I'd like the wheels to be a little narrower so the tread appears to have some more overhang"): bands 2.24 m round the same centers, so each band's horn stays in its groove; the spacer grows to 0.30 m, the wheel is 4.78 m and the tread hangs 9 cm past each outer edge. The 5x5 double follows: 4.64 m bands, 0.50 m spacer, 9.78 m wheel.
- **DD2, 5x5: decided, a 10 m double** (owner, 2026-11-22: "lets keep the 5x5 double wide in play, but its double wide would just be a 10m width instead of a 5m width"). The 5x5 double is the 3x3 double at twice the width: two bands with a spacer (sizes in DD1), 9.96 m tread across four cells. Its link is the double link at SegmentScale 2.01, 2.13, 2.13, so the pads stretch only 6% lengthwise, close to the single 5x5's proportions.
- **DD3, where the doubles sit across the cells: decided, between the grid line at the mount and the line four cells out** (owner, 2026-11-22, marked in `Source/KharakTread/reference/double_5x5_bounds_owner_2026-11-22.webp`: "this is what I want the 5x5 wheel to stay inside"). The 10 m double spans 5 to 15 m from the mounting face, the 5 m doubles 2.5 to 7.5 m, each centered on the single's line less 0.13 m. The inner band covers the part of the mount that pokes past that grid line. Background: The wheel's attach point (its mount on the suspension) is 2.675 m from the mounting face on the 1x1 to 3x3 and 5.531 m on the 5x5 (Lifted Short; groove line minus the groove's distance from the attach point, track-wheel-swap.md). Centered on a grid line, the 5 m double spans 2.5 to 7.5 m and its inner band reaches 0.12 m behind the mount; the 10 m double spans 5 to 15 m and reaches 0.47 m behind it, into the suspension. Shifting the 10 m double out one more cell (7.5 to 17.5 m) clears the mount but puts the track 2.4 m further out than the single 5x5.
- **DD4, the gap between the two wheels: decided, the groove hub** (owner, 2026-11-22: "Yes, same as groove"). The gap shows the same recessed hub as the groove between each wheel's two rubber rings. After the round 2 renders the owner simplified it to a plain channel, without the groove's bevels and wear strips (round 3).

## Open decisions

- **T1, name: decided** (owner, 2026-11-22): "Kharak Tread", ids `KharakTread_Large` / `KharakTread_Small`. One GVK design at first.
- **T2, paint: decided** (owner, 2026-11-22): fixed dark worn metal like the screenshot; the tread never takes the grid's paint. Later the same day the owner asked for the pads in a different material from the plate and picked dark painted metal for the plate with scratched rubber pads.
- **T3, Keen's suspensions: decided** (owner, 2026-11-22: "Yes, add it"): Keen's large-grid suspensions (Suspension, Short, Offroad, Offroad Short, each size and mirror) get Kharak Tread `_Swap` styles in GVK's `[Blocks]`, next to Digi's vanilla track. Their SBC stays untouched. Offroad tires use the offroad Y fix (D5 in track-wheel-swap.md). Keen's small-grid suspensions wait for T4.
- **T4, small grid: decided, later** (owner, 2026-11-22: "lets just do large grid for now, we'll look at doing small grids later because those probably need new track wheel models too"): this plan covers large grid only. `KharakTread_Small` and small-grid track wheels come later, together with D9 in track-wheel-swap.md. Until then, once Morue leaves the mod list, the `SG_*` blocks and Keen's small-grid suspensions offer only Digi's vanilla track (`LiftedOTT_Small_*` / `VanillaOTT_Small`), and small-grid tracks built on Morue designs disappear.
- **T5, 5x5 link:** one link scaled for every size, or a separate wide link for 5x5. Settled by the render review.
