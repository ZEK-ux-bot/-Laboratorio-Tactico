import json,unittest,sys,os
from unittest.mock import patch, MagicMock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import automation as p
class TestAutoShorts(unittest.TestCase):
    def test_demo_passes(self):
        a=p.demo_brief();p.verify_brief(a)
        s=p.plan_story(a,55.5)
        self.assertAlmostEqual(sum(x['duration'] for x in s['scenes']),55.5,places=4)
        self.assertFalse(s['verified_match'])
        self.assertIn('ILUSTRACIÓN',s['disclaimer'])
    def test_lack_of_sources_blocks(self):
        a=p.demo_brief();a['selected']['sources']=[]
        with self.assertRaises(p.PipelineError):p.verify_brief(a)
    def test_bad_concept_blocks(self):
        a=p.demo_brief();a['selected']['scenes'][0]['concept']='real_exact_positions'
        with self.assertRaises(p.PipelineError):p.verify_brief(a)
    def test_official_domain_strict(self):
        self.assertTrue(p.official('https://www.uefa.com/'))
        self.assertFalse(p.official('https://uefa.com.evil.test/fake'))
        self.assertFalse(p.official('http://www.uefa.com/fake'))
    def test_heygen_no_paid_generation_without_approval(self):
        with patch.dict(os.environ, {'HEYGEN_API_KEY':'fake', 'GENERACION_PAGADA_AUTORIZADA':'NO'}):
            with self.assertRaises(p.PipelineError):
                p.get_audio('Texto de prueba',Path('/tmp/never-written.wav'))
    def test_heygen_v3_endpoint_and_no_voice_substitution(self):
        import requests
        fail=MagicMock()
        fail.ok=False
        fail.status_code=422
        with patch.dict(os.environ, {'HEYGEN_API_KEY':'fake','GENERACION_PAGADA_AUTORIZADA':'SI','HEYGEN_VOICE_ID':p.DEFAULT_VOICE}):
            with patch.object(requests,'post',return_value=fail) as req:
                with self.assertRaisesRegex(p.PipelineError,'compatible'):
                    p.get_audio('Texto de prueba', Path('/tmp/never-written.wav'))
                self.assertEqual(req.call_args.args[0],'https://api.heygen.com/v3/voices/speech')
                self.assertEqual(req.call_args.kwargs['json']['voice_id'],p.DEFAULT_VOICE)
    def test_srt_duration(self):
        self.assertEqual(p.timecode_srt(61.31),'00:01:01,310')
if __name__=='__main__':unittest.main()
