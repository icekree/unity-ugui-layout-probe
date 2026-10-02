# Calculate Unity RectTransform overflow with Python

For Unity uGUI developers who want to inspect supplied anchors, pivots and rectangle geometry without launching Unity. This tutorial uses original synthetic input and the frozen experimental [Unity uGUI Layout Probe](../README.md). It does not import a Unity scene or establish native Unity parity.

## Run the seven-scene demo

Clone this repository, enter its root directory, and use Python 3.12 with [uv](https://docs.astral.sh/uv/):

```sh
uv run --with-requirements requirements.txt python demo.py
```

The command prints the actual `artifacts/demo/<report_id>/` directory. Open its `summary.json` and `02.png` alongside the [input fixture](../examples/layouts.json). The default fixture has nine nodes: eight computed and one `UNKNOWN`. Report IDs include the implementation and environment, so do not copy an ID from a different machine.

## Supply an explicit RectTransform

This is the fixture's `overflow` case wrapped as a complete version-1 input. Save it as `artifacts/overflow-input.json` (create `artifacts/` first) to run only this case. The node's visibility defaults to true, with no declared runtime uncertainty.

```json
{
  "schema_version": 1,
  "cases": [{
    "id": "overflow",
    "viewport": [100, 100],
    "canvas": {
      "render_mode": "screen_space_overlay",
      "scaler": {"ui_scale_mode": 0, "scale_factor": 1}
    },
    "nodes": [{
      "id": "box",
      "parent": null,
      "rect": {
        "m_AnchorMin": {"x": 0, "y": 0},
        "m_AnchorMax": {"x": 0, "y": 0},
        "m_Pivot": {"x": 0.5, "y": 0.5},
        "m_SizeDelta": {"x": 20, "y": 20},
        "m_AnchoredPosition": {"x": 105, "y": 50}
      }
    }]
  }]
}
```

```sh
uv run --with-requirements requirements.txt python demo.py --input artifacts/overflow-input.json --output artifacts/overflow-report
```

The output base is separate from the input's directory; the demo rejects output bases containing the input. One case produces `01.png`, an overview and a report. The public [format contract](format.md) explains required fields, inherited state and unsupported modes.

## Verify 15 pixels and 0.75 by hand

The Canvas scale factor is 1, so the logical Canvas is 100×100. Equal bottom-left anchors contribute no stretch. SizeDelta therefore gives a 20×20 rectangle. With pivot (0.5, 0.5) and anchored position (105, 50), its logical bounds are x=95..115 and y=40..60. Top-left screen coordinates flip y but leave those symmetric y bounds unchanged.

The viewport ends at x=100. Right overflow is `115 - 100 = 15` pixels. The full area is `20 × 20 = 400`; the screen excludes a `15 × 20 = 300` strip. Outside area ratio is `300 / 400 = 0.75`. This exceeds the default 4-pixel tolerance.

The computed node reports `overflow.edges.right: 15`, `overflow.outside_ratio: 0.75` and `band: "A"`. A means the supplied state is visible without declared uncertainty; it does not certify a runtime defect. The [hand-derived expectations](../examples/expected.json) are independent of report generation.

## Reuse only the standard-library geometry

From the repository root, run the [complete reuse example](../examples/reuse_geometry.py):

```sh
uv run --python 3.12 python -m examples.reuse_geometry
```

It needs no Pillow and writes no files. It calls `canvas_scale`, `child_frame` and `corners` for the same valid RectTransform, then `overflow`. Its core calculation is:

```python
size, pivot, matrix = child_frame(rect, canvas_size, {"x": 0, "y": 0}, IDENTITY)
polygon = corners(size, pivot, matrix, factor, viewport[1])
result = overflow(polygon, viewport)
```

Expected output:

```json
{"after_ancestor_clip": null, "outside_ratio": 0.75, "right_pixels": 15.0}
```

To borrow it under MIT, copy `geometry.py` and adapt the example, retaining the copyright/license notice. Helper signatures are experimental, not a stable package API. This short example assumes valid geometry; it does not replace the demo's structural checks, failure propagation or `UNKNOWN` reporting. In particular, a low-level `overflow` return of `None` can also mean degenerate geometry, so it alone is not a validity verdict.

## Understand clipping and unknown results

The `ancestor-clip` scene declares a parent rectangle covering x=0..100 and y=0..100. It clips the child to x=95..100, leaving area 100. Overflow is then absent, while the child's original polygon remains outside. The ratio's denominator is the ancestor-clipped area, not the original rectangle. The reuse example models the same clip polygon. This is rectangular polygon clipping, not Unity stencil/Mask emulation.

The `unsupported-canvas` scene declares World Space and yields `UNKNOWN` with `canvas: ValueError: unsupported Canvas render mode`. Missing geometry, invalid transforms and unresolved parents also stay unknown. `runtime-uncertain` still computes geometry and receives B; `default-hidden` receives C. Neither is the same as failed geometry. Fully clipped valid geometry remains computed; `UNKNOWN` never counts as a pass.

**No systematic native Unity comparison has been completed. Determinism is not correctness, and static overflow is not a runtime defect.** Standard layout and clipping formulas belong to their established sources; this project's contribution is its implementation, explicit failures, original fixtures and verification. See [attribution](../THIRD_PARTY.md), the [bounded engineering case](case-study.md) and [release fixes](../CHANGELOG.md).

## 中文摘要

这篇教程用原创 RectTransform 输入说明：100×100 视口里，一个 20×20、中心在 (105, 50) 的矩形横跨 x=95..115，因此右侧越界 15 像素，屏幕外面积为 300/400=0.75。先运行七场景演示，再按上面的完整 JSON 单独运行此场景；标准库复用示例无需 Pillow 或 Unity。

祖先裁剪后可能不再越界，但原矩形仍在外侧；裁剪后的面积才是比例的分母。A/B/C 是输入状态下的静态分诊，UNKNOWN 是无法计算，不表示通过。底层函数仍属实验性接口；使用时保留 MIT 声明，并自行处理验证和失败。尚无系统性的 Unity 原生运行对照，不能将结果当作已确认的游戏或运行时缺陷。
