---
title: GVK treads (replace the Morue track pack)
covers:
  - Content/Models/KharakTread*.mwm
  - Content/Models/KharakDoubleTread*.mwm
  - Content/Models/TankWheel*Double*.mwm
  - Content/Models/RubberTrack*.mwm
  - Content/Data/TankTracks.ini
  - Content/Data/Icons.sbc
---

# GVK treads: plan

Status 2026-11-22: the Kharak Tread and the Kharak Double Tread are built and passed in game (GVK_Suspension 2d222d5), and the track wheels are drawn smaller so the tread rests on the ground ([Tread above the ground](#tread-above-the-ground-built-2026-11-22-passed-in-game)). The 1x1 rework for mixed tracks (d07437b) passed in game ([1x1 on mixed tracks](#1x1-on-mixed-tracks-passed-in-game-2026-11-22)). Everything is published (Workshop @98c8131). Later: two more GVK track styles (T6), then small grid (T4). The signed-off link is described in [The tread model](#the-tread-model); its eleven review rounds are in this file's history up to GVK_Suspension 7c11bde.

Lessons from the link reviews, for the next track style:
- Trace the owner's own markup over the concept art. The art was AI-made, so it sets the layout but not the proportions (owner, 2026-11-22: "the proportions may not be exact, that was concept art made by AI").
- Judge the link at the wheel size it will be seen on: on the 3x3 the owner picked a 0.75 m link over a CV90-sized 0.49 m one ("on the 3x3 wheel I like how B looks").
- Measure a gap at its opening, bevels included. The plate edge has its own 12 mm bevel, so an edge margin equal to the groove between two bevelled pads read narrower; the margin is the groove plus one bevel.
- No part under about 0.08 m wide and no chamfer slivers: thin strips round the notches and a 9 mm corner chamfer were rejected ("I don't like these very skinny bits").
- A raised part on a plate has no bottom face, so it meets the plate with a sharp corner; bevels underneath were triangles nobody sees ("you have unnecessary bevels underneath the pads").
- Merge each hinge knuckle into the plate as one rounded profile; lug blocks, steps and seams only added triangles ("simplify how the hinges attach").

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
- **Link as signed off** (round 11, modelled at 3x3 size): plate 2.80 m wide, 0.75 m long on a 0.78 m pitch, pivots `track_pivot1/2` at +0.456 and -0.324 (Tank Tracks recenters them). Raised pads and a center rib 0.075 m thick (top at 0.215 m), per half: a top strip in the outer corner, a side strip down the outer edge, a recessed triangle, an upper diagonal pad, a lower pad and a small bottom pad. Every gap opening is 0.048 m: a 0.024 m groove floor between pads and a 0.036 m margin to the plate edge and notches. The rib's two slots go through the rubber to the plate's metal. Open corner notches 0.386 m wide at the outer hinges and a center notch; each knuckle is a 0.093 m radius barrel flush with the plate's underside. `track_collider` covers 0 to 0.215 m.
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
5. Then wire the Zantulo swaps (track-wheel-swap.md, Part B step 4) on the GVK styles. Done 2026-11-22: Zantulo uses Keen's Kharak styles (track-wheel-swap.md, "Zantulo on Keen's line").

Done 2026-11-22 (steps 1 to 4; not seen in game). The Morue-based `_Track` and `_Swap` styles are gone, and the ini no longer names a Morue style.

| Style | SegmentScale | SegmentOffset | Why |
|---|---|---|---|
| `KharakTread_Large_1x1_Track`, `_2x2_`, `_3x3_` | 1.104, 1, 1 | .554 / 1.326 / .757, 0, 0 | Link modelled at 3x3 size, and 1x1 to 3x3 share the 3x3 tread width (2.80 m of rubber; 3.01 m rim to rim). X 1.104 makes it 3.09 m, about 4 cm past each wheel face (owner, 2026-11-22: "extend past the faces of all track wheels a few cms"; was 1.03, 4 cm past the rubber but 6.5 cm inside the rims). X is the groove line the old tank styles used after Part A. |
| `KharakTread_Large_5x5_Track` | 2.318, 2.13, 2.13 | .529, 0, 0 | 5.96 m wheel / 2.80 m link, kept in proportion (pitch 1.66 m); X 2.318 makes it 6.49 m, about 4 cm past each face of the 6.41 m rim (was 2.16, 6.05 m). |
| `KharakTread_Large_1x1_Static`, `_3x3_Static` | as 1x1 / 3x3 | 0, 0, 0; `AllowOnRotors` | The Track Wheel blocks' `OutOffset` 0.14 already puts the groove on the line. |
| `KharakTread_Large_<size>_Swap` | as `_Track` | as `_Track` | Plus `ReplaceWheelModel` TankWheel<size> and its BS2. |
| `KharakTread_Large_<size>_Swap_Offroad` | as `_Track` | X as `_Track`; Y +0.048 / -0.022 / -0.033 / -0.042 | Offroad tire radius fix (D5 in track-wheel-swap.md), for Keen's Offroad and Offroad Short. |

- **Y is 0:** the link's origin is on the plate's underside, and Tank Tracks puts the middle of each link's chord on the roller radius (`Roller.cs:191-196`), so the plate rests on the tire. The hinge axes sit 0.093 m above the chord (Tank Tracks ignores pivot Y, `DefinitionsInternal.cs:293-305`), so on a curve the knuckles part by about 2 cm on a 3x3 and 6 cm on a 1x1; the in-game test checks it.
- **`[Blocks]`:** Zantulo and Offroad Lifted list `LiftedOTT_*` plus `_Swap` / `_Swap_Offroad`, like Keen's suspensions (step 5); Short Track and Lifted Short Track list `_Track`; Lifted Short lists `_Swap` and Offroad Lifted Short `_Swap_Offroad`; Keen's 32 large suspensions list only the Kharak swap (Digi's vanilla track stays from his own pack, since block mappings add up across mods, `DefinitionsInternal.cs:34-39`); the Track Wheel blocks list `VanillaOTT_*_Static` plus `_Static`; small grid keeps `LiftedOTT_Small_*` only.
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

First look in game (owner, 2026-11-22): "this new tread looks SO good, and it fits perfectly around the wheels". Covers the look and the fit on the wheel (part of test 1). **Passed in game, all six tests** (owner, 2026-11-22: "all checks pass 1x1 and 5x5 look great, no issues"), including the hinge gap on the 1x1 curve, the 2.13x 5x5 link, the 10 / 20 / 40 m LODs, the construction model and rebuilding a swapped track. The NPC Dev world also loads the local `TankTracks_SwapFix` copy. Digi's Workshop v1.1.6 (2026-11-22) ships that fix unchanged (every script matches `TankTracks_SwapFix` except the version string), so the rebuild check holds for the Workshop build.

1. Build a track on each GVK suspension size, 1x1 to 5x5. Pass: the tread sits on the tread line, no gap, no sinking, links bend at the hinge with no gaps on the curve.
2. Mixed 1x1/2x2/3x3 track. Pass: one tread width, guide teeth in the grooves.
3. Lifted Short swap with the GVK design. Pass: same as the Part A swap.
4. Drive at speed and turn. Pass: no visible link popping; LODs switch cleanly at distance.
5. Build-stage track (place, then weld). Pass: the construction model shows, then the finished tread.
6. Load the test world without Morue. Pass: no definition errors in the Tank Tracks log; Keen's suspensions still offer Digi's vanilla track.

## Kharak Double Tread (built 2026-11-22, passed in game)

A second track design that looks like the twin tracks on the larger Deserts of Kharak cruisers: two road wheels bolted side by side under one tread with two bands, just under 5 m across so it fits between blocks (owner, 2026-11-22). It is visual only: every wheel keeps its own tire's collision, grip and radius (owner, 2026-11-22: "I'm ok with it being mostly visual and keeping the original wheel block's collision").

### How it works in Tank Tracks (read in code, v1.1.5)

- New design `KharakDoubleTread_Large`, picked in the track builder like any other. Each wheel then uses its own block's style for that design (`Roller.cs:62-86`), so a wheel looks double only on a track built with this design. The same wheel shows the single tread when the player picks Kharak Tread.
- Every style swaps the wheel model (`ReplaceWheelModel`); the swap keeps the tire's collision (`Roller.cs:123-140`).
- The Track Wheel blocks swap too: on a static wheel the "wheel" is the block itself (`Roller.cs:256-257`), so the double idlers are swap models of the two Track Wheel block models. No new blocks, SBC or block owners.
- The track is drawn with the biggest wheel's style (`Track.cs:285-306`). Every double is the same width, so a mixed 1x1/2x2/3x3 double track looks the same whichever wheel leads.
- Risk: the whole look rides on the wheel swap, so it carries Digi's swap crash (rebuilding a track on swapped wheels; see track-wheel-swap.md). Fixed in Digi's Workshop v1.1.6 (2026-11-22), the same code as the local `TankTracks_SwapFix` the NPC Dev world loads, so the server needs nothing extra.

### Size (proposal)

| Part | Width | Notes |
|---|---|---|
| Double wheel | 4.78 m | Two bands of 2.24 m with a 0.30 m spacer between them (round 2) |
| Each band | 2.24 m | The single road wheel scaled 0.80 across, with its own groove (0.45 m) |
| Tread | 4.856 m | Just inside both rim faces, 4.86 m apart (owner, 2026-11-22: "so they don't extend past the rim face on either side"; was 4.96 m, 5 cm past each rim face). SegmentScale X 0.979 (1.987 on the 5x5, 9.856 m inside 9.86 m) |

- **Centered between grid lines:** on the Lifted Short line the groove sits 0.137 m past a grid line, so the double's mesh moves that far toward the hull inside the swap model, and its styles' X moves with it. The wheel then spans exactly two cells.
- **Keen's suspensions:** the 1x1 to 3x3 sit within 0.01 m of that line, so the same models fit. The Keen 5x5 sits 0.13 m off the Lifted Short line, so its 10 m double would be about 0.1 m off the cells.
- **Zantulo and Offroad Lifted:** since their 2x2/3x3 mount moved to Keen's spot (2026-11-22) they list the same double styles as Keen's suspensions.

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
- Swap styles only (no plain `_Track`): `KharakDoubleTread_Large_<size>_Swap` and `_Swap_Offroad` (the offroad Y fix) for every size, plus `_1x1_Static` and `_3x3_Static`. Link SegmentScale 0.979, 1, 1 on 1x1 to 3x3 and 1.987, 2.13, 2.13 on the 5x5 (DD2; X cut 2026-11-22 so the tread stays inside the rim faces, was 1 and 2.01).
- SegmentOffset X is the single style's X less the mesh's shift toward the hull: .417 / 1.188 / .613 / .401 for 1x1 / 2x2 / 3x3 / 5x5, and -.14 / -.132 on the Track Wheel blocks. That assumes + X is outward, as in Tank Tracks' notes; the in-game test confirms the sign (a wrong sign puts the tread about 0.28 m off the wheels).
- `[Blocks]`: the matching double style added to every line that lists a Kharak Tread style, except Zantulo and Offroad Lifted (58 lines; the 16 Zantulo lines got theirs on 2026-11-22). Short Track and Lifted Short Track get `_Swap` too, so their track wheels swap to the double under a double track.
- Done 2026-11-22: models exported (SEUT I007, every file read back: LOD distances, dummies, materials, bounding boxes), ini written, MDK2 Release build passed, and the deployed `Mods\GVK_Suspension` copy matches the repo (40 files hashed). Not seen in game.
- **Dummies after every wheel export, 2026-11-23** (owner: "they are all flopping around the suspension like their attachment point is in the wrong spot"). `TrackWheelStudy.blend` holds no empties: the eight suspension wheels (`TankWheel*`, `TankWheelDouble*`, Main only) get Keen's dummies copied in after SEUT export, with `wheel` at the vanilla tire's spot (scratchpad `post_export.py`, `post_doubles.py`). The scale-pass export of 2026-11-22 21:20 (`Source/TrackWheels/scale_pass.py`: texture scale, 5x5 bolts) skipped that step, so the wheels had no attach point and swung about the suspension; it showed only after a full game restart, since dummies load once. Fixed by putting the committed dummies back (`wheel` y -1.901 / -1.129 / -1.711 / -4.071 for 1x1 / 2x2 / 3x3 / 5x5, singles and doubles), deployed; fixed in game after a full restart (owner: "they are all fixed now"). Before deploying a re-exported wheel, read its dummies back (se-dev-seut `scripts/mwm_dummies.py`): three each, as committed.

### Order

1. Owner reviews this plan and the decisions below.
2. Build the 3x3 double wheel and a few double links on it in Blender; owner reviews renders. Round 1 built 2026-11-22 (`Source/KharakTread/review/double_r1_*.png`); round 2 narrows the wheel bands (DD1), waiting for the owner's review (`double_r2_three_quarter.png`, `double_r2_front.png`):
   - Wheel `TankWheelDouble3x3_wip` in `Source/TrackWheels/TrackWheelStudy.blend` (scene `Double_wip`), from the scratchpad script `double_build.py` on top of `abrams_build.py`: the inner wheel's hull-side cup with the axle stub, four rubber rings, the spacer with the groove's profile, and the outer wheel's cup and hub with its bolts. The cup lips past the rubber are cut to 0.04 m, so lip to lip it is 4.96 m, the same as the tread. 8,406 vertices in Blender against 5,382 for the single 3x3; LODs not built yet.
   - Link `KharakDoubleTread` in `KharakTread.blend` (scene `KDT_review`): two copies of the single link's LOD1 at 0.864 width (2.42 m each), 0.12 m apart over the spacer, 4.96 m in all; 716 vertices in Blender, about the single link's Main once stored.
   Round 3 (owner, 2026-11-22): the spacer became a plain channel ("yeah thats better").
3. The 1x1, 2x2 and 5x5 doubles and both Track Wheel block doubles. Done 2026-11-22.
4. The double link's LODs and construction model; the icon. Done 2026-11-22.
5. Export, ini, MDK2 build, check the deployed copy. Done 2026-11-22.
6. In-game test. First look (owner, 2026-11-22): "oh man this is good". **Passed, every test** (owner, 2026-11-22: "all of those test pass"); committed as GVK_Suspension 2d222d5. The owner then saw the tread pushed below the ground under every track wheel (next section). The six tests above on the double design, plus: the tread sits on both bands (checks the X sign), a mixed 1x1/2x2/3x3 double track, a Track Wheel block idler, Keen's and an offroad suspension, a 10 m 5x5 double, and a fit check between two blocks.

### Decisions

- **DD1, widths: decided** (owner, 2026-11-22: "Yes, 0.20 spacer"): 4.88 m wheel, 0.20 m spacer, 2.34 m bands, 4.96 m tread. Round 2 (owner, 2026-11-22: "I'd like the wheels to be a little narrower so the tread appears to have some more overhang"): bands 2.24 m round the same centers, so each band's horn stays in its groove; the spacer grows to 0.30 m, the wheel is 4.78 m and the tread hangs 9 cm past each outer edge. The 5x5 double follows: 4.64 m bands, 0.50 m spacer, 9.78 m wheel.
- **DD2, 5x5: decided, a 10 m double** (owner, 2026-11-22: "lets keep the 5x5 double wide in play, but its double wide would just be a 10m width instead of a 5m width"). The 5x5 double is the 3x3 double at twice the width: two bands with a spacer (sizes in DD1), 9.96 m tread across four cells. Its link is the double link at SegmentScale 2.01, 2.13, 2.13, so the pads stretch only 6% lengthwise, close to the single 5x5's proportions.
- **DD3, where the doubles sit across the cells: decided, between the grid line at the mount and the line four cells out** (owner, 2026-11-22, marked in `Source/KharakTread/reference/double_5x5_bounds_owner_2026-11-22.webp`: "this is what I want the 5x5 wheel to stay inside"). The 10 m double spans 5 to 15 m from the mounting face, the 5 m doubles 2.5 to 7.5 m, each centered on the single's line less 0.13 m. The inner band covers the part of the mount that pokes past that grid line. Background: The wheel's attach point (its mount on the suspension) is 2.675 m from the mounting face on the 1x1 to 3x3 and 5.531 m on the 5x5 (Lifted Short; groove line minus the groove's distance from the attach point, track-wheel-swap.md). Centered on a grid line, the 5 m double spans 2.5 to 7.5 m and its inner band reaches 0.12 m behind the mount; the 10 m double spans 5 to 15 m and reaches 0.47 m behind it, into the suspension. Shifting the 10 m double out one more cell (7.5 to 17.5 m) clears the mount but puts the track 2.4 m further out than the single 5x5.
- **DD4, the gap between the two wheels: decided, the groove hub** (owner, 2026-11-22: "Yes, same as groove"). The gap shows the same recessed hub as the groove between each wheel's two rubber rings. After the round 2 renders the owner simplified it to a plain channel, without the groove's bevels and wear strips (round 3).

## Tread above the ground (built 2026-11-22, passed in game)

Tested in the NPC Dev world the same day (owner, 2026-11-22: "I tested it and it works great").

Owner, 2026-11-22: "the tracks get pushed below the surface of the ground, can we shrink the visual diameter of the tank track wheels so the visible track can wrap closer but still stay above the ground? this is for all of the tank track wheels".

### Why it sinks

- A wheel touches the ground with its collision sphere, which is smaller than the tire it draws. The track wheels copy the vanilla tires on both counts (vanilla tire spec, track-wheel-swap.md), so the drawn rubber already reaches below the ground:

  | Size | Drawn radius | Collision sphere | Rubber below ground |
  |---|---|---|---|
  | 1x1 | 1.278 | 1.1 | 0.178 |
  | 2x2 | 2.553 | 2.278 | 0.275 |
  | 3x3 | 3.829 | 3.4 | 0.429 |
  | 5x5 | 6.337 | 5.8 | 0.537 |

  Drawn radii are half the model's bounding box width, read from the `.mwm` files. The sphere radii are the GVK track wheels' own collision (built to the vanilla values), and they gave the same top speed as vanilla tires in game (owner, 2026-11-22). Offroad tires draw 1 to 4 cm bigger.
- Tank Tracks wraps the track round the radius it measures from the wheel model (half its bounding box width, `Roller.cs:263-264, 519-520`). Its hull points sit on a slightly bigger circle, sqrt(R² + (link pitch / 2)²) (`Roller.cs:190-195`), and the straight bottom run between two wheels lies on that circle. The tread's outer face sits a link thickness further out: 0.215 m on 1x1 to 3x3, 0.458 m on the 5x5 (SegmentScale Y 2.13). So the bottom run's tread surface is 0.451 / 0.519 / 0.664 / 1.049 m below the ground. Tank Tracks lifts long straight runs onto the terrain (`GroundCollide`, `Track.cs:1076-1250`), but only their lower half, never the part wrapped round a wheel.

### Fix

Lower the tread by that amount and draw every track wheel smaller by the same amount, so the tread's outer face ends where the collision sphere touches the ground and the tread still wraps the drawn wheel. Collision, attach points, grip and speed stay as they are, and so does the track line across the vehicle.

| Size | Drawn radius now | New drawn radius | Tread drop (SegmentOffset Y) | Offroad style Y |
|---|---|---|---|---|
| 1x1 | 1.278 | 0.827 (-35%); 0.833 since the 1x1 middle ground | -0.451; -0.615 since then (reports 1.448) | -0.405; -0.615 since then |
| 2x2 | 2.553 | 2.033 (-20%) | -0.519 | -0.541 |
| 3x3 | 3.829 | 3.165 (-17%) | -0.664 | -0.697 |
| 5x5 | 6.337 | 5.288 (-17%) | -1.049 | -1.091 |

Offroad tires have the same collision spheres as vanilla ones (read from Keen's `WheelSuspension*_Racing.mwm`), so their Y uses the same formula with the offroad radius (1.23 for the 1x1, Digi's override; 2.575 / 3.862 / 6.379). Y is in metres, + outward, and Tank Tracks moves its ground rays with it (`Track.cs:1087-1096`). Every SegmentOffset restates its X.

1. **Models.** Rebuilt at the new radius, scaled in radius only (hub, cups and bolts with it; width, groove line and axle stub unchanged): `TankWheel1x1/2x2/3x3/5x5`, the swap-only `TankWheel1x1_Lifted` and `TankWheel5x5_Lifted`, the four Track Wheel block models (`TankWheelBlock1x1/3x3` and their `_Lifted` idlers) and the six doubles, with every LOD and build stage. Suspension wheels keep their vanilla-size collision sphere and every dummy (checked byte for byte against the previous files). The Track Wheel blocks' convex hull now reaches 1.1 / 3.4 m, the tread's outer face, instead of the old drawn tire (about 1.25 / 3.75 m): a block idler touching the ground then holds the tread on it, as a suspension wheel's sphere does. The 1x1 block's mounting flange (0.99 m) is now wider than its 0.83 m wheel. The axle stubs and the blocks' posts keep their old size. The 1x1 groove is cut deeper and a little wider (floor 0.31 m from the axle), because the tread's 0.44 m guide horn would otherwise reach 6 to 9 cm into the hub; on the bigger sizes the horn clears the groove floor by 0.4 m or more.
2. **What each roller reports.** One track is drawn with one style, picked from its biggest wheel (`Track.cs:168-276`), so every wheel on it has to report a radius that the style's one drop fits. `[WheelOverride] Radius` sets it, per the scheme below. Vanilla and offroad tires need an override too: after a destroyed track the surviving wheels stay swapped (`Roller.cs:113`), and a rebuilt track would measure the smaller swapped model. A later mod's WheelOverride replaces Digi's whole entry, so ours restates his values (`RealWheel1x1` Width 2.5; `OffroadRealWheel1x1` Width 2.5, Radius 1.23; mirrored too).
3. **Styles lower the tread:** every Kharak Tread and Kharak Double Tread style on a GVK track wheel, a swapped tire or a Track Wheel block (`_Static`) gets the drop above.
4. **Styles that draw round tires GVK does not shrink stay as they are.** Zantulo and Offroad Lifted draw the Kharak Tread round their own tires through the same `_Track` styles as Short Track. They got their own copies with Y 0 (`KharakTread_Large_<size>_Zantulo`) until their swaps were wired on 2026-11-22; those copies are gone. Tank Tracks picks a block's style by the design the player chooses, so the new style names don't break tracks already built.
5. **Over-the-tire styles on GVK track wheels.** Short Track and Lifted Short Track also list Digi's over-the-tire track (`LiftedOTT_Large_<size>_Offroad`), which would float above the smaller wheel. They get copies lowered by the same drop (`LiftedOTT_Large_<size>_Offroad_TrackWheel`); Lifted Short keeps the original, since its vanilla tire does not shrink. The Track Wheel blocks get the same for Digi's static styles (`VanillaOTT_Large_1x1_Static_TrackWheel`, `_3x3_`).
6. **Tread collider.** Tank Tracks reads the `track_collider` empty's scale as half its size (`DefinitionsInternal.cs:375`), and the Kharak Tread colliders were set at full size, so a run lifted onto a bump floated 0.11 m above it (0.23 m on 5x5). The collider is halved in `KharakTread.mwm`, `KharakDoubleTread.mwm` and their scenes in `KharakTread.blend`.
7. MDK2 build and deployed copy checked (2026-11-22). An independent review read the Tank Tracks code and the new files and recomputed every drop to within 1 mm. In-game test: see the list below.

In-game test (full game restart first: the wheel models changed, and the Track Wheel blocks' collision too):
- T1. One-size tracks, every size: Short Track 1x1, 2x2, 3x3, 5x5 with Kharak Tread on flat ground. The tread's outside rests on the ground, the tread wraps the smaller wheels with no gap and nothing poking through.
- T2. Swaps: the same on Keen's Suspension 3x3 and Offroad Suspension 3x3, and Lifted Short 5x5. Wheels swap and the tread rests on the ground.
- T3. Mixed one-size track: Short Track 3x3 and Lifted Short 3x3 on one track.
- T4. Track Wheel blocks: a 3x3 track with a Track Wheel 3x3 block idler, and a 1x1 track with a Track Wheel 1x1 idler, with Kharak Tread and with Digi's track. Expected: tread wraps the idler. A 3x3 track with a 1x1 idler is expected to cut about 0.21 m into the idler (Scheme A).
- T5. Kharak Double Tread on Short Track 3x3 and on Offroad Suspension 3x3: both bands on the ground.
- T6. Destroy one track wheel under a track (grinder), rebuild the track: it looks the same as before.
- T7. Digi's over-the-tire track on Short Track 3x3: it wraps the smaller wheel, not floating.
- T8. Zantulo Lifted 3x3 with Kharak Tread: unchanged from before (still sinks). Superseded: Zantulo now swaps (track-wheel-swap.md).
- T9. Drive each over rough ground: no wheel catching on terrain it seems to clear, top speed unchanged. Small bumps may show through long straight runs (limit below); taller ones lift the tread onto them.
- T10. A Short Track 3x3 with no track: the wheels are expected to hover about 0.24 m above the ground (limit below). Say whether that is acceptable.
- The NPC Dev world still loads `TankTracks_SwapTest`, which adds its own style to Keen's 3x3 and 5x5 suspensions; pick Kharak Tread there.

### Mixed sizes: Scheme A picked

The drop has to be one number per track, but the right drop differs per size. Two ways to set the radii. **Picked: Scheme A** (owner, 2026-11-22: "try one-size tracks, I really want these to play nicely with vanilla blocks. If I don't like it then we can switch to the all-gvk tracks later").

- **Scheme A, one radius per size.** Every wheel reports its size's vanilla radius. Exact on any track of one size, GVK and swapped vanilla tires mixed. On a mixed-size track the smaller wheels get the big wheel's drop and the tread cuts into them: on a 3x3 track a 1x1 by 0.21 m and a 2x2 by 0.14 m; on a 5x5 track a 3x3 by 0.385 m, a 2x2 by 0.53 m and a 1x1 by 0.60 m.
- **Scheme E, one drop for all GVK wheels.** GVK track wheels and Track Wheel blocks report their new drawn radius plus 0.664, so the 3x3 drop fits every GVK size. Exact on any all-GVK track, mixed sizes and idlers included, and on GVK with vanilla 3x3 tires. Off on mixed tracks of GVK with swapped vanilla 1x1, 2x2 or 5x5 tires, and vanilla 5x5 with idlers. Switching later means new Radius overrides and drops; the models stay.

Limits (both schemes):
- **Small bumps show through long straight runs.** Tank Tracks casts its ground rays only down to the lowered link's inner face, not its outer face (`Track.cs:1088`), so on a straight run of 3 or more links (2.3 m; 5.0 m on 5x5) a bump lower than the tread's thickness (0.215 m; 0.458 m on 5x5) is not seen and pokes through. A taller bump lifts the run onto it, exactly (collider fix, step 6). Before this change every run was lifted, floating 0.11 m. Fix if it shows: one tread model per size with the drop built into the model and Y back to 0 (8 more tread models), or ask Digi to cast the ray to the outer face.
- **Track wheels hover with no track.** A GVK track wheel is drawn smaller than its collision sphere, so on a suspension with no track (or a destroyed one) it hovers 0.27 / 0.25 / 0.24 / 0.51 m above the ground. Swapped Keen tires that stay swapped after their track is destroyed do the same (`Roller.cs:113`).
- **A tire on the other kind of suspension gets the wrong drop.** The game lets any wheel go on any suspension, and Tank Tracks picks the style by the suspension. A Keen tire on a Short Track suspension gets the lowered tread without a swap, so the tread cuts into it; a GVK track wheel under Digi's track on a Keen or Zantulo suspension gets a tread that floats. Short Track could list the swap style instead, but every plain Kharak Tread track would then depend on the swap (hub #345).
- **The radius overrides depend on mod order.** GVK_Suspension must load after Digi's track pack (3209008231), or his WheelOverride entries replace ours for the four 1x1 wheels he lists. True in the NPC Dev world and the Season 10 list.
- The swap-only `TankWheel1x1_Lifted` and `TankWheel5x5_Lifted` and the `_Lifted` idlers were shrunk too, but are no longer used: the Zantulo mount moved instead (track-wheel-swap.md).
- Tank Tracks spins a wheel at speed / reported radius (`Roller.cs:421, 657`), so the smaller drawn wheels turn slower than the tread moves: 35% slower on the 1x1, 17 to 20% on the others.
- On rough ground a sphere can still dip a few centimetres into a voxel edge, so the tread may touch the ground there; it no longer sinks by its own thickness.
- The collision sphere now reaches past the drawn tire, so a wheel can bump a wall it seems to clear.
- The 1x1 loses about a third of its drawn size. A thinner tread on 1x1 (SegmentScale Y below 1) would let it shrink less.
- Rejected: one drop with per-size tread thickness (the tread's horns scale and pierce the hub), and shrinking the radius Keen's tires report (breaks Digi's over-the-tire track on Keen's suspensions). The radius shrink was later picked anyway to stop links bunching, with Digi's styles retuned: [Link bunching on curves](#link-bunching-on-curves-plan-2026-11-22). The radii, drops and spin figures in this section are from before it.

### 1x1 on mixed tracks (passed in game 2026-11-22)

Seen in game (owner, 2026-11-22): every 1x1 wheel clips under a 3x3 or bigger track, and the GVK 1x1 face "looks like an opened soda can" (a 3 cm wall round a 1 m deep cup, with the tread visible inside). Bigger wheels hide their sink in their deep groove; the 1x1 cannot. A per-wheel drop in Tank Tracks was rejected (owner: "no, not doing that").

**Settings (middle ground).** Every large 1x1 wheel reports a bigger radius, by d, and every style a 1x1 leads lowers its Y by the same change in hull radius, so a 1x1-only track stays exact (same ground contact, the tread wraps 6-8 mm further out). Under a bigger wheel's style the 1x1 sinks d less.

| | d = 0.15 | d = 0.17 (offroad 1x1 shares the vanilla radius) |
|---|---|---|
| 1x1 Radius (track wheel, idler, Keen 1x1 tires) | 1.428; offroad 1.38 | 1.448 for every large 1x1 |
| Y, Kharak and Double 1x1 `_Track` / `_Swap` / `_Static` | -0.595 | -0.615 |
| Y, both `_Swap_Offroad` | -0.549 | -0.615 |
| Y, `LiftedOTT_Large_1x1`, `_Offroad` | -0.141, -0.140 | -0.160 |
| Y, `LiftedOTT_Large_1x1_Offroad_TrackWheel` | -0.592 | -0.611 |
| Y, `VanillaOTT_Large_1x1_Static_TrackWheel` | -0.737 | -0.756 |
| Merge `[Track:VanillaOTT_Large_1x1]`, `SegmentOffset` | 0.09, -0.317, 0 | 0.09, -0.335, 0 |
| 1x1 cut under a 3x3 (was 0.21 m) | 0.06 m; horns clear the hub by 1.4 cm (offroad 3x3: 2 cm into it) | 4-8 cm; horns clear by 3 cm (offroad 3x3: level with the groove floor) |
| 1x1 on a 2x2 track | floats 6-8 cm | floats 8-10 cm |
| 1x1 spin vs tread | 10% slower | 12% slower |

Keen's static `Wheel1x1` / `OffroadWheel1x1` overrides stay as they are. No d fixes a 1x1 under a 5x5 (the scaled horn passes the axle): unsupported.

**Model.** New 1x1 face profile (prototypes in scene `proto_1x1`, render `Source/TrackWheels/review/wheel1x1_face_options_r1.png`):
- A: a thick rim ring and a shallow 0.18 m dish, hub boss just past the face.
- B: a nearly flat disc with a raised hub.

Both hide the tread inside the wheel. The pick goes into `TankWheel1x1`, `TankWheelBlock1x1`, `TankWheelDouble1x1` and `TankWheelBlockDouble1x1`, with LODs and build stages; the joining bolts and lug nuts move onto the new face.

Picked (owner, 2026-11-22): d = 0.17 with the shared offroad radius, and face A.

Built 2026-11-22: the ini values above (d = 0.17 column), and the four 1x1 models with face A (Main, LOD1-3, build stages). The drawn 1x1 grew to 0.833 m (reported radius + drop) so the tread still rests on it; joining bolts and lug nuts sit on the dish floor. Same day (owner: "simplify the black rubber rub strips inside the centers so it doesn't have the extra step in it"): the groove's rub strips on every track wheel, Track Wheel block and double are one plain band (was 0.085 m on the inner half, 0.045 m on the outer half), then cut to a quarter, 0.021 m thick (owner: "like 1/4 the thickness so they look more flat like rub strips"); then removed from every wheel (owner: "unnecessary detail no one needs for more triangles"; 384 fewer faces on each single wheel's Main model, 768 on a double). All wheel models rebuilt. Face A round 2 (owner, same day): the joining-bolt ring removed, the lug nuts 1.5x bigger on the same circle ("Bigger bolts"), and the dish 0.30 m deep (was 0.18; the hub boss still ends just past the face). Then the hub (owner: "doesn't look so much like a cone"): a straight round boss filleted into the hub plate, a small chamfer and a flat end cap with the decal, like the bigger wheels' hub. Then half its height (owner: "don't like how the hub cap face sticks out past the rim face"): 0.15 m above the hub plate, so the cap sits 0.09 m inside the rim face. Then (owner: "spread out the diameter of the bolts just a tad, it looks like no one can fit a socket on them"; "smooth the base of the hubcap where it flanges out more"): lug circle 1.80 design (was 1.60), and the hub's base fillet twice the radius, in 8 steps. Then (owner: "make the rim diameter wall a little thinner so the rubber track can be thickened while keeping the same overall outside diameter"): the 1x1's rubber inner radius 3.35 design (was 3.504), so its rubber is 8.9 cm thick (was 5.5) and the steel rim ring 3.4 cm thinner; outside diameter unchanged. On every wheel the bolt bosses are `PaintedMetalScratched_Colorable` (Chrome first, then owner: "color matched metal but not painted"; the worn colorable metal under the bolt-head decal), and the painted metal texture is finer, 0.14 UV per metre (was 0.10; owner: "scale down the texture on all of the tank track wheels a bit more").

Face cuts (owner, 2026-11-22: "Plain hull-side face", "48 segments on 1x1/2x2", "Drop tiny bevels"): the hull-side face of every wheel is the rim lip, then a flat plate in to the axle stub, with no bolts; the 1x1 and 2x2 (their Track Wheel blocks and doubles too) are 48 segments around (was 64); the axle stub is 24; the rubber bands lost their edge chamfers, the outer face's corner arc has 2 steps (was 4) and the hub fillet 3 (was 6). The Track Wheel block double 3x3 keeps its recessed hull-side cup, since a flat plate there would cut into the block's flange. Main-model faces, before and after: 1x1 3217 to 1953, 2x2 4049 to 1969, 3x3 and 5x5 4049 to 2545, Block1x1 3393 to 2193, Block3x3 4225 to 2881, BlockDouble1x1 4545 to 2817, BlockDouble3x3 5377 to 4353, Double1x1 4369 to 2625, Double2x2 5201 to 2593, Double3x3 and 5x5 5201 to 3393. All models, LODs and build stages together: 184,024 to 121,224 faces.

Hull side of the 2x2 to 5x5 back (owner, same day: the flat plate is "super bland when walking around underneath the rover", "maybe it doesn't need as many angles"; the 1x1 "is fine now"; picked "D: simple cup + bolts" from `Source/TrackWheels/review/hullside_options_r1.png`): the recessed cup again with fewer angles (its bulge and corner arc are one straight wall with a chamfer; the floor slope and raised hub ring stay) and the 8 joining bolts back on the cup floor. The Track Wheel block double 3x3 now uses it too, as it clears the flange. Main faces: 2x2 2321, 3x3 and 5x5 2993, Block3x3 3329, BlockDouble3x3 4225, Double2x2 2993, Double3x3 and 5x5 3889 (448 more than the flat plate on a 64-segment wheel). The 1x1, its block and doubles keep the flat plate.

In-game test, after a full restart: a 1x1-only track; vanilla and offroad 3x3 tracks with a 1x1 idler; a 2x2 track with a 1x1 idler; Digi's track on a Keen 1x1. **Passed** (owner, 2026-11-22: "test passes"; runbook E21).

### Rubber track (T6, plan 2026-11-22)

The first T6 style: a pure rubber track that takes the place of Morue's CV90 Mk4 look (owner, 2026-11-22: "I like the idea of this for a pure rubber tank track. I believe it can replace the CV90 Mk4").

- **Link look:** one lug of Keen's 3x3 tire, straightened: a rubber block with chamfered ends, a chevron crown, and a stepped notch about a quarter in from each edge (owner's picture, `Source/RubberTread/reference/rubber_link_owner_2026-11-22.png`). Checked 2026-11-22: the lug matches Keen's `WheelSuspension3x3_LOD0.mwm` (rubber materials `RubberWheels`, `RubberWheelsScratched`, `RubberDry`). It is not Digi's vanilla `Segment`, which is a metal frame with side plates.
- **Wheels:** the single track wheels only, every size (owner: "It will use the single track wheels"). No double version.
- **Width:** the track overhangs the wheels well beyond their tread, as the CV90 Mk4 did (owner: "it should overhang by quite a lot to give it some nice width"). For scale, the CV90 Mk4 was 3.68 m wide on 3x3, shifted 0.9 m outward (`SegmentOffset` X), and 6.83 m on 5x5, shifted 0.8 m; 1x1 and 2x2 sat centered at 2.63 and 3.41 m (Morue ini, `CV90mk4_Large_*`). The GVK 1x1 to 3x3 wheels share a 2.80 m tread and the 5x5 a 5.96 m one. Tank Tracks draws a whole track at the width of its widest wheel's style, so a mixed 1x1 to 3x3 track keeps one width if those sizes share it.
- **Model:** vanilla materials only, no new textures. Pivots, collider, LOD1-3, construction model, the vertex budget and the build checks follow the Kharak Tread ([The tread model](#the-tread-model)). Visual only: grip and collision stay the wheels'.
- **Ini:** a new design with the same style set as the Kharak Tread (`_Track`, `_Swap`, `_Swap_Offroad`, `_Static`, the `[Blocks]` lines), with its own link, scale and offsets.
- **R1, link source: decided** (owner, 2026-11-22: "Build from Keen's tire"): cut one lug out of Keen's 3x3 tire mesh and straighten it, keeping Keen's shape and rubber materials.
- **Link study r2 (2026-11-22, `Source/RubberTread/RubberLink_study_r2.blend`, scripts in `Source/RubberTread/scripts/`):** Keen's tire has 19 lugs, one every 18.95°, 1.27 m apart at the crown, on a 2.61 m tread. Each groove is a ramp down from a straight chevron edge, then a stepped vertical wall back up to the next lug, about 0.1 m deep (`RubberDry`). The build unrolls a three-lug strip of the tire's rubber, trims the sidewalls 0.39 m below the crown, shears the chevron straight (slope 0.346), cuts one link between two groove edges, and closes it with a flat inner face 0.05 m below the trim. Result: 3.14 x 1.27 x 0.44 m, 440 vertices, closed. Not yet scaled, pivoted, UV-checked or given LODs.
- **R2, guide horn: decided** (owner, 2026-11-22: "Yes, add a horn"): a rubber horn the Kharak Tread's size (0.40 wide, 0.32 long, 0.44 deep, tapered) under the center, in the wheel's 0.57 m groove.
- **Proportions** (owner, 2026-11-22: "its too narrow, it looks like it needs to be stretched wider"): the owner's picture is about 6 times as wide as long; study r4 is modelled at 3x3 size, 3.70 m wide on a 0.61 m pitch, 0.30 m thick, centered on the wheel. Study r5 (owner, 2026-11-22: "a little deeper and a little more wider"): 4.00 m wide, lips 0.25 m deep.
- **Recessed profile** (owner, 2026-11-22: "I want it to also have a recessed profile so it wraps around down over the wheel rim a bit"): the inner face is flat across the 2.80 m wheel tread, then each overhang drops 0.15 m past a 5 cm side gap and a 6 cm chamfer, so the lips hang down beside the wheel (study r4, `review/link_r4_end_on_wheel.png`; 0.25 m in r5).
- **Shape r7** (owner, 2026-11-22: "overall shape is good"; then "rather than a hard vertical face, I think it needs to have a wide triangular front and back that will intersect with the adjoining links and hide any potential gaps from it curving or stretching", "There are some hard corners that look odd too", "the top middle has some very gradual angles that I think can be straightned out and simplified"): each end is a full-width triangular nose, 0.12 m forward at 0.12 m above the inner face, so neighbours overlap; edges sharper than 50° get a 2.5 cm bevel; the crown is one flat face (Keen's raised center diamond and cross curve removed). 1,591 vertices before LODs.
- **End profile r9** (owner markup 2026-11-22, `Source/RubberTread/reference/end_profile_owner_2026-11-22.png`: green lines for the profile, red for the hard edges to remove; then "you still have remnants of that upward slope with the harsh cut you did on the left"): seen from the side, each end is six-sided. The crown stops short of the end (3 cm at the front, 16 cm at the back), slopes to a full-width tip 0.13 m past the end and 0.03 m above the inner face, then slopes back to the bottom corner. Keen's groove behind the stepped wall is filled to the crown first, so the back slope cuts solid rubber and the pockets become notches in its top edge. The lip's outer face is squared (Keen's shoulder corner made the red vertical edges). Weighted normals. 4.00 x 0.87 x 0.70 m with the horn, 1,394 vertices.
- **Scratch build s1** (owner, 2026-11-22: r9 "looks awful, I think you need to start from scratch honestly", then "make the tread from scratch using similar notches as the straightened vanilla wheel tread"): no Keen mesh. The link is the side profile (r9's six-sided end, crown setback 8 cm at both ends) intersected with the cross-section (flat crown, double-chamfered shoulders, recessed underside with 0.25 m lips), all built to exact dimensions. Notches read off the owner's straightened-tread picture: two pockets in the back edge 0.65 to 1.36 m from the center, 0.10 m deep with sloped walls and reaching 0.20 m into the crown, plus a 0.04 m step across the middle between them. Horn and size as r9: 4.00 x 0.87 x 0.74 m, 444 vertices, 1.5 cm bevel on edges sharper than 30°. Script `Source/RubberTread/scripts/rt_scratch.py`, file `RubberLink_s1.blend`.
- **s2** (owner, 2026-11-22: "looking good so far, I don't like that really wide shallow groove on the front top between the two notches. I want notches on the ends too, should be one at each corner"): the middle step is gone. Four corner notches, front and back at each end, run from 1.55 m out through the shoulder, 0.10 m deep with sloped walls and reaching 0.18 m into the top, which leaves a 9 cm ridge between each front and back pair. 556 vertices. File `RubberLink_s2.blend`. Accepted (owner, 2026-11-22: "Yes, keep going").
- **s4** (owner, 2026-11-22: "The sides need a little more detail, some corrugated steps between each one", then, on a first try with small horizontal ribs, "no, I was thinking larger and vertical", then "Stretch the treads to be about 30% longer (in the direction of the track)"):
  - Seen from above, each side is full width in the middle and steps in 5 cm twice toward each end, with 45° step walls, so a run of links reads as a corrugated wall.
  - The whole link is stretched 1.3x along the track: pitch 0.79 m, 1.13 m long nose to nose. The horn keeps the Kharak Tread size.
  - The noses overlap the next link, so they sit 2 cm inside it on the sides and 1 cm inside on the lips and inner face; matching faces there would flicker.
  - 1,076 vertices. File `RubberLink_s4.blend`.
- **s5** (owner markup 2026-11-22, `Source/RubberTread/reference/side_steps_owner_2026-11-22.png`, then "these should integrate with the other slopes and corners, not just be hard cuts"):
  - One step per end instead of two. The middle 0.40 m of each side bulges out 0.115 m, with 45° ramps.
  - The cross-section is lofted along the track, so the shoulder chamfer, side face and lip all move in together toward the ends. No vertical cut through them.
  - The noses still sit 2 cm and 1 cm inside the next link.
  - 1,056 vertices. File `RubberLink_s5.blend`.
- **R3, overhang: decided** (owner, 2026-11-22): centered on the wheel, 0.6 m past the tread on each side, a lip over each rim (s2 as modelled). The link's center is its horn, so the ini uses the Kharak Tread's X, which puts the horn in the groove.
- **R4, name: decided** (owner, 2026-11-22): "Rubber Track", id `GVK_RubberTrack_Large`.
- **R5, 5x5 link: decided** (owner, 2026-11-22). First "Separate 5x5 link" at the 3x3 sizes in metres; then "Scale 2.13x like Kharak" for its length and thickness; then "I think the overhang should be larger on the 5x5 than it is on the 3x3 and smaller wheels", picking a 1.28 m overhang. The 5x5 tread (5.96 m) is exactly 2.13x the 3x3 one (2.80 m), so the 5x5 style is the 3x3 link scaled 2.129 on every axis in the ini: 8.52 m wide, 1.69 m pitch, 0.64 m thick. No separate model.
- **Build plan (2026-11-22, after s5 was accepted: "Yes, keep going"):**
  1. One build script, `Source/RubberTread/scripts/rt_build.py`, makes every level from the s5 profiles into a new `Source/RubberTread/RubberTrack.blend`. It has two SEUT scenes, `RubberTrack` and `RubberTrack_Construction`, with no SBC, exported to `Content/Models`.
  2. Main is s5 (about 1,060 vertices in Blender). LOD1 drops the bevels. LOD2 also drops the notches and pockets. LOD3 also drops the side steps. Distances 10 / 20 / 40 m, as the Kharak Tread.
  3. The construction model is s5 with the top 8 cm lower, so it grows into the finished link without the notches. LOD1 and LOD2 at 15 / 40 m.
  4. Pivots: `track_pivot1/2` at ±0.397 m (pitch 0.793 m). `track_collider` covers the top 4.0 x 0.793 x 0.30 m. The origin is on the inner face; the ini Y drops it so the outer face ends at the collision sphere, as the Kharak Tread.
  5. One vanilla rubber material on the whole link, picked from a render of four (`RubberScratched`, `RubberWheels`, `RubberWheelsScratched`, `RubberDry`). Tiling UVs at 0.5 UV per metre, box projected.
  Steps 1 to 5 built 2026-11-22 (not exported). Vertices in Blender: Main 1,056, LOD1 176, LOD2 136, LOD3 102; construction 712 / 128 / 94. No open edges. The two SEUT scenes have the levels, pivots, collider and LOD distances. Renders: `review/rubbertrack_lods.png`, `rubbertrack_construction.png`, and `rubbertrack_materials.png` (left to right: `RubberScratched`, `RubberWheels`, `RubberWheelsScratched`, `RubberDry`; `RubberScratched` is assigned until the owner picks). The other three were shown again with textures 2.5x and 5x bigger (`rubbertrack_materials_x2_5.png`, `_x5.png`; owner: "They look bad because the pattern is so obvious but it might not be so bad if we zoom in"). **Material: decided** (owner, 2026-11-22): `RubberScratched` at 0.5 UV per metre, as the Kharak Tread pads. Changed to `RubberWheels` 2026-11-23 (see "Bevel and rubber" below).
  6. SEUT export through the live Blender, icon, ini styles (`GVK_RubberTrack_Large`, scale 1 on 1x1 to 3x3 and 2.129 on 5x5, X offset as the Kharak Tread), MDK2 build, check the deployed copy. Done 2026-11-22; in-game test below.
- **Built 2026-11-22:**
  - **Guide horn shortened** to 0.355 m below the inner face (was 0.44). The link is 0.30 m thick against the Kharak plate's 0.215, so with its outer face on the collision sphere its inner face sits 0.085 m inside the drawn wheel (0.18 m on 5x5). The link hides the tire; the shorter horn clears the groove floor as the Kharak horn does. The rim lips clear the rim face by about 5 mm on 3x3 and 1 cm on 5x5 (check in game).
  - **Export read back** (round 1, before the band) from the `.mwm` files: 4.000 x 0.655 x 1.130 m with the nose overlap, pivots at ±0.396 m, collider half extents (2.0, 0.15, 0.396), LOD distances 10 / 20 / 40 and 15 / 40, material `RubberScratched`. Vertices: Main 1,388, LOD1 511, LOD2 398, LOD3 280; construction 1,103 / 350 / 260.
  - **Icon:** five links on a curve, `Textures/Icons/RubberTrack.dds` (256 px BC7 sRGB, one mip, as the Kharak icons), `RubberTrack_Icon` in `Icons.sbc`. Render: `review/icon_r1.png`.
  - **TankTracks.ini:** `_Track`, `_Static`, `_Swap` and `_Swap_Offroad` styles like the Kharak Tread, added to every large-grid `[Blocks]` line that lists a Kharak Tread style, with the same kind of style (84 lines). Y = sphere − 0.30 − sqrt(radius² + (pitch/2)²); 5x5 thickness and pitch times 2.129.

    | Size | X | Y | Offroad Y |
    |---|---|---|---|
    | 1x1 | .554 | −0.701 | −0.701 |
    | 2x2 | 1.326 | −0.606 | −0.627 |
    | 3x3 | .757 | −0.749 | −0.782 |
    | 5x5 (scale 2.129) | .529 | −1.232 | −1.273 |

    `_Static` (Track Wheel 1x1 and 3x3): X 0, the `_Track` Y.
  - MDK2 build passed; the deployed `Models`, `Data/TankTracks.ini`, `Data/Icons.sbc` and the icon match the repo.
- **In-game test (Rubber Track):**
  1. The track builder lists "Rubber Track" with its icon on every large-grid suspension and Track Wheel block. Pass: no Tank Tracks definition errors in the log.
  2. A track on each Short Track size, 1x1 to 5x5. Pass: the outer face sits on the ground, no sinking or floating; the link is centered on the wheel; the lips do not clip through the rim faces; links close on the curve with no gaps or flicker.
  3. 5x5. Pass: the wider overhang (1.28 m each side) reads right next to a 3x3 track.
  4. Lifted Short, Keen's Suspension and Offroad Suspension (swap styles). Pass: the tire shows the GVK track wheel and the tread sits as in step 2. Remove the track and build it again. Pass: the tires come back, then swap again (no crash; Digi's fix is in Tank Tracks v1.1.6).
  5. Track Wheel 1x1 and 3x3 (`_Static`). Pass: as step 2.
  6. Mixed 1x1/2x2/3x3 track. Pass: one tread width, horn in the grooves.
  7. Weld a new track, then drive away. Pass: the construction model shows while welding; LODs switch at 10 / 20 / 40 m without popping.
- **Round 1 in game (owner, 2026-11-22):** "on 3x3s its a tad too thick, on 1x1s its REALLY too thick"; 5x5 "a tad too thick but also its cartoonish, it loses its sense of scale because its so big and so low on detail that it makes the rover look small. I think 5x5 needs a custom read with some more details"; "the LOD distances on this is way too conservative"; "overhang looks good on all tests though"; "the 5x5 wheel needs more bolts to help show its scale too". On texture: scale the UVs "so that the texture looks the same size to the human eye on every wheel then it will help big wheels actually feel bigger". On models: "just 1x1 through 3x3, then 5x5. You can scale thickness right?"; the 1x1 needs no model of its own ("not worth a dedicated track model").
- **What the code says (read 2026-11-22, Tank Tracks v1.1.6 and the decompiled game):**
  - Each link is its own model entity. `SegmentScale` goes into its world matrix: X width, Y thickness, Z along the track. A thickness-only scale works; `SegmentOffset` is in metres and is not scaled. [HARD, `TrackRender.cs:539-558`]
  - Tank Tracks has no LOD or distance setting of its own; the `.mwm` LOD distances decide. The game measures from the link's origin, divides by the Z scale and multiplies by the Model Quality setting: High as set, Medium about half plus 5 m, Low a quarter, Extreme always LOD0. LODs switch out at 1.1x the distance and back at 0.9x. [HARD, `MyLodStrategy.cs:149-173`, `Environment.sbc`]
  - For comparison: Keen's 3x3 tire 5 / 60 / 120 m, 5x5 tire 20 / 60 / 120, suspensions and turrets 20 / 60 / 150, Digi's own track link 15 / 30 / 60. [HARD, read from the files]
  - Keen's 1x1, 2x2 and 3x3 offroad tires are one mesh stretched by radius, with lugs about 5% of the radius deep (0.06 / 0.13 / 0.20 m). The 5x5 is its own mesh with 37 lugs, 1.08 m apart and 0.23 m deep, finer than a stretched 3x3. [HARD, measured on `Wheel*_LOD0.mwm`]
- **Round 2 plan (2026-11-22):**
  1. **LOD distances: decided** (owner, 2026-11-22: "15 / 40 / 100 m", over Keen's 20 / 60 / 150 and 30 / 80 / 200). Construction 20 / 60 m. Re-exported from `RubberTrack.blend` and read back from the `.mwm` files the same day.
  2. **Thickness on 1x1 to 3x3:** the shared link thinned per size with `SegmentScale` Y; the horn and lips thin with it. The drawn track wheels leave a fixed space for the link between the wheel and the ground contact (0.27 m on 1x1, 0.245 on 2x2, 0.235 on 3x3, the sphere radius less the drawn radius), so a thinner link either floats off the wheel or sinks into the ground. **Placement: decided** (owner, 2026-11-22: "Halfway", over on the ground, on the wheel, or a bigger Rubber Track wheel swap): a link thinner than the space sits halfway, its inner face at (sphere − thickness + drawn radius) / 2 from the axle. Three temporary designs went in side by side for one in-game round (built and deployed 2026-11-22); the two not picked are removed after.

     | Design | 1x1 | 2x2 | 3x3 | Off the wheel and into the ground, 1x1 / 2x2 / 3x3 |
     |---|---|---|---|---|
     | Rubber Track (round 1) | 0.30 | 0.30 | 0.30 | none (pushed into the wheel) |
     | A | 0.15 m (sy 0.50) | 0.195 (0.65) | 0.24 (0.80) | 6 / 2.5 / 0 cm |
     | B | 0.12 (0.40) | 0.165 (0.55) | 0.21 (0.70) | 7 / 4 / 1 cm |
     | C | 0.09 (0.30) | 0.135 (0.45) | 0.18 (0.60) | 9 / 5.5 / 2.5 cm |

     **Thickness: decided** (owner, 2026-11-22, after the in-game round: "track test A looks best 1x1 2x2 and 3x3"). The main Rubber Track styles now use A's scale and offsets; designs A, B and C and their 252 `[Blocks]` entries are removed. On the 5x5 link the same round: "the links look too close together, otherwise I guess it works, not 100% satisfied but not sure what else to do". 
     **Lug spacing: band built, then reverted.** (owner, 2026-11-22). A first try stretched the 5x5 link to 1.69 m ("I didn't want the model to be stretched more, I wanted them to be further away from eachother"); renders of the 1.10 m link spaced out showed floating links ("I don't want gaps like they are floating disconnected"); the owner picked 1.45 m ("I like 1.45"), and then "the smaller sizes need to be spaced apart more too". So every link is now a lug on a band, built 2026-11-22 (checkpoints `RubberTrack_before_band.blend`, `RubberTrack5x5_before_p169.blend`):
     - Each link is the old lug (unchanged) unioned with a band: the lug's cross-section, lips and rim faces included, 0.135 m high on the small link (0.45 of the lug, under its 0.20 m pocket floors) and 0.20 m on the 5x5 (flush with its pocket and corner-notch floors), running to 1 cm short of each pivot with the lug's nose below it. Neighbours meet in a 2 cm seam on top. Past each pivot the band's nose is inset like the lug's (sides in by the side step plus 2 cm, inner faces up 1 cm), so two overlapping links never share a face plane. The horn stays under the lug only.
     - Pivots 1.45 m apart on the 5x5 (from 1.10) and 1.045 m on the small link (from 0.793, the same 1.45 / 1.10 ratio). Colliders follow the pivots.
     - Check (2026-11-22, a read-only verify run, then rebuilt): the first band build had about 1.1 m² (small link) and 3 m² (5x5) of shared, coplanar faces at every straight joint (side walls, inner floor, lip walls) that would z-fight, and zero-area bevel faces on the 5x5 where a 0.19 m band met the 0.20 m notch floors. After the fix: no shared faces at a straight joint and no zero-area or zero-UV faces on any level. Bent 15° about the hinge, 0.006 m² (small) and 0.04 m² (5x5) remain, from the link sides squeezing together; the pre-band links measure the same, and the old 5x5 also had 0.07 m² at a straight joint.
     - Vertices: small link Main 1,248, LOD1 196, LOD2 155, LOD3 155, construction 844 / 140 / 139; 5x5 Main 1,026, LOD1 162, LOD2 154, LOD3 155, construction 790 / 138 / 139 (the band's nose insets add stations to every level). Read back from the `.mwm`: pivots ±0.5225 m and ±0.725 m, LODs unchanged (15 / 40 / 100, 20 / 60; 30 / 80 / 200, 40 / 120).
     - Ini Y, still halfway (or on the ground line on 3x3): 1x1 −0.648, 2x2 −0.548 (offroad −0.569), 3x3 −0.704 (offroad −0.737), 5x5 −1.044 (offroad −1.086). Changed with the radii the same day ([Link bunching on curves](#link-bunching-on-curves-plan-2026-11-22)); the links sit in the same place on the ground run.
     - On the 1x1 wheel a 1.045 m link spans 65° (about 5.5 links around), so the 1x1 track looks polygonal; it was 49° before.
     - Renders: `review/rubbertrack3x3_run_*.png`, `rubbertrack5x5_run_*.png`, `rubbertrack1x1_run_*.png`, concept `link5_band_*.png`. Deployed; not seen in game.
     - **Reverted 2026-11-23.** The band was my reading of "I like 1.45" (picked from renders of spaced lugs with no band); the owner never picked it. In game it ran at the link's full width and buried the side steps under a flat slab (owner, 2026-11-23: "its like they are all stuck on fat slabs, all of the side detail is gone", "so you added this band without asking me"). Picked: "Revert, no band": the links are back to the ones approved before it (small link 0.793 m pitch, 5x5 1.10 m), restored from `RubberTrack_before_band.blend` and `RubberTrack5x5_before_p169.blend` and re-exported; the band versions are kept as `RubberTrack_band_rejected.blend` and `RubberTrack5x5_band_rejected.blend`. The build scripts no longer add the band and rebuild the restored files exactly (every level, vertex for vertex). With the bunching fix the old pitch overlaps 1.5% on 1x1 curves and about 1% or less elsewhere, so the 5x5 "too close together" may be gone; ini Y in [Link bunching on curves](#link-bunching-on-curves-plan-2026-11-22).
     - **Bevel and rubber, 2026-11-23** (owner: "they still need a little more detail or something, idk, they just look a bit cartoonish. maybe some bevelled edges will help?", "I think we should consider one of the other rubber textures too"). Picked from close-up renders (`review/bevel_closeup_3x3.png`, `texture_closeup_3x3.png`): bevel "C" and rubber `RubberWheels` (was `RubberScratched`). Bevel C is two passes on Main and construction: 3x the small bevel (4.5 cm on the small link, 6 cm on 5x5, 3 segments) on every edge sharper than 30° and at least 5 cm long (7 cm on 5x5), then the old small bevel (1.5 / 2 cm) on the rest. Both are clamped, so the short steps and notches stay sharp. Built by `two_tier_bevel()` in both build scripts; checkpoints `RubberTrack_before_bevelC.blend`, `RubberTrack5x5_before_bevelC.blend`. Vertices in Blender: small Main 1,336, construction 1,510; 5x5 Main 1,510, construction 910. LODs unchanged. Exported and deployed.
     - **Flush sides, 2026-11-23** (owner: "why do they have this extra inward step on the sides? bring that inner step out so it is flush, but actually make that face a very slight angle inward so I won't see any surface z-fighting between the overlaps of the links"). The nose sides were 2 cm in from the link sides. Now each side is flush up to the step (r1), then one face angles in through the nose: about 3°, 13 mm in at the tip and 4 mm at the joint on the small link (20 mm and 8 mm on the 5x5, whose vertices round to about 4 mm). The joint reads as a shallow V seam. Checked by sampling where a link and its neighbour share a face, straight and bent 8° and 20° about the hinge: no shared outer side face at any bend (before: 0.027 m² on a wheel curve, small link). Still shared, both out of sight: the inner lip walls facing the wheel on a curve (0.013 m² small, 0.017 m² 5x5), and on the 5x5 the corner-notch floors at each straight joint (0.08 m², there before too). Render `review/side_flush_3x3.png` (left before, right after); checkpoints `*_before_flush.blend`. Exported and deployed.
     - **Knob corners, notch fixes and one bevel, 2026-11-23** (owner: "yes fix both", "I want the edges to slope a little more and integrate better", then a numbered-vertex markup: "158 and 165 move inward half way to 153 and 163, and 157 and 164 move down maybe 25% of the wall below them. also I don't think 155 should exist?"; "make the 3x3 match the 5x5 more"; "the bevel underneath on the center knobby to be larger"; "a simple bevel and some shade smoothing to match the vanilla tire rubber look better", then "tone it down like 50%"). Checkpoint of the state before: `*_flush.blend`.
       - Middle knob: its corner at each corner notch is one sloped facet from the crown corner down to the side step, so the corners connect. The crown edge comes halfway in to the notch wall, and the side drops a quarter of the wall below the notch floor (`knob_corner()`, `XK`, `ZK`).
       - Small link scaled from the 5x5 corner (1/1.39): the side's top corner and the notch floor at 0.145 m (was 0.20), so the notch is 15.5 cm deep (was 10), the knob top half-width 0.113 m (was 0.059), and the side drop to 0.061 m (`ZS`, `RK`). The shoulder along the whole link is steeper with it.
       - Bottom chamfer under the knob (owner picked "B" from `review/under_knob_ABC.png`): rises as far as the knob's top drops, at 45°, 14 cm on the small link and 20 cm on the 5x5, back to the normal chamfer at the step.
       - No shared faces with the neighbor on straight track or round a wheel: the notch inner walls lean 5 cm per meter along the link, the notch floors tilt 2° up toward the link end, and the side's top corner in the nose sits above the floor (`nk`). What lines up is left to reverse bends.
       - Bevel: replaces bevel C, which came out a few mm wide because Blender's overlap clamp shrinks the whole bevel to its tightest spot. One round bevel, 3 cm on the small link and 4 cm on the 5x5 (half the first try, which looked too soft), 3 segments, on every top and outer edge sharper than 30°. Each edge has its own limit (45% of the edges it meets and of its faces' depth). The underside and inner lips stay sharp. Shading: smooth to 60°, weighted normals with face strength, so flat faces stay flat (`simple_bevel()`). Bent faces are split after the bevel.
       - Vertices in Blender: small Main 840, 5x5 Main 950. Renders: `review/knob_corner_v3_5x5_vs_3x3.png`, `bevel_half_clay.png`, `bevel_half_tex.png`. Exported and deployed.
     - **Spacing, deeper pockets and Keen's rubber split, 2026-11-23** (owner: "I want them spaced apart a little more, and I want the notches deeper on the 3x3 style. then I want all of the beveled edges to use the different worn scratched rubber like how keen's wheels do"). Each picked from renders: `review/spacing_options_3x3.png`, `spacing_options_5x5.png`, `notch_depth_options_3x3.png`, `rubber_split_options.png`. Checkpoints `*_before_spacing.blend`.
       - Spacing "B", +13.5%: pivots 0.90 m apart on the small link (was 0.793) and 1.25 m on the 5x5 (was 1.10). The links keep their size, so the noses still overlap (by 0.23 m and 0.31 m) and nothing floats. Colliders follow the pivots.
       - Pockets "N1": the small link's middle pockets are 15.5 cm deep, as deep as its corner notches (was 10 cm), which matches the 5x5's proportions. The corners are unchanged.
       - Rubber "M2", Keen's split as on his tires (`review/keen3x3_rubber_split.png`): `RubberWheels` on the tops and underside, `RubberWheelsScratched` on every bevel face, `RubberDry` on the walls (any other face steeper than about 53°). The bevel modifier puts its faces on the scratched slot; `rubber_split()` in both build scripts does the rest. LODs have no bevels, so they carry `RubberWheels` and `RubberDry`.
     - **Missing chamfers and a one-sided face, 2026-11-23** (owner: "on the 5x5 there was a random angled 1 sided face along the long side with notches"; "I want the chamfer and its texture along all of the top edges of the track, some are missing them"). The notch and pocket cuts split each top edge into straight pieces, and each piece read its neighbour's end point as a face with no depth, so the per-edge bevel limit came out 0 on most crown edges and pocket rims. `bevel_limits()` now ignores vertices on the edge's own line or past its ends, scales the limit from a meeting edge by the sine of their angle, and gives a whole straight run its narrowest piece's width, so every top edge and notch rim gets an unbroken chamfer (3 cm small, 4 cm 5x5, less where a notch is tight). The one-sided face was the 5x5's back slope, a big concave face that the planar split cut across its open side and folded over; concave faces are now split into convex pieces first. A bevel that still folds a sliver loses its bevel near the fold and the bevel runs again (only the construction corners need it). Every level: 0 folded faces, 0 coplanar joint overlap, 0 zero-area or bad-UV faces (`joint_check.py`). Checkpoints `*_before_bevelfix.blend`.
     - **Center texture seam, 2026-11-23** (owner: "theres a texture seam right in the middle of both models, can you hide that?"). Keen's rubber textures (`RubberWheels`, `RubberWheelsScratched`, `RubberDry`) do not tile: each shows a hard line where it wraps, about 4x the change between neighbouring pixels. The box projection at 0.5 UV per metre put those wraps at x = 0 (down the middle of the track), at y = 0 (across each link) and, on the 5x5, at x = +-2 m. `uv_box()` now keeps y and z inside one tile (offset half a tile; every link is under one tile long and tall), and across the width the texture mirrors at each tile edge instead of wrapping. `fold_cuts()` cuts an edge along each mirror line (x = 0 on the small link; 0, +-2 and +-4 m on the 5x5), and the odd tiles carry a +2 UV offset so the vertices split there and each side keeps its own tangent. The texture scale is unchanged; the price is a mirrored pattern at each line. No exported triangle now crosses a tile edge (`mwm_uv.py` on the 14 models). The other way to hide it, one tile across each link with no mirror, would make the texture 2x larger on the small link and 4.3x on the 5x5. Checkpoints `*_before_uvfold.blend`. The owner approved it the same day: "oh yeah this is looking great".
     - **Texture turned 90°, 2026-11-23** (owner: "rotate the rubber texture 90 degrees so it matches the direction of keen wheel rubber"). `uv_box()` turns every face's UVs a quarter turn, so the texture's streaks run along the track, as they run round Keen's tires. The scale, the mirror lines and the seam checks are unchanged (no exported triangle crosses a tile edge). Checkpoints `*_before_uvturn.blend`.
     - **Texture scale checked, 2026-11-23** (owner: "Does the scale match near keens tires?"). Keen's large wheels (`Wheel1x1` to `Wheel5x5`, read from their `_LOD0` files, which hold the geometry) carry their rubber at 0.44 to 0.47 UV per metre, one repeat every 2.1 to 2.3 m; the links at 0.5 match within about 10%. The track wheels' rubber stays at 0.125 UV per metre, about 3.6x coarser (owner: "Leave the wheels"). Keen's own tires do not hide the rubber's wrap: hundreds of their triangles cross a tile edge.
     - **No mirror on the small link, 2026-11-23** (owner: "I think the seam looks better in this ornetation than the mirrored. Can you stretch it enough to not need a seam on the 3x3?"). Options rendered first (`review/seam_options.png`: seamless copies of Keen's maps shipped in the mod, one repeat across at both scales, `RubberScratched`, the one Keen rubber that tiles). On the small link (1x1 to 3x3 tracks) the width is now stretched 2x to one repeat, 0.245 UV per metre across and 0.5 along the track and up, so the link has no wrap and no mirror. `fold_cuts()` is gone (small Main 1,028 vertices, was 1,057). Every level: one tile, no triangle crosses a tile edge. Exported and deployed; render `review/stretch_3x3.png`. Checkpoint `RubberTrack_before_stretch.blend`.
     - **Center seam on the 5x5, 2026-11-23** (owner: "I don't want to ship new textures for something so minor, do the 3x3 with one stretched across the top face, and do a seam at the center on the 5x5"). Each half of the 5x5 link is one repeat, stretched 2.15x across (0.2325 UV per metre, about the small link's 2x) and 0.5 along the track and up, so the only wrap is one seam down the center; no mirror, and `fold_cuts()` is gone (Main 1,222 vertices). Every exported triangle that crosses a tile edge spans x = 0, on every level. Exported and deployed; render `review/centerseam_5x5.png`. Checkpoint `RubberTrack5x5_before_centerseam.blend`. Seamless copies of Keen's maps were declined: new textures in the mod for a minor gain.
     - **Small link pockets moved in, 2026-11-23** (owner: "Can you move the two notches on the small link inward just a bit? I also want there back slopes at the top to line up with the same sides end notch top"). The two middle pockets sit 10 cm closer to the center (top edge 0.55 to 1.26 m off center, was 0.65 to 1.36), and each back slope's top edge is level with the corner notches' on the same edge (0.138 m in from the crown edge before the stretch, was 0.20), with the same slope, so the pocket floor is 6 cm shorter (8 cm after the stretch). Every level: 0 zero-area or bad-UV faces, no coplanar overlap at the joints; one texture tile, none crossed. Exported and deployed; render `review/pockets_moved_3x3.png` (top view, before and after). Checkpoint `RubberTrack_before_pocketmove.blend`. Then (owner: "can you make the notch slopes match the same end notch that you just aligned them with?") each pocket's back slope is the corner notch's back wall: from that top edge down to the side step's end at floor height, 45 degrees (was 0.10 m over the 0.155 m depth), so the pocket floor is another 5.5 cm shorter. Checks as above, all clean; exported and deployed; render `review/pocket_slopes_3x3.png`. Checkpoint `RubberTrack_before_pocketslope.blend`.
     - **5x5 pockets lined up, 2026-11-23** (owner: "Can we do a similar treatment to the large track making the notch backs and slopes line up?"). All four pockets (inner pair on the back edge, outer pair on the front) take the corner notches' back wall: top edge 0.25 m in from the crown edge, bottom at the side step's end at floor height, about 48 degrees (was 0.40 at the top and 0.20 at the floor). The pockets keep their places and widths; each floor is about 0.2 m shorter. Every level: 0 zero-area or bad-UV faces, no coplanar overlap at the joints; the only texture wrap is still the center seam. Exported and deployed; render `review/pocket_slopes_5x5.png`. Checkpoint `RubberTrack5x5_before_pocketslope.blend`. The owner approved it the same day: "Oh it's so good".
       - At the wider pitch the two noses' 1 cm raised undersides overlapped in one plane (0.14 m² per joint on the small link, 0.77 m² on the 5x5). The nose underside now rises 2° to the tip, so neighbors cross instead; the joint check finds no shared face on any level, straight or bent 15°.
       - Ini Y moved so every straight run stays where it was, Y' = Y + sqrt(R² + (L/2)²) − sqrt(R² + (L'/2)²): `_Track`, `_Swap` and `_Static` −0.113 / −0.109 / −0.125 / −0.179 (1x1 / 2x2 / 3x3 / 5x5), `_Swap_Offroad` −0.113 / −0.131 / −0.159 / −0.221. Links overlap on curves by 3.8% on 1x1 (was 1.5%) and 1.5% or less on the rest. A 1x1 link now spans 53° of its wheel (was 48°).
       - Read back from the `.mwm`: pivots ±0.45 m and ±0.625 m, Main and construction in three rubbers, LODs in two. Small Main 856 vertices in Blender, 5x5 950. Exported and deployed.
  3. **5x5 link:** its own model, built at full size so its texture stays 0.5 UV per metre and reads the same size as on the 3x3, with finer detail for scale. Overhang stays 1.28 m. Its look is settled one question at a time from renders, before modelling. **Direction: decided** (owner, 2026-11-22: "Finer rubber lugs", over bolted pads on a steel plate or rubber with steel inserts).
     - **5x5 s1** (2026-11-22, `scripts/rt5_scratch.py`, `RubberLink5_s1.blend`, renders `review/link5_s1_links.png`, `_runs.png`, `_close.png`): the 3x3 link's profile at 1.39x in pitch and thickness (1.10 m pitch, near Keen's 5x5 lug spacing of 1.08 m; 0.42 m thick, from 0.64), its real 8.52 m width with the lips over the 5x5 rim, two pockets per side 1.39x the 3x3 pocket, staggered back and front so they read as two rows, and four corner notches. Horn tip at the round 1 radius. 1,342 vertices. Placed halfway, 4.6 cm off the wheel and into the ground.
     - **5x5 s2** (owner, 2026-11-22: "Yes, deeper lugs"; `RubberLink5_s2.blend`, `review/link5_s2_*.png`): pockets and corner notches 0.22 m deep (was 0.14), about half the link, the pockets 1.05 m wide and reaching 0.40 m into the link (was 0.28). 1,198 vertices.
     - **Built 2026-11-22** (owner: "Yes, build it out"; then "those two new inner notches you made, can you move them a little closer to center?", so the inner pair moved from 0.95 m to 0.75 m off the center line; "much better"). `scripts/rt5_build.py` makes `RubberTrack5x5.blend` with SEUT scenes `RubberTrack5x5` and `RubberTrack5x5_Construction`, exported to `Content/Models`. Levels as the 3x3 link: Main 1,198 vertices, LOD1 (no bevels) 178, LOD2 (no notches) 138, LOD3 (no side steps) 102; construction 0.11 m lower with no notches, 798 / 130 / 94. LOD distances 30 / 80 / 200 m, construction 40 / 120: twice the owner's 3x3 pick, since the link is about twice the size and no longer gets the 2.129x distance stretch a scaled link got. Read back from the `.mwm`: 8.516 x 1.35 x 1.562 m with the horn and noses, pivots ±0.55 m, collider half extents (4.258, 0.21, 0.55). The ini's 5x5 styles used it at scale 1, Y −1.027 (offroad −1.069), halfway: inner face 5.334 m from the axle, 4.6 cm off the 5.288 m drawn wheel and into the ground. Renders: `review/rubbertrack5x5_lods.png`, `_construction.png`.
  4. **5x5 track wheel:** more bolts for scale. Check whether the `TankWheel*` models' UVs grow with the wheel; if they do, set every size to one texel density.
     - **Checked 2026-11-22** (`Source/TrackWheels/TrackWheelStudy.blend`, Main meshes; render `Source/TrackWheels/review/wheels_3x3_5x5_now_three_q.png`). The paint is 0.14 UV per metre on every size, but the rubber (`RubberWheels`, a tiling grunge texture) grows with the wheel: 0.26 UV per metre on 1x1, 0.16 on 2x2, 0.125 on 3x3, 0.068 on 5x5, so its scratches are 1.8x bigger on the 5x5 than on the 3x3. The 5x5 is the 3x3 mesh stretched (both 3,558 vertices): the same 10 lug nuts (0.27 m on 3x3, 0.45 m on 5x5) and 16 rim bolts (0.20 m, 0.33 m), each on a `PanelingColorable` seat decal that grows with it.
     - **Built 2026-11-22** (owner: "I also want the regular paint texture to scale appropriately with the diffrent wheel sizes, not only the rubber. Yes build it."). `Source/TrackWheels/scale_pass.py` on `TrackWheelStudy.blend` (checkpoint `TrackWheelStudy_before_scalepass.blend`):
       - Rubber on every `TankWheel*`, `TankWheelDouble*` and `TankWheelBlock*` level rescaled per UV island to the 3x3's 0.125 UV per metre (x0.47 on 1x1, x0.77 on 2x2, x1.84 on 5x5; doubles x0.43 / x0.70 / x1.67). The 3x3 is unchanged.
       - Paint was already 0.137 UV per metre on every size; only faces more than 30% off it were corrected (single faces stretched with the 5x5). Lifted wheel scenes are not used and were left alone.
       - 5x5 single and double, Main and LOD1 (the levels that have bolts): the nuts and their seat decals replaced by copies of the 3x3's at their real size, 16 lug nuts (was 10) and 14 rim bolts on each wheel face (was 8). Custom normals kept (no kept loop changed).
       - Renders: `Source/TrackWheels/review/wheels_before_face.png`, `wheels_after_face.png`, `wheels_after_three_q.png`. All 12 non-Lifted wheel scenes (72 files) exported (SEUT I007, LODs 25 / 50 / 100 read back) into `Content/Models`; MDK2 build passed and the deployed copy matches. These wheels are shared with the Kharak Tread. Not seen in game.
  5. Export, MDK2 build, deployed copy, E23 round 2. Done 2026-11-22 except the in-game wheel check and the 5x5 link spacing.

### Link bunching on curves (plan, 2026-11-22)

Owner, 2026-11-22: "why do all of the links bunch closer together when bending around the wheels?", then "It's actually really noticeable, we should adjust that".

**Cause** (read in Tank Tracks v1.1.6, a read-only research run 2026-11-22):
- Tank Tracks spaces the links around each wheel on a circle of the wheel's reported radius (`WheelOverride` `Radius`, or half the model's width). The link's `SegmentOffset` Y then moves each link inward in metres, without changing the angle between links. A link drawn 0.6 m inside the spacing circle on a 1.45 m wheel gets 0.6 / 1.45 = 42% less room, so neighbours overlap by that much on the curve. [HARD, `Roller.cs:175-221`, `TrackRender.cs:319-431, 521-551`]
- The large negative Y comes from [Tread above the ground](#tread-above-the-ground-built-2026-11-22-passed-in-game): the drawn wheels shrank, while every wheel still reports the larger vanilla radius (Scheme A).
- Overlap on curves before the fix, at the hinge line (the share of each link's length that overlaps the next):

  | Style | 1x1 | 2x2 | 3x3 | 5x5 |
  |---|---|---|---|---|
  | Kharak Tread | 35% | 16.5% | 15% | 13% |
  | Rubber Track | 37% | 17% | 15% | 13% |
  | Digi's track on a Keen tire (his own tuning) | 13% (21% with GVK's 1x1 Merge) | 7.6% | 6.4% | 9.1% |
  | Digi's track on a GVK track wheel or Track Wheel block | 40-48% | 19.5% | 23% | 25% |

**The only fix:** each wheel reports the radius the links are actually drawn at, and Y drops to about 0. Kharak Tread 0.897 / 2.121 / 3.255 / 5.478 m, Rubber Track 0.813 / 2.091 / 3.239 / 5.497. The ini, link models and wheel models offer nothing else: Tank Tracks ignores the pivots' height, and its API only reads. Radius affects no physics: grip, collision and suspension stay the wheels'. Side effects: GVK wheels spin close to the right speed (today 17-35% slow), and links on curves sit 0.4 cm (3x3) to 3.5 cm (1x1) deeper into the wheel, hidden inside the tread (the ground run is kept exact).

**The catch:** `Radius` is set per wheel block, for every design on it. Since every GVK track suspension and Track Wheel block is hidden (`Public` false), new tracks are built on Keen's 16 large tire blocks, swapped to GVK wheels. Those same tires also carry Digi's over-the-tire track (`VanillaOTT`) and GVK's `LiftedOTT` copies, unswapped, drawn over the full-size Keen tire. A smaller radius on a Keen tire moves those tracks into the tire, and after a Y fix they gap apart on curves: 9% on 3x3, 14% (Digi's) to 34% (`LiftedOTT`) on 1x1. Unswapped Keen tires would also spin too fast. This is the "shrinking the radius Keen's tires report" rejected in [Mixed sizes](#mixed-sizes-scheme-a-picked).

**Options:**
1. **Ask Digi for a per-design spacing radius** (for example a style key that sets the circle links are spaced on, relative to the wheel radius). Fixes every GVK design with no effect on Digi's track or Keen's tires. I draft the request and a patch; the owner sends it. Precedent: Digi shipped the swap crash fix in v1.1.6. Waits on Digi.
2. **Shrink every large wheel's radius, Keen's tires included.** Fixes the GVK designs now. Retune `VanillaOTT` (a Merge on Digi's styles) and every `LiftedOTT` Y; those tracks then gap 9-34% on curves and their tires spin fast. One radius per wheel serves Kharak and Rubber, so about 5% stays on 1x1 and 1% on the rest.
3. **Shrink only the GVK-only wheels** (hidden track wheels and Track Wheel blocks). Fixes old tracks only; new builds on Keen tires keep bunching, and a track mixing the two gets two radii under one Y, so one floats or sinks. Not recommended.
4. **Leave it.**

**Picked: option 2** (owner, 2026-11-22: "Shrink all radii"). This reverses the radius rejection in [Mixed sizes](#mixed-sizes-scheme-a-picked) and retires the 1x1 middle ground's 1.448.

**Built 2026-11-22** (`TankTracks.ini`; script `scratchpad\radius_fix.py`):
- Radii: every large wheel of a size reports the Kharak Tread's hinge radius, 0.897 / 2.121 / 3.255 / 5.478 (track wheels, Track Wheel blocks, Keen's tires); offroad tires 0.897 / 2.143 / 3.288 / 5.520 (bigger by as much as their drawn tire).
- Every style's Y moved by the change in hull radius, so every straight run stays exactly where it was: Y' = Y + sqrt(R² + (L/2)²) − sqrt(R'² + (L/2)²), L the style's pitch. Digi's four large styles get Merges (`VanillaOTT_Large_1x1` to `_5x5`); his static styles on Keen's static Wheel blocks are untouched.

  | Style | 1x1 | 2x2 | 3x3 | 5x5 | Overlap on curves after (− = gap) |
  |---|---|---|---|---|---|
  | Kharak Tread and Double, `_Track` / `_Swap` / `_Static` | −0.094 | −0.093 | −0.093 | −0.198 | 0 |
  | the same, `_Swap_Offroad` | −0.094 | −0.115 | −0.126 | −0.240 | 0-1% |
  | Rubber Track, `_Track` / `_Swap` / `_Static` (pitch 0.90 m, 5x5 1.25 m, since 2026-11-23; at 0.793 / 1.10: −0.090 / −0.099 / −0.118 / −0.171) | −0.113 | −0.109 | −0.125 | −0.179 | 3.8% / 0.6% / 0.1% / −0.6% |
  | Rubber Track, `_Swap_Offroad` (at 0.793 / 1.10: −0.090 / −0.121 / −0.152 / −0.213) | −0.113 | −0.131 | −0.159 | −0.221 | 3.8% / 1.5% / 1.2% / 0.2% |
  | Digi's `VanillaOTT_Large_*` (Merge) on Keen's tires | 0.152 | 0.219 | 0.307 | 0.219 | −14% / −10% / −9% / −4% |
  | `LiftedOTT_Large_*` (Zantulo) | 0.346 | 0.423 | 0.307 | 0.219 | −34% / −19% / −9% / −4% |
  | `LiftedOTT_Large_*_Offroad` (Lifted Short, Offroad Lifted) | 0.346 | 0.412 | 0.308 | 0.220 | −34% / −18% / −9% / −4% |
  | `LiftedOTT_Large_*_Offroad_TrackWheel` | −0.105 | −0.107 | −0.357 | −0.830 | 10% / 5% / 11% / 14% |
  | `VanillaOTT_Large_*_Static_TrackWheel` | −0.271 | | −0.351 | | 25% / 10.5% |

- Mixed tracks: 1x1 to 3x3 mixed on one Kharak track are now exact (the same Y on every size). Under a 5x5's tread (2.13x thick) a smaller wheel's tread now rests on the drawn wheel and sits 0.22 m (3x3) to 0.38 m (1x1) below the ground line, where before it cut into the wheel.
- The primary-wheel check still holds without a Width change: Track Wheel 1x1 Width + Radius 5.447 against a vanilla 2x2's 5.191 (offroad 5.342).
- Spin: GVK wheels turn 3-7% slow (was 17-35%); unswapped Keen tires under Digi's track turn 16-42% fast.
- The Rubber Track 1x1 link now spans 48° of its wheel (about 7.5 links around), since links are no longer squeezed.
- MDK2 build passed; the deployed `TankTracks.ini` matches. In game (owner, 2026-11-22): "ok this adjustment you did is WAY better". The gaps on Digi's track (runbook E24 c) not reported yet.

## Open decisions

- **T1, name: decided** (owner, 2026-11-22): "Kharak Tread", ids `KharakTread_Large` / `KharakTread_Small`. One GVK design at first.
- **T2, paint: decided** (owner, 2026-11-22): fixed dark worn metal like the screenshot; the tread never takes the grid's paint. Later the same day the owner asked for the pads in a different material from the plate and picked dark painted metal for the plate with scratched rubber pads.
- **T3, Keen's suspensions: decided** (owner, 2026-11-22: "Yes, add it"): Keen's large-grid suspensions (Suspension, Short, Offroad, Offroad Short, each size and mirror) get Kharak Tread `_Swap` styles in GVK's `[Blocks]`, next to Digi's vanilla track. Their SBC stays untouched. Offroad tires use the offroad Y fix (D5 in track-wheel-swap.md). Keen's small-grid suspensions wait for T4.
- **T4, small grid: decided, later** (owner, 2026-11-22: "lets just do large grid for now, we'll look at doing small grids later because those probably need new track wheel models too"): this plan covers large grid only. `KharakTread_Small` and small-grid track wheels come later, together with D9 in track-wheel-swap.md. Until then, once Morue leaves the mod list, the `SG_*` blocks and Keen's small-grid suspensions offer only Digi's vanilla track (`LiftedOTT_Small_*` / `VanillaOTT_Small`), and small-grid tracks built on Morue designs disappear.
- **T5, 5x5 link:** one link scaled for every size, or a separate wide link for 5x5. Settled by the render review.
- **T6, more track styles: later** (owner, 2026-11-22: "I have two other track styles I want to create after everything is working perfect with the current kharak ones"): two more GVK designs, started once the Kharak Tread and Kharak Double Tread pass every in-game test. First one: [Rubber track](#rubber-track-t6-plan-2026-11-22) (built 2026-11-22, in-game test next); the second is not designed yet.
