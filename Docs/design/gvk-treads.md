---
title: GVK treads
covers:
  - Content/Models/KharakTread*.mwm
  - Content/Models/KharakDoubleTread*.mwm
  - Content/Models/TankWheel*Double*.mwm
  - Content/Models/RubberTrack*.mwm
  - Content/Data/TankTracks.ini
  - Content/Data/Icons.sbc
---

# GVK treads

GVK's own track designs for Digi's Tank Tracks (Framework 3208995513, Builder 3209005014), large grid only. They replaced the Morue pack (3225398014), so nothing reads as a copy of Morue's. This page holds the final specs, the Tank Tracks behavior they rely on, and the lessons for the next design. Every review round, render pick and superseded number is in this file's history up to GVK_Suspension a4031e3.

| Design | Id | State |
|---|---|---|
| Kharak Tread | `KharakTread_Large` | Passed in game 2026-11-22 (2d222d5) |
| Kharak Double Tread | `KharakDoubleTread_Large` | Passed in game 2026-11-22 (2d222d5) |
| Rubber Track | `GVK_RubberTrack_Large` | Built 2026-11-22 (bd35817), reworked 2026-11-23 (a4031e3); in-game round 2 next (runbook E23) |

The Workshop has the Kharak designs as of @98c8131. The radius fix ([Link bunching on curves](#link-bunching-on-curves)) and the Rubber Track came after and are not published.

Still to do:
- The Rubber Track's in-game round 2 (runbook E23), and the gaps on Digi's track after the radius fix (E24 c).
- The player change note: tracks built on Morue designs disappear and have to be rebuilt. The owner takes Morue out of the Workshop collection.
- The second new style (T6), then small grid (T4).

## How Tank Tracks draws a design

Read in Tank Tracks v1.1.5 and v1.1.6.

- **Design and style.** `[Design:<Id>]` holds `DisplayName` and `Icon` (a transparent material in `Icons.sbc`). The player picks the design in the builder, and a saved track remembers it. A `[Track:<Id>]` style sets `Design`, `SegmentModel`, `SegmentConstruction`, `SegmentScale`, `SegmentOffset`, `ReplaceWheelModel(Construction)` and `AllowOnRotors`; `Inherit` copies another style, and `Merge` changes one from another mod (`DefinitionsInternal.cs:168-184`). `[Blocks]` maps each wheel or suspension block to its styles, and mappings add up across mods (`DefinitionsInternal.cs:34-39`).
- **Visual only.** Grip, speed, collision and suspension stay the wheels' own.
- **One style per track.** Each wheel uses its own block's style for the design picked (`Roller.cs:62-86`), but the track is drawn with the style of its biggest wheel, the one with the largest Width + Radius (`Track.cs:166-306`). So a track has one width and one Y.
- **The link model.** The first two empties named `track_pivot*` are the hinges. Only their Z (Blender Y) counts: pitch = pivot gap x `SegmentScale` Z, and pivot height is ignored (`DefinitionsInternal.cs:272-327`). A `track_collider` empty is the ground-contact box for the terrain rays (`GroundCollide`), and Tank Tracks reads its scale as half its size (`DefinitionsInternal.cs:375`). Names match by prefix, so a construction model's `track_pivot1.c` works (`DefinitionsInternal.cs:361, 371`). Model axes: X across the track, Y outward from the wheel, Z along the track.
- **Scale and offset.** `SegmentScale` (X width, Y thickness, Z length) goes into each link's world matrix, so a thickness-only scale works. `SegmentOffset` (X across, + outward; Y radial, + outward) is in meters and is not scaled (`TrackRender.cs:539-558`).
- **Where the links go.** Links are spaced on a circle of each wheel's reported radius (`WheelOverride` `Radius`, else half the model's width, `Roller.cs:263-264, 519-520`). The hull points sit at sqrt(R² + (pitch/2)²), with the middle of each link's chord on them (`Roller.cs:190-195`). Y moves the links in or out without changing the angle between them, so a negative Y of a few tenths makes the links overlap on curves by Y / R (`Roller.cs:175-221`, `TrackRender.cs:319-431, 521-551`).
- **Ground.** `GroundCollide` lifts long straight runs onto the terrain, their lower half only, never the part around a wheel (`Track.cs:1076-1250`). Its rays reach only down to the lowered link's inner face (`Track.cs:1088`).
- **LODs.** Tank Tracks has no distance setting; the `.mwm` LOD distances apply. The game measures from the link's origin, divides by the Z scale and multiplies by the Model Quality setting: High as set, Medium about half plus 5 m, Low a quarter, Extreme always LOD0. A level switches out at 1.1x its distance and back at 0.9x (`MyLodStrategy.cs:149-173`, `Environment.sbc`).
- **Wheel swap.** `ReplaceWheelModel` draws another wheel model while the wheel is under a track and keeps the tire's collision (`Roller.cs:123-140`). On a static wheel the block itself swaps (`Roller.cs:256-257`). A swapped wheel stays swapped after its track is destroyed (`Roller.cs:113`). The crash on rebuilding a track on swapped wheels is fixed in v1.1.6.
- **Spin.** A wheel turns at track speed / reported radius (`Roller.cs:421, 657`).
- **Saved tracks.** A track whose design id no longer exists skips loading; the save keeps it in the block's storage, and it comes back only if that id returns (`TrackHandler.cs:351-358`). That is why every track built on a Morue design disappears.
- **Traps.** Two styles of the same design on one block break the builder. A later mod's `WheelOverride` replaces another mod's whole entry, so GVK restates Digi's values, and GVK_Suspension must load after his vanilla track pack (3209008231).

## Wheels, radii and drops

All three designs run on the GVK track wheels ([track-wheel-swap.md](track-wheel-swap.md)), which are drawn smaller than their collision sphere so the tread's outer face ends where the sphere touches the ground. Every large wheel reports the Kharak Tread's hinge radius, so the Kharak links neither bunch nor gap on curves.

| Size | Drawn radius | Collision sphere | Reported radius | Offroad tire reports |
|---|---|---|---|---|
| 1x1 | 0.833 | 1.1 | 0.897 | 0.897 |
| 2x2 | 2.033 | 2.278 | 2.121 | 2.143 |
| 3x3 | 3.165 | 3.4 | 3.255 | 3.288 |
| 5x5 | 5.288 | 5.8 | 5.478 | 5.520 |

- Drawn radii are half each model's width, read from the `.mwm`. The spheres are the vanilla tire values, which the offroad tires share, and they keep the vanilla top speed. Radius affects no physics.
- `Radius` is set per wheel block, for every design on it. Keen's 16 large tires get it too: every GVK track suspension and Track Wheel block is hidden, so new tracks are built on Keen's tires and swapped.
- Kharak Y = sphere − link thickness − sqrt(R² + (pitch/2)²), which comes out as minus the hinge height. The 1x1 to 3x3 share one Y, so mixed 1x1 to 3x3 tracks are exact. Under a 5x5's thicker tread a smaller wheel's tread rests on its drawn wheel and sits 0.22 m (3x3) to 0.38 m (1x1) below the ground line.
- `RealTrackWheel1x1` reports Width 4.55, so it stays the biggest wheel next to a vanilla 2x2 (Width + Radius 5.447 against 5.191; offroad 5.342). A track can't fit inside a smaller wheel (Digi's alignment check).
- GVK wheels turn 3 to 7% slower than the tread moves.

