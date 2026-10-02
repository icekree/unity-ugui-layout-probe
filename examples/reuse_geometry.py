"""Educational reuse of experimental helpers; run from the repository root.

No Pillow, file writes, Unity runtime, archive parsing or state inference.
This example assumes a valid, positive rectangle in Screen Space Overlay.
The JSON demo is responsible for input validation and UNKNOWN reporting.
"""
import json
import math

from geometry import IDENTITY, canvas_scale, child_frame, clip_polygon, corners, overflow, screen_polygon


def main():
    viewport = (100, 100)
    factor, canvas_size = canvas_scale(viewport, {"ui_scale_mode": 0, "scale_factor": 1})
    rect = {
        "m_AnchorMin": {"x": 0, "y": 0},
        "m_AnchorMax": {"x": 0, "y": 0},
        "m_Pivot": {"x": 0.5, "y": 0.5},
        "m_SizeDelta": {"x": 20, "y": 20},
        "m_AnchoredPosition": {"x": 105, "y": 50},
    }
    size, pivot, matrix = child_frame(rect, canvas_size, {"x": 0, "y": 0}, IDENTITY)
    polygon = corners(size, pivot, matrix, factor, viewport[1])
    result = overflow(polygon, viewport)
    assert result is not None
    assert math.isclose(result["edges"]["right"], 15)
    assert math.isclose(result["outside_ratio"], 0.75)

    # Model a declared ancestor clip occupying exactly the viewport.
    clipped = clip_polygon(polygon, screen_polygon(viewport))
    after_clip = overflow(clipped, viewport)
    assert after_clip is None
    print(json.dumps({"right_pixels": result["edges"]["right"],
                      "outside_ratio": result["outside_ratio"],
                      "after_ancestor_clip": after_clip}, sort_keys=True))


if __name__ == "__main__":
    main()
