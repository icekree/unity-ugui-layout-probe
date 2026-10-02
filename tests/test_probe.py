import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

import demo
import geometry as geo

FIXTURE = demo.ROOT/'examples/layouts.json'
DATA = json.loads(FIXTURE.read_text())
EXPECTED = json.loads((demo.ROOT/'examples/expected.json').read_text())


def sample():
    return copy.deepcopy(DATA['cases'][1])


class GeometryTests(unittest.TestCase):
    def test_analytic_overflow(self):
        n = demo.analyze_case(sample())['nodes'][0]
        self.assertEqual(n['overflow']['edges']['right'], EXPECTED['overflow']['right_pixels'])
        self.assertEqual(n['overflow']['outside_ratio'], EXPECTED['overflow']['outside_ratio'])
        self.assertEqual(n['band'], 'A')

    def test_anchors_and_noncentral_pivots(self):
        tree = copy.deepcopy(sample()['nodes'][0]['rect'])
        tree.update(m_AnchorMin={'x':.1,'y':.2}, m_AnchorMax={'x':.9,'y':.8},
                    m_Pivot={'x':.2,'y':.7}, m_SizeDelta={'x':-20,'y':30},
                    m_AnchoredPosition={'x':7,'y':-3})
        size, pivot, matrix = geo.child_frame(tree, (200,100), {'x':.3,'y':.6}, geo.IDENTITY)
        self.assertAlmostEqual(size[0],140)
        self.assertAlmostEqual(size[1],90)
        self.assertAlmostEqual(matrix[0][3],-1)
        self.assertAlmostEqual(matrix[1][3],-1)

    def test_canvas_modes(self):
        s = dict(ui_scale_mode=1, reference_width=100, reference_height=100,
                 screen_match_mode=0, match_width_or_height=.25)
        factor, size = geo.canvas_scale((400,200),s)
        self.assertAlmostEqual(factor, 4**.75*2**.25)
        self.assertAlmostEqual(size[0]*factor,400)
        s['screen_match_mode']=1
        self.assertEqual(geo.canvas_scale((400,200),s),(2,(200,100)))
        s['screen_match_mode']=2
        self.assertEqual(geo.canvas_scale((400,200),s),(4,(100,50)))
        self.assertEqual(geo.canvas_scale((400,200),dict(ui_scale_mode=0,scale_factor=2)),(2,(200,100)))

    def test_parent_rotation_and_mirror(self):
        n = demo.analyze_case(DATA['cases'][2])['nodes'][1]
        p=n['polygon']
        self.assertAlmostEqual(sum(x for x,y in p)/4,EXPECTED['rotation-and-mirror']['child_center'][0])
        self.assertAlmostEqual(sum(y for x,y in p)/4,EXPECTED['rotation-and-mirror']['child_center'][1])
        self.assertAlmostEqual(geo.area(p),EXPECTED['rotation-and-mirror']['child_area'])

    def test_rotated_reversed_clipping(self):
        clip=geo.screen_polygon((100,100))
        subject=[(-50,50),(50,-50),(150,50),(50,150)]
        self.assertAlmostEqual(geo.area(geo.clip_polygon(subject,clip)),10000)
        self.assertAlmostEqual(geo.area(geo.clip_polygon(subject,list(reversed(clip)))),10000)

    def test_tolerance(self):
        self.assertIsNone(geo.overflow([(-4,0),(10,0),(10,10),(-4,10)],(100,100)))
        self.assertIsNotNone(geo.overflow([(-4.01,0),(10,0),(10,10),(-4.01,10)],(100,100)))

    def test_clip_and_fully_clipped_are_computed(self):
        case=copy.deepcopy(DATA['cases'][3])
        r=demo.analyze_case(case)
        self.assertIsNone(r['nodes'][1]['overflow'])
        case['nodes'][1]['rect']['m_AnchoredPosition']['x']=150
        n=demo.analyze_case(case)['nodes'][1]
        self.assertEqual(n['status'],'computed')
        self.assertTrue(n['fully_clipped'])
        self.assertIsNone(n['overflow'])