### Link bunching on curves

Owner, 2026-11-22: "why do all of the links bunch closer together when bending around the wheels?". Before this fix every wheel reported the vanilla radius and the tread came down through Y, so links overlapped by 13 to 37% on curves. Picked (owner: "Shrink all radii"): every wheel reports the radius the links are drawn at, and Y drops to about 0. In game: "ok this adjustment you did is WAY better".

The price falls on Digi's own tracks, which share the wheels. His styles on Keen's tires are moved out to match (a `Merge` on `VanillaOTT_Large_*`); they now gap a little on curves, and unswapped Keen tires under them turn 16 to 42% fast.

| Style (Y) | 1x1 | 2x2 | 3x3 | 5x5 | On curves (− is a gap) |
|---|---|---|---|---|---|
| `VanillaOTT_Large_*` (Merge), Keen's tires | 0.152 | 0.219 | 0.307 | 0.219 | −14 / −10 / −9 / −4% |
| `LiftedOTT_Large_*` (Zantulo) | 0.346 | 0.423 | 0.307 | 0.219 | −34 / −19 / −9 / −4% |
| `LiftedOTT_Large_*_Offroad` | 0.346 | 0.412 | 0.308 | 0.220 | −34 / −18 / −9 / −4% |
| `LiftedOTT_Large_*_Offroad_TrackWheel` | −0.105 | −0.107 | −0.357 | −0.830 | 10 / 5 / 11 / 14% |
| `VanillaOTT_Large_*_Static_TrackWheel` | −0.271 | | −0.351 | | 25 / 10.5% |

