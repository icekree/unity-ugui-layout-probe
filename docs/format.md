# Explicit input and report contract (version 1)

The public entry point is `demo.py`. This is a JSON geometry experiment, not a serialized Unity object format. Structural problems (invalid JSON, missing cases/IDs, duplicate IDs) stop the command with an error. Per-node missing geometry, non-finite values, invalid transforms or unresolved parents produce `UNKNOWN` with a reason. Unsupported or invalid Canvas context makes its nodes unknown.

## Input

Top-level `schema_version` is integer `1`; `cases` is a nonempty array of objects. Each `nodes` value must be an array of objects; an empty nodes array is valid, but an empty dictionary or string is not. Case IDs and node IDs are unique nonempty strings within their respective scope. Each case supplies:

| Field | Contract |
| --- | --- |
| `id` | Nonempty string |
| `viewport` | Two positive finite numbers: pixel width and height |
| `canvas.render_mode` | `screen_space_overlay`; all other modes unsupported |
| `canvas.scaler` | Parameters below |
| `nodes` | Array of explicit nodes |

Scaler `ui_scale_mode: 0` requires positive finite `scale_factor`. Mode `1` requires positive `reference_width`, `reference_height` and `screen_match_mode`: `0` (logarithmic width/height blend with `match_width_or_height` in [0,1]), `1` (expand: smaller factor), or `2` (shrink: larger factor). DPI/physical mode is unsupported. Logical Canvas size is viewport divided by the computed scale factor, not necessarily the reference resolution.

Each node requires `id`, `parent` (another node ID or `null`) and `rect`. The virtual root Canvas has bottom-left origin and pivot (0,0). Parents may appear after children; cycles, missing parents and failed parents propagate unknown results. `rect` requires complete x/y dictionaries for `m_AnchorMin`, `m_AnchorMax`, `m_Pivot`, `m_SizeDelta`, `m_AnchoredPosition`.

Optional `m_LocalPosition.z` defaults to 0; x/y position is derived from anchors and anchored position. Optional `m_LocalRotation` defaults to identity, with omitted components x/y/z=0 and w=1; provided components must be finite and the quaternion must have a nonzero finite norm. Optional `m_LocalScale` defaults to x/y/z=1. Nonunit valid quaternions are normalized. Positive calculated width/height and nondegenerate projected area are required. Screen coordinates use top-left origin, x rightward and y downward.

Optional node state:

| Field | Default / propagation |
| --- | --- |
| `active`, `enabled` | Boolean true; false propagates to descendants |
| `alpha` | Finite number in [0,1], default 1; multiply through ancestors |
| `uncertain` | Array of nonempty strings, default []; inherited union |
| `expected` | Boolean false; true propagates to descendants |
| `clip` | Boolean false; when true, this rectangle clips descendants |

These are declared experimental inputs, not a complete model of Unity state inheritance. `clip` uses a convex rectangular polygon after transforms, including mirrored winding. It does not clip the node itself, emulate stencil rendering or infer a Mask/RectMask2D from a scene.

## Output

`summary.json` includes exact input SHA-256, hashes of `geometry.py` and `demo.py`, Python/system/Pillow versions, `tolerance_pixels` (4 by default), cases and `input_unchanged`. `report_id` is the first 16 hex digits of SHA-256 of the canonical analysis payload, before image filenames and the final input-unchanged flag are added. It identifies an analysis payload, not a security signature or globally unique identifier.

Computed nodes include original and ancestor-clipped polygons, `fully_clipped`, effective supplied state, and optional overflow/band. Overflow reports nonnegative edge distances in screen pixels, maximum distance, outside area ratio after ancestor clipping, and a `pronounced` heuristic (>16 pixels or >=5% outside). Overflow within 4 pixels (with 1e-7 numeric slack) is suppressed. Outside ratio divides screen-excluded area by the ancestor-clipped polygon area. It does not measure opaque pixels or judge usability.

Unknown nodes include ID, status `UNKNOWN` and reason. Case counts satisfy `total = computed + unknown`. A/B/C counts are subsets of computed overflow; they are not probabilities or defect counts. A computed, entirely ancestor-clipped rectangle has no overflow and `fully_clipped: true`. No geometry is guessed after a parent failure.

Numbered PNGs and `overview.png` draw synthetic rectangles. Coordinates are fit to each panel for illustration; consult JSON for exact pixels. Built-in fonts and pinned Pillow avoid host-font dependencies. JSON/PNG repeatability is tested only within the same environment.

Reports go to `<--output directory>/<report_id>/`; the CLI prints that actual directory. Different analysis payloads do not mix their images, and same-input repeats reuse their own directory. Unexpected files in an existing report directory are rejected without deleting them. Inputs are checked before and after generation, including after report writing. An output base directory containing the input is rejected. Report directories cannot be symlinks; existing output targets must be regular files with a single link. Symlinks and hard links are rejected before any reports are written. These checks protect ordinary local execution, not concurrent file replacement by another process.
