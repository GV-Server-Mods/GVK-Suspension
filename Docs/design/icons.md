---
title: Block icons (full color)
covers:
  - Content/Textures/Icons/*.dds
  - Content/Textures/Icons/Vanilla/*.dds
---

# Block icons: full-color redo

Status 2026-11-22: round 2 passed in game (owner, 2026-11-22: "E18 all passes"), with the lifted badge moved to the bottom left and the G menu tidied (Home positions, one icon per group). Round 1 (24 icons) was rejected in game. The owner wants every icon in full color, like Keen's Warfare III icons (owner, 2026-11-22: "I want to redo all of the custom icons", "need full color").

## Round 2 (owner, 2026-11-22)

Owner, in game: "every suspension icon you made is upside down, you also forgot to do the lifted suspensions, and theres also a bunch of vanilla ones still with blue icons like offroad short wheel suspension left, also a bunch of icons are just missing straight up like the offroad suspension left".

Causes:
- **Upside down.** Every round 1 icon was rolled 270° about the axle, the roll that matched Keen's suspension. Keen's suspension has its wheel mount at the block center, so that check could not tell up from down. The Zantulo and Lifted Short models put the mount about a third of their depth toward the model's +Z (the ground side in game, which is what lifts them), and roll 270 drew it on top. Keen's compact puts its mount the other way, and Keen's icons draw it at the bottom.
- **Missing.** GVK's copies of Keen's suspensions and wheels (`CubeBlocks_Suspension_Vanilla.sbc`, `_Offroad.sbc`, `CubeBlocks_RealWheels_Vanilla.sbc`, `_Offroad.sbc`) named Keen's `WheelSuspension<size>Left` and `WheelSuspension<size>_RacingLeft` icons, which Warfare III removed (33 blocks).
- **Blue.** Those copies, the Lifted Short blocks and the new Offroad Lifted Short blocks named icons Warfare III left in the game but no longer uses: `ShortWheelSuspension*` (except the 1x1 Right), `SmallShortOffroadWheelsSuspension_*` and every `LargeShortOffroadWheelsSuspension_*_Left`.
- **Wrong tire size** (found by review): the large-grid Zantulo 1x1 and 2x2 showed the 3x3 icon.

Fix (built 2026-11-22):
1. **Roll per model:** the wheel mount is always at the bottom of the icon, as in Keen's. `build_icon_scenes.py` rolls 90° when the model's `electric_motor` dummy sits more than a tenth of the model's depth toward +Z, 270° otherwise.
2. **Every GVK suspension, wheel and track wheel block has a GVK render** (table below). Keen's Short 2x2, 3x3 and 5x5 get GVK renders of Keen's compact too, since Keen gives them its regular suspension icon.
3. **Keen's own icons where Keen has a current one:** GVK's copies of Keen's suspensions name Keen's current Right icon, and Left is that icon flipped (`Textures/Icons/Vanilla/`, 13 files). Keen's wheels name Keen's `Wheel<size>` and `Wheel<size>_Racing` icons, and Keen's small short offroad suspensions name the large one, as vanilla does.
4. The Lifted Short and Offroad Lifted Short variant groups use the 3x3 renders.
5. `Source/Icons/check_icons.py` checks that every block and group icon exists and none is one of Keen's retired blue icons (a suspension icon in the game dated before 2026-11-16): 240 icons, all pass, in the repo and in the deployed copy. An independent review compared all 172 blocks and 8 groups with their icons, and looked at every render.

Accepted (review, minor): the small-grid Zantulo 3x3 and 5x5, Keen's small Short and the small 7x7 use the large-grid render, as Keen does for its own small blocks. On the 7x7 suspension the big tire hides most of the block.

## Icon files

GVK renders, each with `_Right` and `_Left` unless marked:

| Icon files | Blocks | Model shown |
| --- | --- | --- |
| `3x3_`, `5x5_Lifted_Suspension`, `3x3_`, `5x5_Lifted_Offroad_Suspension` | Zantulo and Offroad Lifted 3x3 and 5x5, large and small; the 3x3 is also the Lifted groups' icon | `LG_3x3` / `LG_5x5_Lifted_Suspension_ZANTULO` with Keen's tire or offroad tire |
| `2x2_Lifted_Suspension`, `LG_1x1_Lifted_Suspension`, and their `_Offroad_` versions | Large-grid Zantulo and Offroad Lifted 2x2 and 1x1 | `LG_3x3_Lifted_Suspension_ZANTULO` with a 2x2 or 1x1 tire |
| `1x1_Lifted_Suspension`, `1x1_Lifted_Offroad_Suspension` | Small-grid Zantulo 1x1 | `SG_1x1_Lifted_Suspension_ZANTULO` with a small 1x1 tire |
| `<size>_Lifted_Short_Suspension`, `<size>_Lifted_Short_Offroad_Suspension` | Lifted Short and Offroad Lifted Short, 1x1 to 5x5; the 3x3 is also their groups' icon | `LiftedMotorSuspensionCompact` (`...Large` for 5x5) with Keen's tire or offroad tire |
| `<size>_Lifted_Short_Track_Suspension` | Lifted Short Track (hidden from the G menu) | The same with a track wheel |
| `<size>_Short_Track_Suspension` | Short Track (hidden from the G menu) | Keen's `MotorSuspensionCompact` (`...Large` for 5x5) with a track wheel |
| `2x2_`, `3x3_`, `5x5_Short_Suspension` | Keen's Short and Small Short 2x2 to 5x5 | Keen's compact with Keen's tire |
| `WheelSuspension7x7` | 7x7 suspensions | `MotorSuspensionLarge` with the 7x7 tire |
| `TankTrackWheelBlock1x1`, `3x3` (no Left) | Track Wheel 1x1 and 3x3 | `TankWheelBlock1x1`, `TankWheelBlock3x3` |
| `RealTrackWheel<size>`, `Wheel7x7` (no Left) | The GVK track wheels and the 7x7 tire | The wheel alone |

Also: `Lifted_Icon` (the small "lifted" badge drawn over the group icons; flipped to the bottom left on 2026-11-22, since the game draws the DLC icon in the bottom right and the owner saw them collide), and `KharakTread`, `KharakDoubleTread` and `RubberTrack` (the Tank Tracks builder icons; `RubberTrack` added 2026-11-23 and re-rendered the same day from the current link, [gvk-treads.md](gvk-treads.md), "Rubber Track"). `KharakTreadMk2` was added and `KharakTread` and `KharakDoubleTread` re-rendered on 2026-11-24 with `Source/KharakTreadMk2/scripts/kt2_icon.py` (five links on the 3x3 curve; gvk-treads.md, "Kharak Tread detail pass").

## How

Icon Studio was tried first and does not put the wheel on a suspension (owner, 2026-11-22), so the icons are rendered with SEUT's icon renderer in full color:

1. `Source/Icons/build_icon_scenes.py` (background Blender 4.5 with SEUT) reads each model's `.mwm` through GVK_Settings `tools/models/mwm_mesh.py` (vanilla models: the `_LOD0` file), links SEUT's vanilla materials and builds one SEUT main scene per icon, `Icon_<file stem>`, in `Source/Icons/SuspensionIcons.blend`. The wheel's `wheel` dummy sits on the suspension's `electric_motor` dummy and the axle lies flat. The wheel's outer face is toward the camera, with the suspension behind it on the right. `renderColorOverlay` is on (no blue filter). The file also has a mirrored Left scene for each pair, but `render_all.py` renders only the Right one and flips the image for Left, so both icons in a pair are lit the same way (a review found mirrored scenes lit unevenly).
2. `Source/Icons/render_all.py` renders each scene at 512 px with `icon_render.py`, a copy of se-dev-seut `scripts/icon_render_bg.py` that adds the lighting and tone settings. The model is scaled to fit SEUT's distance-1 camera, since SEUT's lights get dimmer as the camera moves back.
3. Angle and look are matched to Keen's `WheelSuspension3x3Right` icon by rendering Keen's own suspension and 3x3 wheel through the same rig (owner, 2026-11-22: "make the lighting match a little closer to keens", "white balance and tone"):
   - Angle: camera 35° up (Icon Studio's, not SEUT's 20°); block turned 262° about the vertical axis, and rolled about the axle by the rule in Round 2 step 1.
   - Look: view transform Standard instead of Blender's AgX. SEUT's shadow and midtone lift is off (it suits the blue look only). Contrast 0.25, fill light at 15%, key light at 160% with a slight warm tint, exposure +1.4, and a gentle midtone curve.
   - Result on the calibration render: average color 78/76/74 against Keen's 81/77/77, with matching shadow, median and highlight levels.
4. `frame_icon.py` crops each render to 75% fill at 128 px (Keen's icons measure 75 to 79%), then texconv writes BC7 sRGB DDS, copied into `Content/Textures/Icons` under lowercase `.dds` names.
5. `check_icons.py`, MDK2 build, `check_icons.py` on the deployed copy, look in game.