Rejected: asking Digi for a per-design spacing radius (waits on him), shrinking only the GVK-only wheels (a track mixing them with Keen's tires gets two radii under one Y), and leaving it.

### 1x1 on mixed tracks

Under a bigger wheel's tread the 1x1 used to sink, and its old face "looks like an opened soda can" (owner, 2026-11-22). Face A replaced it on `TankWheel1x1`, `TankWheelBlock1x1` and both 1x1 doubles: a thick rim ring round a 0.30 m dish, the lug nuts on the dish floor and the hub cap 0.09 m inside the rim face, so a tread inside the wheel stays hidden. Passed in game (runbook E21). The bigger 1x1 radius (1.448) that went with it was retired by the radius fix.

### Scheme A and its limits

Picked (owner, 2026-11-22: "I really want these to play nicely with vanilla blocks"): one radius per size, so any one-size track is exact whether its wheels are GVK track wheels or swapped vanilla tires. Scheme E (one drop for every GVK size) stays the fallback; switching means new `Radius` values and drops, not new models.

- **Small bumps show through long straight runs.** Tank Tracks' ground rays stop at the link's inner face, so on a run of 3 or more links a bump lower than the tread's thickness (0.215 m; 0.458 m on 5x5) goes unseen and pokes through. A taller bump lifts the run onto it. If it shows: one tread model per size with the drop built in, or ask Digi to cast to the outer face.
- **Track wheels hover with no track:** 0.27 / 0.25 / 0.24 / 0.51 m above the ground, the gap between the drawn wheel and the sphere. Swapped Keen tires that stay swapped after their track is destroyed do the same.
- **A tire on the other kind of suspension gets the wrong style.** Tank Tracks picks the style by suspension. A Keen tire on a Short Track suspension gets the lowered tread without a swap and the tread cuts into it; a GVK track wheel under Digi's track on a Keen suspension floats.
- **The collision sphere reaches past the drawn wheel,** so a wheel can bump a wall it seems to clear, and on rough ground the tread may touch a voxel edge.
- **Mod order:** GVK_Suspension must load after 3209008231.

## Kharak Tread

Wide flat plates with a raised rubber pattern in dark worn metal, after the original Deserts of Kharak tracks (the owner's screenshot, 2026-11-22). Modeled from scratch, with nothing from the game or the Morue pack.

| Part | Spec (`KharakTread.mwm`, modeled at 3x3 size) |
|---|---|
| Plate | 2.80 m wide, 0.75 m long, 0.78 m pitch. Pivots `track_pivot1/2` at +0.456 and −0.324 m, 0.093 m up (Tank Tracks recenters them) |
| Pads and rib | 0.075 m thick, tops at 0.215 m. Per half: a top strip in the outer corner, a side strip down the outer edge, a recessed triangle, an upper diagonal pad, a lower pad and a small bottom pad. The center rib's two slots go through to the plate |
| Gaps | Every opening 0.048 m: a 0.024 m groove floor between pads and a 0.036 m margin to the plate edge and notches (the plate edge's own 12 mm bevel makes up the difference) |
| Notches | Open corner notches 0.386 m wide at the outer hinges, and a center notch |
| Hinges | Knuckles are 0.093 m radius barrels merged into the plate, flush with its underside |
| Guide horn | 0.40 m wide, 0.32 m long, 0.44 m deep, tapered; runs in the wheel's 0.57 m groove |
| Collider | `track_collider` over 0 to 0.215 m (the empty set at half size) |
| Bounding box | 2.80 x 0.655 x 0.924 m with horn and knuckles |

**Look.** Plate, knuckles and horn are `PaintedMetal_VeryDark`; pads and rib are `RubberScratched`. Tiling UVs at 0.5 UV per meter, one planar map per part along the track. Weighted normals, so flat faces shade flat beside their bevels, and a 12 mm bevel on the plate and horn edges. No edge wear, decals or hinge pins (DT1-DT3), and the tread never takes the grid's paint (T2).

| Level | Distance | What it keeps | Vertices in the file |
|---|---|---|---|
| Main | | everything | 1,748 |
| LOD1 | 10 m | plate bevels; pads without bevels; knuckles 8 steps round | 917 |
| LOD2 | 20 m | no bevels; knuckles 4 steps | 573 |
| LOD3 | 40 m | knuckles 2 steps; flat pad tops; no rib slots | 216 |
| Construction | LOD1 15 m, LOD2 40 m | the plate outline, knuckles and horn without pads or rib, so only the detail grows | |

The distances sit inside Digi's own (15 / 30 / 60 m; owner: "lets do the lod sooner for now"), since the full link costs about 2,240 vertices per meter of track, three times the Morue CV90mk4's.

| Size | SegmentScale | X | Y | Offroad Y | In game |
|---|---|---|---|---|---|
| 1x1 | 1.104, 1, 1 | .554 | −0.094 | −0.094 | 3.09 m wide, about 4 cm past each wheel face (3.01 m rim to rim) |
| 2x2 | 1.104, 1, 1 | 1.326 | −0.093 | −0.115 | as 1x1 |
| 3x3 | 1.104, 1, 1 | .757 | −0.093 | −0.126 | as 1x1 |
| 5x5 | 2.318, 2.13, 2.13 | .529 | −0.198 | −0.240 | 6.49 m wide (6.41 m rim to rim), 1.66 m pitch, 0.458 m thick |

- `_Track` styles serve the GVK track suspensions. `_Swap` adds `ReplaceWheelModel` `TankWheel<size>` and its BS2 for Keen's tires, and `_Swap_Offroad` uses the offroad Y. `_Static` (X 0, `AllowOnRotors`) serves the Track Wheel blocks, whose `OutOffset` 0.14 already puts the groove on the line.
- X is the groove line from track-wheel-swap.md. The 1x1 to 3x3 share the 3x3 tread width (2.80 m of rubber).
- Icon: `Content/Textures/Icons/KharakTread.dds` (256 px BC7 sRGB, five links on the 3x3 curve), material `KharakTread_Icon`.
- Source: scenes `KharakTread` and `KharakTread_Construction` in `Source/KharakTread/KharakTread.blend`.

## Kharak Double Tread

Twin tracks like those on the bigger Deserts of Kharak cruisers: two road wheels side by side under one tread with two bands, just under 5 m across so it fits between blocks. Every style swaps the wheel model, so a wheel looks double only on a track built with this design, and it keeps its tire's collision, grip and radius (owner: "I'm ok with it being mostly visual").

| Part | Spec |
|---|---|
| `TankWheelDouble1x1`, `2x2`, `3x3` | 4.78 m: two 2.24 m bands (the single wheel at 0.80 width, each with its own 0.45 m groove) and a 0.30 m plain steel channel between them |
| `TankWheelDouble5x5` | The 10 m double (DD2): 9.78 m, 4.64 m bands and a 0.50 m channel |
| `TankWheelBlockDouble1x1`, `3x3` | The double on the Track Wheel block's post and flange, centered 2.5 m out from the flange, so it stays inside the 1x1x2 or 3x3x2 block |
| Link `KharakDoubleTread` | Two Kharak bands at 0.864 width (2.42 m each), 1.27 m either side of center, 4.96 m in all; the Kharak pitch and pivots; one collider over both bands |
| Tread in game | 4.856 m (SegmentScale 0.979, 1, 1), just inside the 4.86 m rim faces; 5x5 9.856 m (1.987, 2.13, 2.13) |

- **Placement (DD3).** The 5 m doubles span 2.5 to 7.5 m from the mounting face and the 10 m double 5 to 15 m, so each wheel fills whole cells. The meshes sit 0.137 m nearer the hull than the single groove line, so X is the single style's X less that: .417 / 1.188 / .613 / .401, and −.14 / −.132 on the Track Wheel blocks. Y matches the Kharak Tread. Keen's 5x5 sits 0.13 m off the Lifted Short line, so its 10 m double is about 0.1 m off the cells.
- **Levels.** Each double link level is two single links one level down (Main from LOD1, LOD1 from LOD2, LOD2 from LOD3, LOD3 the LOD3 plate and pads only), so it costs about two single links at the next LOD. LODs 10 / 20 / 40 m; construction model `KharakDoubleTread_Construction` at 15 / 40 m. The wheels have Main and LOD1-3 at 25 / 50 / 100 m, BS1 (the bare steel wheel) for construction, no collision, and the single wheel's dummies.
- **Styles.** Swap styles only: `_Swap` and `_Swap_Offroad` for every size, plus `_1x1_Static` and `_3x3_Static`. Every `[Blocks]` line that lists a Kharak Tread style lists the double too; Short Track and Lifted Short Track get `_Swap`, so their track wheels swap to the double.
- Icon: `KharakDoubleTread.dds`, material `KharakDoubleTread_Icon`.
- Source: wheels in `Source/TrackWheels/TrackWheelStudy.blend`, the link in `KharakTread.blend`.

## Rubber Track

A pure rubber track in place of Morue's CV90 Mk4 (owner, 2026-11-22: "I believe it can replace the CV90 Mk4"): rubber lugs in the style of Keen's tire tread, overhanging the wheels well past their tread, on the single track wheels only. Modeled from scratch to exact dimensions; the version cut from Keen's tire mesh was dropped ("start from scratch honestly").

| Part | Small link `RubberTrack` (1x1 to 3x3) | 5x5 link `RubberTrack5x5` |
|---|---|---|
| Width | 4.00 m: 0.6 m past the 2.80 m tread on each side | 8.52 m: 1.28 m past the 5.96 m tread on each side |
| Thickness | 0.30 m as modeled; SegmentScale Y makes it 0.15 / 0.195 / 0.24 m on 1x1 / 2x2 / 3x3 | 0.42 m, at scale 1 |
| Pitch | 0.90 m, pivots ±0.45 m; the noses overlap 0.23 m | 1.25 m, pivots ±0.625 m, on a 1.10 m lug; the noses overlap 0.31 m |
| Underside | Flat across the wheel's 2.80 m tread, then a lip 0.25 m deep over each rim, past a 5 cm gap and a 6 cm chamfer | Flat across the 5.96 m tread, with the lips over the 5x5 rims |
| Guide horn | 0.40 m wide, 0.32 m long, 0.355 m below the inner face, in the wheel groove | In the 5x5 groove, its tip where the scaled small link's was |
| Pockets | Two in the back edge, top edges 0.55 to 1.26 m off center, 15.5 cm deep | Four, staggered: the inner pair on the back edge 0.75 m off center, the outer pair on the front |
| Corner notches | Four, from 1.55 m out through the shoulder, as deep as the pockets | Four |
| Bevel | 3 cm | 4 cm |

**Shape.**
- **Profile:** a flat crown, double-chamfered shoulders and the recessed underside. Each end is a full-width triangular nose that tucks inside the next link, so a curve shows no gap. The nose underside rises 2° to its tip, so two noses cross instead of sharing a plane.
- **Sides:** the middle 0.40 m of each side bulges out 0.115 m on 45° ramps. Past that step the side angles in about 3° through the nose, so neighbors never share a side face.
- **Knob:** each corner of the middle knob is one sloped facet down to the side step, and a 45° chamfer runs under the knob (14 cm on the small link, 20 cm on the 5x5).
- **Notches:** each pocket's back slope is the corner notch's back wall (45° on the small link, about 48° on the 5x5), with its top edge level with the corner notches'.
- **Bevel:** one round bevel, 3 segments, on every top and outer edge sharper than 30°. Each edge has its own limit from the edges and faces it meets (`bevel_limits()`), so every top edge gets an unbroken chamfer; Blender's own clamp shrinks the whole bevel to its tightest spot. The underside and inner lips stay sharp. Shading: smooth to 60°, weighted normals with face strength.
- **Checks on every level:** no coplanar faces between neighbors, straight or bent round a wheel; no zero-area or bad-UV faces.

**Look.** Keen's tire split: `RubberWheels` on the tops and underside, `RubberWheelsScratched` on the bevel faces, `RubberDry` on the walls, meaning any face steeper than about 53° (`rubber_split()`). The LODs have no bevels, so they carry `RubberWheels` and `RubberDry`. The texture is turned 90° so its streaks run along the track, as they run round Keen's tires. Along the track and up it is 0.5 UV per meter (Keen's large tires: 0.44 to 0.47). Keen's rubber textures don't tile, so across the track the small link is stretched to one repeat (0.245 UV per meter) with no seam, and each half of the 5x5 link is one repeat (0.2325) with one seam down the center. No new textures.

| Level | What it keeps | Small link | 5x5 link | Triangles, small / 5x5 |
|---|---|---|---|---|
| Main | everything | | | |
| LOD1 | no bevels | 10 m | 20 m | 304 / 340 |
| LOD2 | no corner notches; the middle pockets stay | 30 m | 60 m | 292 / 324 |
| LOD3 | no pockets, no side steps | 60 m | 120 m | 220 / 220 |
| Construction | the top 8 cm lower (0.11 m on 5x5), no notches; LOD1 and LOD2 | 10 / 30 m | 20 / 60 m | |

The 5x5 distances are Keen's `Wheel5x5`. The small link's are set by eye from Keen's `Wheel1x1` (5 / 20 / 60 m; owner: "5 is too close for LOD1, make that 10, then make LOD2 30").

**Placement.** A link thinner than the space between the drawn wheel and the collision sphere sits halfway (owner pick): its inner face is at r0 = (sphere − thickness + drawn radius) / 2, and Y = r0 − sqrt(R² + (pitch/2)²). The 3x3's 0.24 m is more than its 0.235 m space, so it sits on the ground line (r0 = sphere − 0.24). The 5x5 link sits 4.6 cm off the wheel and 4.6 cm into the ground. The radii suit the Kharak Tread, so these links overlap on curves by 3.8% on 1x1 and 1.5% or less on the rest; a 1x1 link spans 53° of its wheel.

| Size | Link | SegmentScale | X | Y | Offroad Y |
|---|---|---|---|---|---|
| 1x1 | `RubberTrack` | 1, 0.50, 1 | .554 | −0.113 | −0.113 |
| 2x2 | `RubberTrack` | 1, 0.65, 1 | 1.326 | −0.109 | −0.131 |
| 3x3 | `RubberTrack` | 1, 0.80, 1 | .757 | −0.125 | −0.159 |
| 5x5 | `RubberTrack5x5` | 1, 1, 1 | .529 | −0.179 | −0.221 |

- The same style set as the Kharak Tread, with its X, so the horn sits in the groove. `_Static` uses X 0.
- The design is on every large-grid `[Blocks]` line that lists a Kharak Tread style, with the same kind of style.
- Icon: `Content/Textures/Icons/RubberTrack.dds` (256 px BC7 sRGB), five current links on the 3x3 curve, lit from behind and seen from higher up so the pockets read at icon size (`Source/RubberTread/scripts/rt_icon.py`, variant v7), material `RubberTrack_Icon`.
- Source: `Source/RubberTread/scripts/rt_build.py` and `rt5_build.py` rebuild every level of `RubberTrack.blend` and `RubberTrack5x5.blend`, with SEUT scenes `RubberTrack`, `RubberTrack_Construction`, `RubberTrack5x5` and `RubberTrack5x5_Construction`. The `*_before_*.blend` checkpoints sit beside them.
- **Rejected:** a band joining the lugs, which buried the side steps ("its like they are all stuck on fat slabs, all of the side detail is gone"; kept as `*_band_rejected.blend`); the 3x3 link scaled 2.13x for the 5x5, which read cartoonish and made the rover look small; mirrored UVs across the link; seamless copies of Keen's rubber maps shipped in the mod; `RubberScratched` on the whole link.

## Next design: Kharak Tread Mk II (plan, 2026-11-23)

The second T6 style, from the owner's mockup of a few joined links (`Source/KharakTread/reference/kharak_tread_v2_mockup_owner_2026-11-23.png`). The reading below is confirmed (owner, 2026-11-23: "Yes, that's it"; `Source/KharakTread/review/v2_mockup_reading.png`). Sizes assume a 2.80 m plate, as the Kharak Tread:

| Part | Reading |
|---|---|
| Plate | 2.80 x 0.68 m, pitch 0.74 m, a 6 cm gap between links |
| Center arrowhead pad | A 0.71 m flat tip, 45° shoulders, a 1.01 m flat back edge, 0.65 m long. Its front 0.25 m reaches past the plate, over the gap, into a notch in the link ahead |
| Upper side bars | 0.15 m deep, out to 6 cm from the plate edge; each joins the arrowhead's shoulder, split from it by a 2 cm slot at 45° |
| Lower side bars | 0.17 m deep, 7 cm behind the upper ones; each inner end turns 45° into the arrowhead's back corner |
| Plain plate | 0.23 m at the front corners; 6 cm margins at the sides and back |

A new design next to the Kharak Tread, which stays as it is (owner, 2026-11-23: "New design"), named "Kharak Tread Mk II", id `KharakTreadMk2_Large` (owner pick, 2026-11-23). Materials: a dark metal plate with the pads in Keen's tire rubbers, split as on the Rubber Track (owner pick, 2026-11-23: "Keen's rubber split"). No visible hinge: plain plates meet across the gap, with the tongue over the joint (owner pick, 2026-11-23); a round bar runs through the plate under the tongue's front piece (hinge bar, below). Guide horn: the Kharak Tread's (owner pick, 2026-11-23). Single track wheels only, no double version (owner pick, 2026-11-23).

The 5x5 gets its own full-size link, the pattern kept at the 3x3's scale (owner pick, 2026-11-23); its layout is settled from renders before modelling.

Thickness: pads raised to about 0.10 m on a 0.14 m plate, about 0.24 m in all (owner pick, 2026-11-23: "Taller pads"). With the outer face on the collision sphere, the plate's underside sits 2.7 cm off the 1x1 wheel, 0.5 cm off the 2x2 and 0.5 cm into the 3x3, as the Rubber Track's 3x3 link does.

The tongue is picked from renders (owner, 2026-11-23: "Show me renders"). Tongue A is rubber only and lies on the plate ahead, with the cut-out drawn in front of its tip. Tongue B is plate and pad together, in a notch of the tongue's shape 4 cm wider all round; that leaves a 3.9 cm strip of plate between the notch and the arrowhead's back edge. Tongue C is B with the tongue's front piece on the link ahead (owner, 2026-11-23: "I like B, but that looks bad when its curving around the 1x1 barrel. I wonder if maybe faking it by attaching part of the tongue to the link ahead"): the arrowhead is cut at the hinge line, half a pitch ahead of the link's center, and the piece ahead of the cut sits in the next link's notch and turns with it. On a wheel curve tongues A and B lift off the link ahead; C's cut opens instead (blockout, measured at the tip and at the cut):

| Wheel | Turn per link | Tongue A: tip off the next plate | Tongue B: tip rise in its 14 cm notch | Tongue C: cut opening at the outer face; bottom corner into the piece ahead |
|---|---|---|---|---|
| 1x1 | 44.6° | 14.9 cm | 18.9 cm, clear of the notch | 9.2 cm; 7.7 cm |
| 2x2 | 19.7° | 7.4 cm | 8.2 cm | 4.2 cm; 3.9 cm |
| 3x3 | 12.9° | 5.0 cm | 5.3 cm | 2.8 cm; 2.6 cm |

**Picked: tongue C with a knuckle** (owner, 2026-11-23: "yes C tip on link ahead. I think the back of the tongue tip would extend back and maybe curve downward so the curve is hidden when the link is straight but bridges the gap when around the wheel"). The knuckle is a sector of a cylinder round the hinge axis on the tip piece's back: 0.123 m radius about the hinge, 0.113 m up the link (the hinge sits 0.110 m up on the 1x1 and 0.116 m on the 3x3), reaching 46° back. On a straight run it stays 4 mm inside the arrowhead behind. On a wheel the cut opens round the same axis, so the knuckle's arc spans the opening. Tried as tongue D: a back curve of 0.9 m radius (owner, 2026-11-23: "a back curve with a MUCH larger radius than what you added, like the radius of the 1x1"). It hides as well on a straight run, but on a wheel it stands above the outer face of the link behind by 1.6 cm (3x3), 4.2 cm (2x2) and 19 cm (1x1). The link behind turns about the hinge, 12.7 cm under the outer face, so only a curve round the hinge axis meets it flush. The owner kept the knuckle (owner pick, 2026-11-23: "C: knuckle"). Slots: 3 cm across (owner pick, 2026-11-23). Still open: under the hinge, the cut's bottom corner runs 2.6 cm (3x3) to 7.7 cm (1x1) into the tip piece.

**Hinge bar, accepted** (owner, 2026-11-24: "Yes now you got it"; first asked for 2026-11-23: "I don't like the small tab that appears to hold onto the front of the arrowhead tongue, I want it to be a round bar that bridges the gap like a wide hinge that the arrowhead tongue holds on to", "a long horizontal bar"). The tab was the guide horn, seen through the gap in front of the tongue's tip. A first bar filled that gap; the owner wanted it further back (owner, 2026-11-24: "No I wanted that further back like the bar I had in my original drawing that went across under the tongue"). A pin on the hinge axis, across the gap between links, went too far; the owner picked halfway between the first bar and the joint (owner pick, 2026-11-24: "Half way between 1 and 2"). The bar sits 0.236 m behind the link's center, under the tongue's front piece, and runs through the metal plate rather than into the rubber (owner, 2026-11-24: "Roughly right place. It should be connected deep in at the metal plate, not at the rubber pad"). It is centered in the plate's 0.14 m depth, 9 cm across and 1.20 m long. It shows only where it crosses the 4 cm gaps beside the tongue, and both ends stay 4 cm inside the plate beyond them. In the blockout it is a darker steel than the plate (`KT2_bar`). With the first bar gone the horn showed again through the gap ahead of the tip, so that gap now has a 2 cm floor at the plate's underside and stays 12 cm deep (accepted with the bar). The tip piece and the notch are on the same link, so the floor never moves against either. Board: `review/board_hinge.png` (`kt2_boards.py hinge`), with the 5x5 link's bar.

On the 1x1 the plates' inner corners also run 2.8 cm into each other, with any tongue; on the 2x2 and 3x3 they don't meet. On the curve, the plate underside sits inside the drawn tire by 2.6 cm (3x3), 2.7 cm (2x2) and 4.6 cm (1x1); that comes from Tank Tracks' layout, not from the tongue.

Blockout plan (round 1):
1. Done 2026-11-23: `Source/KharakTreadMk2/scripts/kt2_build.py` builds the small link at 3x3 size with each tongue in `Source/KharakTreadMk2/KharakTreadMk2.blend` (collections `KT2_A` to `KT2_D`; C is the picked one).
2. Done 2026-11-23: `kt2_review.py` lays the links out as Tank Tracks does, renders them and prints the joint numbers above; `kt2_boards.py` builds the boards in `Source/KharakTreadMk2/review/` (`board_top.png`, `board_3x3.png` and `board_1x1.png` for A and B; the same names with `_BC` and `_CD` for those pairs). The top view's outlines match the mockup's.
3. Done 2026-11-23: tongue C with its knuckle, and 3 cm slots (above; board `review/board_C.png`).
4. Done 2026-11-24: the 5x5 link's layout (G6: S2X with corner lugs and one 6.4 cm gap, below) and the hinge bar with the floored gap on both links (above; board `review/board_hinge.png`).
5. Next, each with the owner's yes: detailing, LODs and export. Nothing is exported before the blockout is signed off.

### Mk II 5x5 link (plan, 2026-11-23)

The 5x5 track wheel (measured from `TankWheel5x5`): drawn radius 5.288 m, collision sphere 5.8 m, reported radius 5.478 m. Its rubber is 5.96 m wide, in two 2.38 m bands on either side of a 1.21 m groove.

The 5x5 link is the small link scaled up 2.13x (5.96 / 2.80) in width and pitch (owner, 2026-11-23: "just scaling up the small one and adding a few details would look a lot better, maybe making the arrowhead wider so it doesnt look too flmsy, maybe do 3 side cuts instead of 2"). This replaces the first plan, which kept the small link's pads and slots at their size. The owner rejected all four of its layouts (one or two arrowheads across, one or two rows per link): "all of those look absolutely awful". The pattern was too small for the link, the 0.38 m plate under 0.10 m pads read as a slab, and the long bars looked stripy.

On every option:
- **5.96 m wide, pitch 1.57 m**: 16.3° per link on the 5x5, 22 links round the wheel (the Kharak Tread's 5x5 has 21).
- **0.48 m thick: 0.20 m pads on a 0.28 m plate**, the small link's proportions, with the outer face on the collision sphere. Mid-link the plate underside sits 2.4 cm inside the drawn tire.
- **Tongue C with its knuckle**, 6.4 cm slots (the small link's 3 cm, scaled), and the Kharak Tread's 5x5 horn in the groove, X .529 as the Kharak 5x5 style. At each joint the cut opens 7.5 cm at the outer face, which the knuckle fills; its bottom corner runs 6.0 cm into the piece ahead.
- On a mixed track the 5x5 style wraps the smaller wheels too: 27° per link on a 3x3, 41° on a 2x2 and 82° on a 1x1. The knuckle's 46° covers all but the 1x1.

| Option | Arrowhead tip | Bars a side |
|---|---|---|
| S1 | 1.57 m across, the small link's, scaled | Two, 0.32 and 0.37 m wide, with a 15 cm gap |
| S2 | 2.10 m across; the bars are 0.27 m shorter | Two, as S1 |
| S3 | 2.10 m across, as S2 | Three, 0.21 m wide, with 10 cm gaps |

`kt2_5x5.py` builds the options (collections `KT2_S1` to `KT2_S3` under `KT5_blockout`) and renders them on `TankWheel5x5`; `kt2_boards.py 5x5` builds `review/board_5x5_top.png` and `board_5x5_wheel.png`.

**Picked: S2** (owner pick, 2026-11-23: "S2"): the wider arrowhead, with two bars a side as on the small link.

**Picked: S2X** (owner, 2026-11-23: "looks right"): S2 with each side slot run on up 0.15 m further and then across the arrowhead at the slots' 6.4 cm width, so the rubber splits into two lugs (owner, 2026-11-23: "have it go up a little more and cut all the way across so it spits the arrowhead into 2 large lugs"). The front lug is the tip with the upper bars; the rear lug is the arrowhead's core with the lower bars. The cut's top edge is 0.41 m ahead of the plate center and 0.37 m behind the hinge line. Board: `review/board_5x5_cut.png` (`kt2_boards.py 5x5cut`). It has the small link's hinge bar, scaled: 19 cm across, 3.10 m long, crossing 8.5 cm gaps; the gap in front of the tip has a 4 cm floor.

**Corner lugs and one gap: picked G6** (owner pick, 2026-11-24: "G6"; asked for 2026-11-24: "On the 5x5 add a 3rd but disconnected trapezoid lug in the vacant grey space in front of the two side wings. Then make all lugs with an equal gap between lugs and to the of the plate except the tongue"). S2X gets a trapezoid lug in each plain front corner, in front of the upper bar, its inner side at 45° along the arrowhead's shoulder. One gap then separates every two lugs (between the bars, across the 45° slot and across the cut) and each lug from the plate's edges: front, sides, back, and the notch round the tongue. The tongue keeps its own 8.5 cm gap. The upper bar's top stays where it was; the bars keep their height ratio and the arms their width ratio.

| Option | Gap | Changes from S2X |
|---|---|---|
| G6 | 6.4 cm, the slot's width | Plate margins shrink from 12.8 cm; the bars grow; corner lugs 0.36 m deep |
| G13 | 12.8 cm, the plate margin's width | The slot and the cut double; corner lugs 0.23 m deep |

`kt2_5x5.py` builds both (`KT2_G6`, `KT2_G13`); board `review/board_5x5_even.png` (`kt2_boards.py 5x5even`). G6 is the 5x5 link from here on. Next, with the owner's yes: the details (owner: "adding a few details"). Nothing is exported before sign-off.

### Mk II detailing (plan, 2026-11-24)

The owner asked to start the details (owner, 2026-11-24: "commit then work on details"). Both links get the same treatment, with fasteners at one real size on both (lesson: "Don't scale up a link"). The blockout costs 340 triangles (small link) and 376 (5x5), far under the Kharak Tread's 1,748 vertices, so the details fit.

**Finish, on every option** (from earlier picks):
- Materials: the plate, knuckle and horn in `PaintedMetal_VeryDark`; the rubber in Keen's tire split as on the Rubber Track (`RubberWheels` tops, `RubberWheelsScratched` bevels, `RubberDry` walls); the hinge bar in bare steel. Tiling UVs at 0.5 UV per meter, rubber turned to run along the track.
- Bevels on the rubber's top edges and the plate's outer edges, sized so every gap still measures its picked width at the opening (the owner's rule): about 6 mm on the small link's rubber, so its 3 cm slots keep a 1.8 cm floor, and 13 mm on the 5x5's. No bevels under the pads or on the underside.
- Weighted normals; smooth shading on the knuckle and bar.

**Details offered** (board `review/board_details.png`, `kt2_sketch.py`):

| Detail | Small link | 5x5 link | Triangles, small / 5x5 |
|---|---|---|---|
| Pad bolts: sunken heads in 6 cm counterbores, holding the rubber to the plate, about 0.2 m in from each lug's ends | 6: two in the arrowhead, one near each bar's outer end | 18: four on each arrowhead piece, two on each bar, one on each corner lug | about 240 / 720 |
| Sipes: one narrow cut across the middle of each side bar, half the rubber's depth | 4, 1.5 cm wide | 4, 3.2 cm wide | about 100 / 100 |
| Side pockets: a recessed pocket with 45° corners in each end face of the plate, the face seen from beside the vehicle | 0.48 x 0.07 m, 3 cm deep | the same, scaled 2.13x | about 40 / 40 |

Not offered: edge wear and decals (none on the Kharak Tread, DT1 and DT2, and little metal shows), visible hinge pins (owner pick, 2026-11-23: no visible hinge), and a lightening hole in the guide horn, which sits hidden in the wheel's groove.

Order after the pick: the finish and the picked details on both links, renders for review, then LODs and export.

On hold: the owner wants more blockout work first and will send a mockup (owner, 2026-11-24: "I want to work on the block out more. I'll send a mock up"). The options above wait for it.

### Mk II round 3: two equal pads (reading and blockout, 2026-11-24)

The owner's markup over a picture of a track link (`Source/KharakTread/reference/kharak_tread_v3_mockup_owner_2026-11-24.webp`, kept local): "green lines are the pads, red is the plate, blue is the hinge rod that connects them". It is AI concept art ("the dimensions are not perfect, it is a concept"), so the owner's rules and round 2's sizes win over its pixels:
- "I want to keep the visual trick with the tongue attached to the next tread, but it will just be the backplate instead of backplate and rubber".
- "I want the rubber pads to be equal in width", and "the gap between the pads should be equal all the way across too".
- "the ends of the plate are beveled all the way around with some detail lines".

Reading (board `review/v3_reading.png`, `kt2_v3_reading.py`; it copies only the owner's colored lines, not the picture):

| Part | Reading |
|---|---|
| Plate | 2.80 x 0.68 m, pitch 0.736 m, as round 2 |
| Plate ends | Part of the plate (owner: "the end caps need to be better integrated into the plate, they have extra chamfers around the wider base that shouldn't be there"). Each end is a truncated prism over the last 9 cm: its front and back taper in 5 cm and its top and bottom 2 cm, as flat faces (owner: "it should be beveled on all 4 sides so the end cap is a truncated prism") |
| Tongue | Metal only, 0.14 m thick: 1.03 m across its front, 45° sides, 0.25 m long (to 0.5925 m from center, as round 2). The notch round it keeps the 4 cm gap. The plate itself stops straight across its front edge (0.34 m); the whole tongue is the slice of the next link, under the front pad's middle and shoulders, which overhang it (owner, in game: "The metal plate should just go straight across and leave the rubber tread tongue and shoulders as overhang", since the plate's strip in front of its edge stuck out on a wheel) |
| Pads | Two chevrons, both 19 cm wide, with one 5 cm gap between them all the way across. The same gap to the back edge, the plate's ends and the notch. The front pad's shoulders rise 5 cm up the tongue's sides, 24 cm long, to 0.43 m from center (owner: "the forward pad is missing the shoulders"; pick "Seam back, shoulders end on it") |
| Tongue seam | Straight across the tongue along the front pad's middle front edge, 0.85 cm ahead of the hinge. The piece in front (the slice) belongs to the next link, as with tongue C (owner: "you could make the tongue slice larger so it takes more parts of the trailing tread to help improve the bend seam"; then "make the seam here all the way across, straight line, its fine if the rubber part of the tread looks like it is lifting off a little on a really tight bend"). The shoulders' 5 cm rise sits over the slice, so bent, a gap opens under their front edge: 1.4 cm on the 3x3, 2.1 cm on the 2x2, 4.9 cm on the 1x1 |
| Knuckle | One knuckle on the slice, straight across the tongue. Owner, of round 2's knuckle: "the curve is hidden when the track is straight, and hides the split/gap when it is wrapped around a wheel"; then, drawing on the joint section (`review/seam_markup_owner_2026-11-24.png`): "make the tongue slice knuckle straight across at the center of hinge point, and add a more gradual curve that intersects with the trailing plate". The slice and knuckle are one solid, its ends on the tongue's 45° sides all the way back. Its top is an arc of 10.5 cm radius from the slice's top at the seam, turning 80° to end 9.5 cm behind the hinge and 5.3 cm up; from there its back runs straight down to the underside 1 cm behind the plate's front edge, under that edge's chamfer, so no gap shows from below (owner, in game: "the radius is a little tighter and extends further back", then "tighter and angles even further into the back tread", "extend the bottom of the knuckle to close that gap"). Straight, it is hidden in the plate behind; bent, it fills the split, and what rises behind the hinge sits inside the front pad |
| Hinge rod | 9 cm across, 0.51 m from center; it shows only in the gaps beside the tongue. The notch's gap has no floor, so only the rod holds the links together (owner: "remove that, its supposed to look like the rod hinge is holding it together only") |

The pads come out within 3 cm of the drawn lines (front pad top 0.377 m against about 0.39; rear pad bottom −0.290 m against about −0.32). The round 2 arrowhead, side bars and slots go; the hinge rod moves 1 cm forward.

A first blockout curved the seam round the hinge axis, so the plate behind ended in a round knob. The owner turned it down: "you had this perfect on the prior design. You are overthinking it now with these perfectly grooved cutouts. Its just supposed to extend into the tread behind to hide gap when its around a wheel".

Blockout: `scripts/kt2_r3.py` with the outlines in `kt2_r3_geom.py`, collection `KT2_R3` under `KT3_blockout` in `KharakTreadMk2.blend`. Board `review/board_r3.png` (`kt2_boards.py r3`); the joint from the side, straight and bent, `review/seam_section.png` (`kt2_seam_sketch.py`).

Finish (`kt2_r3_detail.py`, run after the blockout):
- Rubber as the Rubber Track: Keen's tire split (`RubberWheels` tops, `RubberWheelsScratched` bevels, `RubberDry` walls), one 3 cm rounded bevel on the top edges and the outside upright corners, none on the bottoms or inside corners (owner: "no chamfers on the bottom sides of the rubber pads"), streaks along the track.
- Plate, slice and horn in `PaintedMetal_Colorable`, with a 1 cm 45° chamfer on the outside edges, none on the inside corners, on the knuckle where it meets the plate behind, or on the slice's top edges under the shoulders (owner: "don't chamfer the knuckle where it intersects with the trailing tread", "chamfer on the top side needs to end where it overlaps with the rubber tread"). Box UVs at 0.5 UV per meter. The chamfers were tried in `PaintedMetalScratched_Colorable`, but its scratches never show: it is 100% paintable, and no tiling worn steel takes paint (owner pick: "worn steel if it is colorable", so the chamfers are painted too).
- End caps (the last 9 cm of each plate end, |x| > 1.31 m) in unpainted `PaintedMetal_VeryDark`, their chamfers in `PaintedMetalScratched_VeryDark`, which shows its scratches since it takes no paint (owner: "I want to make those end caps a dark metal with scratched metal chamfers").
- Seam decal round each end cap where the dark steel meets the paint (`kt2_r3_seam.py`, run after the finish; owner: "add a seam decal all the way around to split the line between the metal end cap and the painted metal"): Atlas4 piece 3 in `Atlas4_Colorable` so it takes some of the paint (owner: "i want it to take some of the paint color"; first tried in `Atlas4_VeryDark`), 16 mm wide, centred on the material border, one closed loop over the top, front, bottom, back and the chamfers, rows every 2.5 cm, 1.5 mm off the surface, V towards the cap on both ends.
- Hinge rod in `PaintedMetal_VeryDark`, the Kharak Tread's metal.

In-game test (runbook E32): `kt2_r3_export.py` exports `KharakTreadMk2.mwm` (main model only, no LODs or construction model yet), used by the test design "Kharak Tread Mk II (test)" (`KharakTreadMk2_Large`), whose styles are the Kharak Tread's with that model and Y 2 cm lower (4.3 cm on the 5x5), as the Mk II hinges sit 0.113 m up instead of 0.093. Owner, in game 2026-11-24: "the tread looks good so far".

## [Blocks]

| Blocks | Styles |
|---|---|
| Short Track and Lifted Short Track (GVK track wheels) | `LiftedOTT_Large_<size>_Offroad_TrackWheel`, Kharak `_Track`, Double `_Swap`, Rubber `_Track` |
| Lifted Short | `LiftedOTT_Large_<size>_Offroad` and the three `_Swap` |
| Offroad Lifted Short and Offroad Lifted | `LiftedOTT_Large_<size>_Offroad` and the three `_Swap_Offroad` |
| Lifted (Zantulo) | `LiftedOTT_Large_<size>` and the three `_Swap` |
| Keen's Suspension and Short Suspension | The three `_Swap`; Digi's vanilla track comes from his own pack |
| Keen's Offroad and Offroad Short Suspension | The three `_Swap_Offroad` |
| Track Wheel and Short Track Wheel 1x1 and 3x3 | `VanillaOTT_Large_<size>_Static_TrackWheel` and the three `_Static` |
| Small grid (`SG_*`) | `LiftedOTT_Small_*` only, until T4 |

Keen's suspension SBC stays untouched.

## Lessons for the next design

From the link reviews:
- **Trace the owner's markup over the concept art.** AI-made art sets the layout, not the proportions ("the proportions may not be exact, that was concept art made by AI").
- **Judge a link at the wheel size it is seen on.** On the 3x3 the owner picked a 0.75 m link over a CV90-sized 0.49 m one.
- **Measure a gap at its opening, bevels included.** An edge margin equal to the groove between two bevelled pads reads narrower, because the plate edge has its own bevel.
- **No part under about 0.08 m wide and no chamfer slivers** ("I don't like these very skinny bits").
- **No bevels under raised parts.** A pad on a plate has no bottom face, so it meets the plate with a sharp corner; bevels underneath are triangles nobody sees.
- **Merge each hinge knuckle into the plate as one rounded profile.** Lug blocks, steps and seams there only add triangles.
- **Don't scale up a link for the biggest wheel.** The 2.13x Rubber Track link read cartoonish on the 5x5. A full-size model with finer detail and the same texture density makes the wheel look as big as it is; the same goes for the wheels' bolts and texture scale.

From building and testing:
- **Build only what the owner picked.** The Rubber Track band came from reading "I like 1.45" as a pick for it, and was reverted ("so you added this band without asking me"). Offer side-by-side renders and let the owner choose.
- **Keep neighbor links from sharing a face.** Overlapping noses and sides flicker where they share a plane. Angle them a few degrees, and check every level straight and bent round a wheel.
- **Keen's rubber textures don't tile.** Each shows a hard line where it wraps, so keep each link inside one tile or put the seam where it hides, and run the texture the way Keen's tires do.
- **Put the drop in the radius, not in Y.** Y moves links without changing their spacing, so a large Y bunches them on curves.
- **Dummies after every wheel export.** `TrackWheelStudy.blend` holds no empties, so every SEUT export of a suspension wheel needs Keen's dummies copied back in (`wheel` at y −1.901 / −1.129 / −1.711 / −4.071 on the 1x1 / 2x2 / 3x3 / 5x5, singles and doubles). A 2026-11-22 export that skipped it left the wheels swinging about the suspension (owner: "they are all flopping around"). Read the dummies back before deploying (se-dev-seut `scripts/mwm_dummies.py`, three per wheel), and restart the game after any dummy change: the game loads dummies once.
- **Set the `track_collider` empty at half size.** Full size made runs float 0.11 m (0.23 m on 5x5) over a bump.
- **Thin a link per size with `SegmentScale` Y.** It works, and the horn and lips thin with it.

## Decisions

- **T1, name:** "Kharak Tread", ids `KharakTread_Large` / `KharakTread_Small`.
- **T2, paint:** fixed dark painted metal with scratched rubber pads; the tread never takes the grid's paint.
- **T3, Keen's suspensions:** Keen's large-grid suspensions get GVK swap styles next to Digi's vanilla track; their SBC stays untouched. Offroad tires use the offroad Y (D5 in track-wheel-swap.md).
- **T4, small grid: later** (owner: "those probably need new track wheel models too"), together with D9 in track-wheel-swap.md. Until then the `SG_*` blocks and Keen's small-grid suspensions offer only Digi's vanilla track, and small-grid tracks on Morue designs disappear.
- **T5, 5x5 link:** the Kharak designs scale one link 2.13x along and in thickness; the Rubber Track has its own 5x5 link.
- **T6, more styles:** two more GVK designs once the Kharak ones pass every test. First the Rubber Track; the second is next.
- **DT1-DT3:** no edge wear, decals or hinge pins on the Kharak Tread.
- **DD1, widths:** 2.24 m bands round the groove centers, a 0.30 m channel, so the tread hangs past the wheel ("so the tread appears to have some more overhang"), then cut to end inside the rim faces.
- **DD2, 5x5 double:** 10 m wide ("its double wide would just be a 10m width").
- **DD3, placement:** between the grid line at the mount and the line two cells (four on the 5x5) out.
- **DD4, the gap between the wheels:** a plain steel channel ("doesn't need those extra bevels and the black rubber wear strips").
- **Scheme A** for radii; then **all radii shrunk** to stop the bunching.
- **Rubber Track:** thickness "A", placed halfway; overhang 0.6 m (1.28 m on 5x5); spacing +13.5%; bevel and Keen's rubber split; LODs as above.
