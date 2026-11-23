# GVK Suspension

The suspensions, wheels and tank tracks of the **GV: Deserts of Kharak (GVK)** server: lifted and short suspensions, real-wheel and track wheel blocks, and the Kharak Tread and Kharak Double Tread for Digi's Tank Tracks. Workshop item 2780232704.

## Philosophy
- **Vanilla suspension models stay untouched.** Track wheels are shown by swapping the wheel model per track style, never by editing a suspension block.
- **One track, one tread line.** Every GVK wheel size reports a radius that lets one tread drop fit a mixed track.
- **Visual swaps keep the original tire.** A swapped wheel keeps its tire's collision, grip and radius, so a swap never changes how a vehicle drives.
- **Few blocks, many looks.** The track look is picked in the Tank Tracks builder, not with extra suspension blocks.

## Requirements
- Digi's Tank Tracks: Framework & API (3208995513), Builder (3209005014) and Tank Tracks over Vanilla Wheels (3209008231). The wheel swap needs the Framework's swap crash fix ([gvk-treads.md](Docs/design/gvk-treads.md)).
- No re-uploads.

## For other modders
- `Content/Data/TankTracks.ini` is a working Tank Tracks config: track designs, per-size styles with `ReplaceWheelModel`, a `Merge` entry on one of Digi's own tracks, and `[Blocks]` lines for Keen's suspensions. How each value was worked out: [gvk-treads.md](Docs/design/gvk-treads.md).
- G menu (read in the game code, `MyGuiScreenToolbarConfigBase`): the Home tab draws one icon per variant group (its first listed block) and places it from `BlockPositions.sbc` by that block's `BlockPairName`; a block with no position fills the first empty slot anywhere. A category tab draws every block it lists, so list only each group's first block, with `StrictSearch` true, to get one icon with the + mark. `GuiVisible` false hides a block from neither.
- A wheel swap model must keep the wheel's diameter and its `wheel` dummy, or the track floats or sinks ([track-wheel-swap.md](Docs/design/track-wheel-swap.md)).

## Folder map
| Path | What is in it |
| --- | --- |
| `Content/Data/` | Block, category, variant group, Home tab position and icon SBCs, and `TankTracks.ini` |
| `Content/Models/` | Suspension, wheel, track wheel and tread models |
| `Content/Textures/` | Block and track design icons |
| `Docs/design/` | Design docs |
| `Source/` | Blender sources and review renders (not tracked) |

## Build
`dotnet build -c Release` (MDK2) deploys the mod to `%APPDATA%\SpaceEngineers\Mods\GVK_Suspension`.

## Design docs
| Doc | What it covers |
| --- | --- |
| [gvk-treads.md](Docs/design/gvk-treads.md) | The Kharak Tread and Kharak Double Tread, their wheels and every Tank Tracks value |
| [track-wheel-swap.md](Docs/design/track-wheel-swap.md) | Track wheels shown by swapping the wheel model, and the suspension blocks that swap |
| [icons.md](Docs/design/icons.md) | The full-color block icons and how they are rendered with SEUT |

## Quick links
- Hub issues: [GV-Server-Mods/GVK-Settings](https://github.com/GV-Server-Mods/GVK-Settings/issues)
- Tank Tracks Framework & API: [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3208995513)
- This mod: [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2780232704)

## Credits
- Digi, for Tank Tracks and for shipping the wheel swap crash fix.
- Zantulo, for the lifted suspension models.
- Keen Software House, for the vanilla suspensions and wheels the GVK blocks are built on.
