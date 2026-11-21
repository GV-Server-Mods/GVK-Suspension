# 5x5 Lifted Short suspension model

**What:** A lifted copy of Keen's short 5x5 suspension model (`MotorSuspensionCompactLarge`), for `LiftedShortSuspension5x5`, `LiftedShortTrackSuspension5x5` and their mirrored pairs. Until now those four blocks used Keen's model unchanged, so they were not lifted at all (owner, 2026-11-21: "the 5x5 lifted short suspension model doesn't actually exist, it reuses the vanilla one").

**Source:** Keen's base-game `MotorSuspensionCompactLarge.mwm` and its LODs and construction models, imported with SEUT. Base-game content, so no DLC tag: SEUT's W012 on `BraidedSteel` and `WarningSignsEaster` comes from Keen's own model, which ships on the non-DLC `ShortSuspension5x5`.

## Decisions

| Item | Choice |
|---|---|
| Lift | 4.06 m, the same as the 5x5 Lifted (`LG_5x5_Lifted_Suspension_ZANTULO`) (owner, 2026-11-21) |
| Shape | Base, drum, column and cables stay Keen's. Only the arm stretches, so the drum shows through a side window about 5.7 m long, as on the 1x1 Lifted Short (`LiftedMotorSuspensionCompact`). Mock: `lift_options.png` |
| Wheel point | `electric_motor` dummy at model Z +3.96 (Keen's: +0.10), same rotation and size as Keen's |
| Direction | The model is turned 180 degrees about its vertical axis against Keen's, so the stretched end faces model +Z (next section) |

## Which end is the ground

The wheel sits at the dummy plus `Forward x Height` (`MyMotorSuspension`). Air shock moves the wheel to `MinHeight` (-2) before a hard landing, so the extended wheel lies toward -Forward, which is model +Z. Both GVK lifted models already move the dummy that way. The first build stretched the -Z end, the end the drum is on in Keen's model, and the test export put the dummy at -3.96, toward the chassis. Turning the whole model kept the drum under the window. The base now sits end for end against Keen's `ShortSuspension5x5`. The mount face and collision are symmetric, so nothing else changed.

## Build

- **Stretch:** `lift_stretch.py`. The arm is cut at 0.845 m from the block center, in a straight run with no end faces nearby and no decal within 4 cm. Every arm vertex past the cut moves 4.06 m. Tiling materials get their UVs refit across the stretch, so the texture keeps its scale. Long non-tiling strips get a thin band at their middle that takes the stretch. Other decal pieces move whole. Corner normals are recorded and restored.
- **Decal snap:** the arm now reaches 7.8 m from the origin, where the game stores vertices on a grid of about 7 mm. `snap_run.py` (se-dev-seut `scripts/decal_snap.py`, shallow dips lifted first) took Main from 2,064 decal triangles broken by rounding to 102. The rest sit on Keen's base, in equal numbers at both arm ends, so they are faults already in Keen's model. Run it last after any rebuild.
- **LODs and build stages:** Keen's LOD1 to LOD4 and three construction stages with their LODs, all stretched the same way. LOD distances are SEUT's 25 / 50 / 100 / 200 m.
- **Collision:** two boxes inside the 2x2x2 bounding box, base and arm. The arm past the block has no collision: collision outside the bounding box makes the game fall back to cube collision.
- **Output:** `Content/Models/LiftedMotorSuspensionCompactLarge*.mwm`. `Model` and `BuildProgressModels` on the four definitions in `CubeBlocks_Suspension_LiftedShort_Regular.sbc` and `_Tracks.sbc` point at it.
- **Checkpoints:** `_before_rotate`, `_before_lift`, `_before_lods`, `_before_snap` and `_before_flip` beside the working `.blend`, on the owner's PC only (git ignores them).

## Gates

1. Lift height and shape, from a mock render. Approved 2026-11-21.
2. Built model, checked against the se-dev-seut pre-export list; dummy and bounds read back from the exported `.mwm`. Done 2026-11-21.
3. In-game test: the vehicle sits about 4 m higher than on the Short 5x5, the wheel sits at the end of the long arm, mirrored placement puts the wheel on the right side, the build stages and LODs show the long arm, and the decals on the far arm end show no broken pieces up close. Passed (owner, 2026-11-21: "Looks good").
