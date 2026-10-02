"""Inspect explicitly supplied synthetic layouts; no Unity or archive importer."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform

from PIL import Image, ImageDraw, ImageFont

import geometry as geo

ROOT = Path(__file__).resolve().parent
ERRORS = (KeyError, ValueError, TypeError, IndexError, OverflowError, RecursionError)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unknown(identifier, reason):
    return {'id': identifier, 'status': 'UNKNOWN', 'reason': reason}


def analyze_case(case, tolerance=4.):
    """Roots inherit a virtual Canvas with bottom-left origin and pivot (0, 0)."""
    nodes = case['nodes']
    ids = [n['id'] for n in nodes]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('node IDs must be unique nonempty strings')
    lookup = dict(zip(ids, nodes))
    results, frames, visiting = {}, {}, set()
    context_error = None
    try:
        if case['canvas']['render_mode'] != 'screen_space_overlay':
            raise ValueError('unsupported Canvas render mode')
        factor, logical_size = geo.canvas_scale(case['viewport'], case['canvas']['scaler'])
    except ERRORS as error:
        context_error = f'canvas: {type(error).__name__}: {error}'

    def resolve(identifier):
        if identifier in results:
            return results[identifier]
        if identifier in visiting:
            return unknown(identifier, 'parent cycle')
        if context_error:
            results[identifier] = unknown(identifier, context_error)
            return results[identifier]
        visiting.add(identifier)
        try:
            node = lookup[identifier]
            parent_id = node['parent']
            if parent_id is None:
                parent_size, parent_pivot, matrix = logical_size, {'x': 0., 'y': 0.}, geo.IDENTITY
                clips, inherited_flags, active, alpha, enabled, expected = [], [], True, 1., True, False
            else:
                if parent_id not in lookup:
                    raise ValueError('parent not found')
                parent = resolve(parent_id)
                if parent['status'] == 'UNKNOWN':
                    raise ValueError(f'parent unresolved: {parent["reason"]}')
                parent_size, parent_pivot, matrix, clips, inherited_flags, active, alpha, enabled, expected = frames[parent_id]
            flags = node.get('uncertain', [])
            if not isinstance(flags, list) or any(not isinstance(f, str) or not f for f in flags):
                raise ValueError('uncertain must be a list of nonempty strings')
            flags = sorted(set(inherited_flags + flags))
            for name in ('active', 'enabled', 'expected'):
                if name in node and not isinstance(node[name], bool):
                    raise ValueError(f'{name} must be boolean')
            active = active and node.get('active', True)
            enabled = enabled and node.get('enabled', True)
            expected = expected or node.get('expected', False)
            own_alpha = geo.finite_number(node.get('alpha', 1.))
            if not 0 <= own_alpha <= 1:
                raise ValueError('alpha must be in [0, 1]')
            alpha *= own_alpha
            size, pivot, matrix = geo.child_frame(node['rect'], parent_size, parent_pivot, matrix)
            if min(size) <= 0:
                raise ValueError('non-positive rectangle size')
            polygon = geo.corners(size, pivot, matrix, factor, case['viewport'][1])
            for point in polygon:
                for value in point:
                    geo.finite_number(value)
            if geo.finite_number(geo.area(polygon)) < 1e-6:
                raise ValueError('degenerate projected rectangle')
            visible_polygon = geo.apply_clips(polygon, clips)
            outside = geo.overflow(visible_polygon, case['viewport'], tolerance)
            band = geo.confidence(flags, active, alpha, enabled, expected) if outside else None
            result = {'id': identifier, 'status': 'computed', 'polygon': polygon,
                      'clipped_polygon': visible_polygon, 'fully_clipped': geo.area(visible_polygon) < 1e-6,
                      'overflow': outside, 'band': band, 'uncertain': flags,
                      'active': active, 'alpha': alpha, 'enabled': enabled, 'expected': expected}
            clip = node.get('clip', False)
            if not isinstance(clip, bool):
                raise ValueError('clip must be boolean')
            frames[identifier] = (size, pivot, matrix, clips + ([polygon] if clip else []),
                                  flags, active, alpha, enabled, expected)
            results[identifier] = result
        except ERRORS as error:
            results[identifier] = unknown(identifier, f'{type(error).__name__}: {error}')
        finally:
            visiting.discard(identifier)
        return results[identifier]

    for identifier in ids:
        resolve(identifier)
    ordered = [results[i] for i in ids]
    counts = {'total': len(ids), 'computed': sum(r['status'] == 'computed' for r in ordered),
              'unknown': sum(r['status'] == 'UNKNOWN' for r in ordered)}
    bands = Counter(r.get('band') for r in ordered)
    counts.update({b: bands[b] for b in 'ABC'})
    viewport = case.get('viewport')
    try:
        if len(viewport) != 2 or min(geo.finite_number(v) for v in viewport) <= 0:
            raise ValueError('invalid viewport')
    except ERRORS:
        viewport = None
    return {'id': case['id'], 'viewport': viewport, 'counts': counts, 'nodes': ordered}


def render_case(case, number, report_id):
    image = Image.new('RGB', (640, 440), '#111827')
    draw, font = ImageDraw.Draw(image), ImageFont.load_default(size=18)
    draw.text((20, 15), f'{number:02d} {case["id"]}', font=font, fill='white')
    draw.text((20, 42), f'Synthetic geometry | report {report_id}', font=font, fill='#cbd5e1')
    computed = [n for n in case['nodes'] if n['status'] == 'computed']
    viewport = case.get('viewport')
    try:
        width, height = viewport
        if min(width, height) <= 0 or not all(isinstance(v, (int, float)) and geo.finite_number(v) for v in viewport):
            raise ValueError('invalid viewport')
        points = [(0, 0), (width, height)] + [p for n in computed for p in n['polygon']]
        xs, ys = zip(*points)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        scale = min(570 / (xmax-xmin), 250 / (ymax-ymin))
        def mapped(poly):
            return [(35+(x-xmin)*scale, 95+(y-ymin)*scale) for x, y in poly]
        screen = mapped([(0, 0), (width, height)])
        draw.rectangle((*screen[0], *screen[1]), fill='#243244', outline='#67e8f9', width=3)
        colors = {'A': '#fb7185', 'B': '#fbbf24', 'C': '#94a3b8', None: '#a7f3d0'}
        for n in computed:
            poly = mapped(n['polygon'])
            draw.line(poly + poly[:1], fill=colors[n['band']], width=2)
            draw.text(poly[0], n['id'], font=ImageFont.load_default(size=13), fill=colors[n['band']])
            if n['clipped_polygon']:
                clipped = mapped(n['clipped_polygon'])
                draw.line(clipped + clipped[:1], fill=colors[n['band']], width=4)
    except ERRORS:
        draw.text((35, 140), 'Unsupported / unresolved geometry', font=font, fill='#fbbf24')
    c = case['counts']
    draw.text((20, 370), f'Computed {c["computed"]}/{c["total"]} | UNKNOWN {c["unknown"]}', font=font, fill='white')
    draw.text((20, 402), 'Rectangles, not runtime pixels or confirmed defects', font=ImageFont.load_default(size=15), fill='#cbd5e1')
    return image


def build(input_path, output, tolerance=4.):
    geo.finite_number(tolerance)
    if tolerance < 0:
        raise ValueError('negative tolerance')
    source = input_path.read_bytes()
    data = json.loads(source)
    if type(data['schema_version']) is not int or data['schema_version'] != 1 or not isinstance(data['cases'], list):
        raise ValueError('expected schema_version 1 and cases list')
    case_ids = [c['id'] for c in data['cases']]
    if any(not isinstance(i, str) or not i for i in case_ids) or len(case_ids) != len(set(case_ids)):
        raise ValueError('case IDs must be unique nonempty strings')
    report = {'schema_version': 1, 'input_sha256': digest(source),
              'implementation_sha256': {n: digest((ROOT/n).read_bytes()) for n in ('geometry.py', 'demo.py')},
              'parameters': {'tolerance_pixels': tolerance},
              'environment': {'python': platform.python_version(), 'system': platform.system(),
                              'Pillow': importlib.metadata.version('Pillow')},
              'cases': [analyze_case(c, tolerance) for c in data['cases']],
              'limitations': ['Synthetic explicit input; no Unity/archive importer',
                              'Rectangular bounds, not runtime pixels or confirmed defects',
                              'Unknown does not mean pass; no native Unity parity certification']}
    report['report_id'] = digest(canonical(report))[:16]
    # Check source and JSON before creating output; never place reports beside source bytes by accident.
    if input_path.read_bytes() != source:
        raise RuntimeError('input changed during analysis')
    output = output.resolve()
    if input_path.resolve().is_relative_to(output):
        raise ValueError('output directory must not contain input file')
    output.mkdir(parents=True, exist_ok=True)
    cards = []
    for number, case in enumerate(report['cases'], 1):
        card = render_case(case, number, report['report_id'])
        filename = f'{number:02d}.png'
        card.save(output/filename, 'PNG')
        case['image'] = filename
        cards.append(card)
    if cards:
        overview = Image.new('RGB', (1280, 440*((len(cards)+1)//2)), '#111827')
        for i, card in enumerate(cards):
            overview.paste(card, ((i % 2)*640, (i//2)*440))
        overview.save(output/'overview.png', 'PNG')
    report['input_unchanged'] = input_path.read_bytes() == source
    if not report['input_unchanged']:
        raise RuntimeError('input changed during rendering')
    (output/'summary.json').write_text(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'examples/layouts.json')
    parser.add_argument('--output', type=Path, default=ROOT/'artifacts/demo')
    args = parser.parse_args()
    try:
        report = build(args.input, args.output)
    except ERRORS + (OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(json.dumps({'report_id': report['report_id'], 'cases': len(report['cases']),
                      'unknown': sum(c['counts']['unknown'] for c in report['cases']),
                      'output': str(args.output), 'input_unchanged': report['input_unchanged']}))


if __name__ == '__main__':
    main()