class StatusTests(unittest.TestCase):
    def test_bands_are_not_defect_counts(self):
        self.assertEqual(demo.analyze_case(DATA['cases'][4])['nodes'][0]['band'],'B')
        self.assertEqual(demo.analyze_case(DATA['cases'][5])['nodes'][0]['band'],'C')
        self.assertEqual(demo.analyze_case(DATA['cases'][6])['counts']['unknown'],1)

    def assert_unknown(self, case, reason=None):
        r=demo.analyze_case(case)
        self.assertEqual(r['counts']['computed'],0)
        self.assertEqual(r['counts']['unknown'],len(case['nodes']))
        self.assertEqual(r['counts']['total'],r['counts']['computed']+r['counts']['unknown'])
        if reason:
            self.assertIn(reason,r['nodes'][0]['reason'])

    def test_missing_required_field(self):
        c=sample(); del c['nodes'][0]['rect']['m_SizeDelta']
        self.assert_unknown(c,'KeyError')

    def test_nonfinite_coordinates(self):
        for v in (float('nan'),float('inf'),-float('inf'),'50',True):
            c=sample(); c['nodes'][0]['rect']['m_AnchoredPosition']['x']=v
            self.assert_unknown(c,'finite number')

    def test_bad_quaternion_and_geometry(self):
        c=sample(); c['nodes'][0]['rect']['m_LocalRotation']=dict.fromkeys('xyzw',0)
        self.assert_unknown(c,'zero quaternion')
        c=sample(); c['nodes'][0]['rect']['m_SizeDelta']['x']=0
        self.assert_unknown(c,'non-positive')
        c=sample(); c['nodes'][0]['rect']['m_LocalScale']={'x':0,'y':1,'z':1}
        self.assert_unknown(c,'degenerate')

    def test_invalid_coordinate_objects(self):
        for key in ('m_LocalRotation', 'm_LocalScale', 'm_LocalPosition', 'm_AnchorMin'):
            for value in (None, [], 'invalid'):
                c=sample(); c['nodes'][0]['rect'][key]=value
                self.assert_unknown(c,'object')

    def test_invalid_canvas_and_viewport(self):
        for change in ('mode','missing','viewport','nan'):
            c=sample()
            if change=='mode': c['canvas']['scaler']['ui_scale_mode']=2
            if change=='missing': del c['canvas']['scaler']['scale_factor']
            if change=='viewport': c['viewport']=[0,100]
            if change=='nan': c['viewport']=[float('nan'),100]
            self.assert_unknown(c,'canvas:')
            json.dumps(demo.analyze_case(c),allow_nan=False)

    def test_unknown_parent_and_cycle(self):
        c=sample(); c['nodes'][0]['parent']='absent'
        self.assert_unknown(c,'parent not found')
        c=sample(); c['nodes'][0]['parent']='box'
        self.assert_unknown(c,'parent cycle')

    def test_failed_parent_propagates_even_out_of_order(self):
        c=copy.deepcopy(DATA['cases'][3]); del c['nodes'][0]['rect']['m_Pivot']
        c['nodes'].reverse()
        self.assert_unknown(c)

    def test_ancestor_hidden_uncertain_and_clip_propagate(self):
        c=copy.deepcopy(DATA['cases'][3]); c['nodes'][0].update(clip=False,active=False,uncertain=['animated'])
        n=demo.analyze_case(c)['nodes'][1]
        self.assertFalse(n['active']); self.assertEqual(n['band'],'C')
        c['nodes'][0]['active']=True
        self.assertEqual(demo.analyze_case(c)['nodes'][1]['band'],'B')

    def test_invalid_flags_do_not_become_pass(self):
        for key,value in [('active','false'),('alpha',2),('uncertain','animated'),('clip',1)]:
            c=sample(); c['nodes'][0][key]=value
            self.assert_unknown(c)

    def test_duplicate_ids_are_structural_error(self):
        c=sample(); c['nodes']*=2
        with self.assertRaises(ValueError): demo.analyze_case(c)


class ReportTests(unittest.TestCase):
    def test_deterministic_read_only_demo(self):
        before=FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            outputs=[Path(tmp)/'one',Path(tmp)/'two']
            reports=[demo.build(FIXTURE,out) for out in outputs]
            self.assertEqual(reports[0],reports[1])
            manifests=[{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()} for out in outputs]
            self.assertEqual(manifests[0],manifests[1])
            self.assertEqual(len(reports[0]['cases']),7)
            self.assertEqual(sum(c['counts']['total'] for c in reports[0]['cases']),EXPECTED['total_nodes'])
            self.assertEqual(sum(c['counts']['computed'] for c in reports[0]['cases']),EXPECTED['computed_nodes'])
            self.assertEqual(sum(c['counts']['unknown'] for c in reports[0]['cases']),EXPECTED['unknown_nodes'])
        self.assertEqual(FIXTURE.read_bytes(),before)

    def test_source_directory_is_not_an_output(self):
        with self.assertRaises(ValueError): demo.build(FIXTURE,FIXTURE.parent)


if __name__=='__main__': unittest.main()
