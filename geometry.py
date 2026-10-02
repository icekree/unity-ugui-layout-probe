"""Deterministic screen-space geometry. No Unity runtime or file writes."""
from __future__ import annotations

import math


def finite_number(value):
    """Reject booleans, strings and non-finite numbers; never guess input values."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('expected a finite number')
    return value


def vector(value, keys):
    if not isinstance(value, dict):
        raise ValueError('expected a coordinate object')
    return tuple(finite_number(value[k]) for k in keys)


IDENTITY = ((1., 0., 0., 0.), (0., 1., 0., 0.), (0., 0., 1., 0.), (0., 0., 0., 1.))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)) for i in range(4))


def trs(position, rotation, scale):
    if not isinstance(rotation, dict) or not isinstance(scale, dict):
        raise ValueError('rotation and scale must be coordinate objects')
    position = tuple(finite_number(v) for v in position)
    if len(position) != 3:
        raise ValueError('position must have three coordinates')
    x, y, z, w = (finite_number(rotation.get(k, 1. if k == 'w' else 0.)) for k in 'xyzw')
    length = math.hypot(x, y, z, w)
    if not math.isfinite(length):
        raise ValueError('invalid quaternion norm')
    if not length:
        raise ValueError('zero quaternion')
    x, y, z, w = (v / length for v in (x, y, z, w))
    sx, sy, sz = (finite_number(scale.get(k, 1.)) for k in 'xyz')
    return (
        ((1-2*(y*y+z*z))*sx, 2*(x*y-z*w)*sy, 2*(x*z+y*w)*sz, position[0]),
        (2*(x*y+z*w)*sx, (1-2*(x*x+z*z))*sy, 2*(y*z-x*w)*sz, position[1]),
        (2*(x*z-y*w)*sx, 2*(y*z+x*w)*sy, (1-2*(x*x+y*y))*sz, position[2]),
        (0., 0., 0., 1.),
    )


def transform(matrix, point):
    v = (*point, 1.)
    return tuple(sum(matrix[i][j] * v[j] for j in range(4)) for i in range(3))


def canvas_scale(viewport, scaler):
    """Unity CanvasScaler's supported modes; screen/logical size is NOT reference size."""
    viewport = tuple(finite_number(v) for v in viewport)
    if len(viewport) != 2 or min(viewport) <= 0:
        raise ValueError('viewport must have two positive dimensions')
    mode = finite_number(scaler['ui_scale_mode'])
    if mode == 0:
        factor = scaler['scale_factor']
    elif mode == 1:
        rx, ry = vector(scaler, ('reference_width', 'reference_height'))
        if min(rx, ry) <= 0:
            raise ValueError('invalid reference resolution')
        x, y = viewport[0] / rx, viewport[1] / ry
        match_mode = finite_number(scaler['screen_match_mode'])
        if match_mode == 0:
            m = finite_number(scaler['match_width_or_height'])
            if not 0 <= m <= 1:
                raise ValueError('invalid matchWidthOrHeight')
            factor = 2 ** ((1-m)*math.log2(x) + m*math.log2(y))
        elif match_mode == 1:
            factor = min(x, y)
        elif match_mode == 2:
            factor = max(x, y)
        else:
            raise ValueError('unknown screen match mode')
    else:
        raise ValueError('physical/DPI CanvasScaler unsupported')
    finite_number(factor)
    if factor <= 0:
        raise ValueError('invalid scale factor')
    return factor, (viewport[0]/factor, viewport[1]/factor)


def child_frame(tree, parent_size, parent_pivot, parent_matrix):
    lo, hi = tree['m_AnchorMin'], tree['m_AnchorMax']
    pivot, delta, anchored = tree['m_Pivot'], tree['m_SizeDelta'], tree['m_AnchoredPosition']
    for value in (lo, hi, pivot, delta, anchored, parent_pivot):
        vector(value, 'xy')
    for value in parent_size:
        finite_number(value)
    size = tuple(parent_size[i]*(hi[k]-lo[k]) + delta[k] for i, k in enumerate('xy'))
    position = [parent_size[i]*(-parent_pivot[k] + lo[k] + (hi[k]-lo[k])*pivot[k]) + anchored[k]
                for i, k in enumerate('xy')]
    local_position = tree.get('m_LocalPosition', {})
    if not isinstance(local_position, dict):
        raise ValueError('local position must be a coordinate object')
    position.append(local_position.get('z', 0.))
    matrix = multiply(parent_matrix, trs(position, tree.get('m_LocalRotation', {}), tree.get('m_LocalScale', {})))
    return size, pivot, matrix


def corners(size, pivot, matrix, factor, height, padding=(0., 0., 0., 0.)):
    left, bottom = -pivot['x']*size[0]+padding[0], -pivot['y']*size[1]+padding[1]
    right, top = (1-pivot['x'])*size[0]-padding[2], (1-pivot['y'])*size[1]-padding[3]
    if right <= left or top <= bottom:
        return []
    result = []
    for x, y in ((left, bottom), (right, bottom), (right, top), (left, top)):
        px, py, _ = transform(matrix, (x, y, 0.))
        result.append((px*factor, height-py*factor))
    return result


def signed_area(poly):
    return sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(poly, poly[1:]+poly[:1]))/2 if poly else 0.


def area(poly):
    return abs(signed_area(poly))


def clip_polygon(subject, clip):
    """Convex Sutherland-Hodgman; supports mirrored and rotated rectangles."""
    if len(subject) < 3 or len(clip) < 3 or area(clip) < 1e-9:
        return []
    sign = 1 if signed_area(clip) >= 0 else -1
    out = list(subject)
    for a, b in zip(clip, clip[1:]+clip[:1]):
        incoming, out = out, []
        if not incoming:
            break
        def distance(p):
            return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
        previous = incoming[-1]
        dp = distance(previous)
        for current in incoming:
            dc = distance(current)
            if (dc >= -1e-9) != (dp >= -1e-9):
                t = dp/(dp-dc)
                out.append((previous[0]+t*(current[0]-previous[0]), previous[1]+t*(current[1]-previous[1])))
            if dc >= -1e-9:
                out.append(current)
            previous, dp = current, dc
    return out


def screen_polygon(viewport):
    w, h = viewport
    return [(0., 0.), (w, 0.), (w, h), (0., h)]


def overflow(poly, viewport, tolerance=4.):
    finite_number(tolerance)
    if tolerance < 0:
        raise ValueError('negative tolerance')
    if len(poly) < 3 or area(poly) < 1e-6:
        return None
    xs, ys = zip(*poly)
    edges = dict(left=max(0., -min(xs)), right=max(0., max(xs)-viewport[0]),
                 top=max(0., -min(ys)), bottom=max(0., max(ys)-viewport[1]))
    if max(edges.values()) <= tolerance + 1e-7:
        return None
    ratio = max(0., min(1., 1-area(clip_polygon(poly, screen_polygon(viewport)))/area(poly)))
    return {'edges': edges, 'outside_ratio': ratio, 'max_pixels': max(edges.values()),
            'pronounced': max(edges.values()) > 16 or ratio >= .05}


def apply_clips(poly, clips):
    for clip in clips:
        poly = clip_polygon(poly, clip)
    return poly


def confidence(flags, active, alpha, enabled, expected=False):
    if not active or alpha <= .001 or not enabled or expected:
        return 'C'
    return 'B' if flags else 'A'
