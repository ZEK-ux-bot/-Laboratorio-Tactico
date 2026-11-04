import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import automation as p
class TestShorts(unittest.TestCase):
    def test_demo(self):
        d=p.demo_brief()
        p.verify_brief(d)
        s=p.plan_story(d,55.5)
        self.assertAlmostEqual(sum(x['duration'] for x in s['scenes']),55.5,places=4)
        self.assertFalse(s['verified_match'])
        self.assertIn('ILUSTRACIÓN',s['disclaimer'])
    def test_no_sources_blocks(self):
        d=p.demo_brief();d['selected']['sources']=[]
        with self.assertRaises(p.PipelineError): p.verify_brief(d)
    def test_bad_concept_blocks(self):
        d=p.demo_brief();d['selected']['scenes'][0]['concept']='real_positions'
        with self.assertRaises(p.PipelineError): p.verify_brief(d)
    def test_domains(self):
        self.assertTrue(p.official('https://www.uefa.com/'))
        self.assertFalse(p.official('https://uefa.com.evil.test/fake'))
    def test_srt(self):
        self.assertEqual(p.timecode_srt(61.31),'00:01:01,310')
if __name__=='__main__':unittest.main()
