---
title: GVK treads (replace the Morue track pack)
covers:
  - Content/Models/KharakTread*.mwm
  - Content/Data/TankTracks.ini
  - Content/Data/Icons.sbc
---

# GVK treads: plan

Status 2026-11-22: plan only, nothing built. Owner, 2026-11-22: "I want to do that, i don't want to keep the same names though because I don't want to be accused of stealing or copying. Besides I want to do a track in the style of the original DoK game." Done before the Zantulo wiring in [track-wheel-swap.md](track-wheel-swap.md), so the track styles are written once.

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

- **Reference first:** load Digi's `Segment.mwm` (3209008231) and one Morue link in a throwaway Blender scene. Measure link length, thickness, pivot empties, axis, triangle count and LODs. They set the budget: a track repeats the link hundreds of times.
- **Shape:** a wide flat plate with a raised pattern, guide teeth on the inside running in the wheel groove, and a short hinge at each end. Built to the DoK look in the owner's screenshot (2026-11-22), modelled from scratch.
- **Files:** `KharakTread.mwm` with LOD1-3 and a construction model (`KharakTread_Construction`), both with pivot empties so the links bend at the hinge. No collision and no block definition: Tank Tracks only draws the model.
- **Materials:** vanilla SE materials only, no new textures. Non-paintable dark worn metal (T2).
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

## TankTracks.ini

1. New design `KharakTread_Large`, display name "Kharak Tread" (T1). Large grid only (T4).
2. Full styles per size, with no Morue inheritance: `_Track` (1x1, 2x2, 3x3, 5x5), `_Static` for the track wheel blocks, and `_Swap` (inherit `_Track`, plus `ReplaceWheelModel`).
3. Retune `SegmentOffset` Y for the new link's thickness, so the tread sits on the vanilla-spec wheels from Part A. X keeps the groove line from track-wheel-swap.md.
4. Remap `[Blocks]`: every GVK suspension and track wheel block lists `LiftedOTT_*` (over the tire) plus the GVK designs. Keen's large-grid suspensions get Kharak Tread `_Swap` styles (T3). Small-grid lines drop their Morue styles and keep `LiftedOTT_Small_*` only (T4).
5. Then wire the Zantulo swaps (track-wheel-swap.md, Part B step 4) on the GVK styles.

## Order

1. Commit Part A of track-wheel-swap.md. The work sits on branch `wheel-swap`; ask the owner about merging it into `main` first (GVK rule: work on `main`).
2. Reference measurements in Blender (checkpoint first).
3. Model the link, LODs and construction model. Owner reviews renders before export.
4. Export, icon, ini rewrite, MDK2 build, check the deployed copy.
5. Remove Morue (3225398014) from the NPC Dev test world (`Sandbox.sbc` and `Sandbox_config.sbc`), the S11 config in gvk-server-config and the Workshop collection.
6. In-game test (below).
7. Player change note (load elements-of-style): tracks built on the old designs disappear and need rebuilding.
8. Wiki decision page; se-dev-kharak if a current fact changes. No new blocks, so no block owner entries.

## In-game test

1. Build a track on each GVK suspension size, 1x1 to 5x5. Pass: the tread sits on the tread line, no gap, no sinking, links bend at the hinge with no gaps on the curve.
2. Mixed 1x1/2x2/3x3 track. Pass: one tread width, guide teeth in the grooves.
3. Lifted Short swap with the GVK design. Pass: same as the Part A swap.
4. Drive at speed and turn. Pass: no visible link popping; LODs switch cleanly at distance.
5. Build-stage track (place, then weld). Pass: the construction model shows, then the finished tread.
6. Load the test world without Morue. Pass: no definition errors in the Tank Tracks log; Keen's suspensions still offer Digi's vanilla track.

## Later: Kharak Double Tread

After the standard Kharak Tread ships (owner, 2026-11-22): a second design that looks like the twin tracks on the larger cruisers in Deserts of Kharak. One extra-wide wheel carries one Tank Tracks track, and its link model draws two tread bands side by side with a gap between them, so it reads as two tracks. Tank Tracks draws one width per track, so the gap has to be part of the link model. The matching swap wheel needs two grooves, one under each band. Not planned in detail yet.

## Open decisions

- **T1, name: decided** (owner, 2026-11-22): "Kharak Tread", ids `KharakTread_Large` / `KharakTread_Small`. One GVK design at first.
- **T2, paint: decided** (owner, 2026-11-22): fixed dark worn metal like the screenshot; the tread never takes the grid's paint.
- **T3, Keen's suspensions: decided** (owner, 2026-11-22: "Yes, add it"): Keen's large-grid suspensions (Suspension, Short, Offroad, Offroad Short, each size and mirror) get Kharak Tread `_Swap` styles in GVK's `[Blocks]`, next to Digi's vanilla track. Their SBC stays untouched. Offroad tires use the offroad Y fix (D5 in track-wheel-swap.md). Keen's small-grid suspensions wait for T4.
- **T4, small grid: decided, later** (owner, 2026-11-22: "lets just do large grid for now, we'll look at doing small grids later because those probably need new track wheel models too"): this plan covers large grid only. `KharakTread_Small` and small-grid track wheels come later, together with D9 in track-wheel-swap.md. Until then, once Morue leaves the mod list, the `SG_*` blocks and Keen's small-grid suspensions offer only Digi's vanilla track (`LiftedOTT_Small_*` / `VanillaOTT_Small`), and small-grid tracks built on Morue designs disappear.
- **T5, 5x5 link:** one link scaled for every size, or a separate wide link for 5x5. Settled by the render review.
