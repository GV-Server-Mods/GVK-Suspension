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
- **Damper rod and cable legs:** the first in-game test showed two parts still at Keen's length in the side window: the damper rod on the +X side (a piston between two black sleeves) ended open short of the drum, and the cable legs on the window ledge stopped short of the window's end wall (owner, 2026-11-21). `lift_stretch.py` (`sgn` and `pick` choose the end and the parts) stretched both legs into the slanted end wall. The damper's front sleeve belongs in the red socket decal on the arm end, which moved 4.06 m with the arm, so the sleeve, its collars and the chrome ring decal at the shaft's end moved 4.06 m too, and the silver shaft stretched 4.06 m to meet them (owner, 2026-11-21: "extend it so it meets where that red socket decal is ... at the silver shaft part"). That matches the plain Short 5x5, where the sleeve ends inside the socket. The ring decal sits 0.8 mm further out than Keen's so the vertex rounding at 4.6 m keeps it whole. All of it in Main, the LODs and the build stages that have these parts. An earlier try that stretched the front sleeve instead and ended it at the drum was dropped.
- **Decal snap:** the arm now reaches 7.8 m from the origin, where the game stores vertices on a grid of about 7 mm. `snap_run.py` (se-dev-seut `scripts/decal_snap.py`, shallow dips lifted first) took Main from 2,064 decal triangles broken by rounding to 102 (83 after the damper fix and the seam joins). The rest sit on Keen's base, in equal numbers at both arm ends, so they are faults already in Keen's model. Run it last after any rebuild.
- **Seam joins:** Keen's panel seam decals in Main now follow se-dev-seut's seam rules (owner, 2026-11-21: "make sure your seam decals all comply with the seut skill", then chose every join, base and arm). `seam_driver.py` (with `seam_map.py` and `seam_fix.py`) found 192 seam strips and fitted the texture of 109 of them exactly onto the seam piece of the atlas. It mitred 17 square corners (9 of them where a closed loop starts and ends), gave the 3 T-joins a pointed stem that meets an unbroken cross seam, and gave 10 free ends a pointed cap. It leaves seams that carry on over an edge or bevel, ends at a face edge, ends that run into another decal, and the 7 corners Keen had already mitred. Main only: the LODs and build stages keep Keen's seams, and the base's seams no longer match the plain Short 5x5 exactly.
- **LODs and build stages:** Keen's LOD1 to LOD4 and three construction stages with their LODs, all stretched the same way. LOD distances are SEUT's 25 / 50 / 100 / 200 m.
- **Collision:** two boxes inside the 2x2x2 bounding box, base and arm. The arm past the block has no collision: collision outside the bounding box makes the game fall back to cube collision.
- **Output:** `Content/Models/LiftedMotorSuspensionCompactLarge*.mwm`. `Model` and `BuildProgressModels` on the four definitions in `CubeBlocks_Suspension_LiftedShort_Regular.sbc` and `_Tracks.sbc` point at it.
- **Checkpoints:** `_before_rotate`, `_before_lift`, `_before_lods`, `_before_snap`, `_before_flip`, `_before_fixes`, `_before_rodremove`, `_before_rodback`, `_before_seamfix` and `_before_mitre` beside the working `.blend`, on the owner's PC only (git ignores them).

## Gates

1. Lift height and shape, from a mock render. Approved 2026-11-21.
2. Built model, checked against the se-dev-seut pre-export list; dummy and bounds read back from the exported `.mwm`. Done 2026-11-21.
3. In-game test: the vehicle sits about 4 m higher than on the Short 5x5, the wheel sits at the end of the long arm, mirrored placement puts the wheel on the right side, the build stages and LODs show the long arm, and the decals on the far arm end show no broken pieces up close. Passed (owner, 2026-11-21: "Looks good"). The extended damper passed too (owner, 2026-11-21: "looks good"). The seam joins passed up close (owner, 2026-11-21: "Looks good").
