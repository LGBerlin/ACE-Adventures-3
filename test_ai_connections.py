import unittest
import ai_connections as c

class ConnectionTests(unittest.TestCase):
    def test_services_available(self):
        def mock(url,timeout):
            if url.endswith('/api/tags'):return {'models':[{'name':'qwen3.5:4b'}]}
            if url.endswith('/system_stats'):return {'system':{'os':'macos'}}
            raise OSError()
        statuses=c.all_statuses(opener=mock)
        self.assertTrue(statuses['ollama']['ready'])
        self.assertTrue(statuses['comfyui']['ready'])
    def test_model_missing_is_not_ready(self):
        s=c.ollama_status(opener=lambda u,t:{'models':[{'name':'other:7b'}]})
        self.assertTrue(s['online']);self.assertFalse(s['ready'])
    def test_offline_fallback(self):
        def offline(u,t):raise OSError('offline')
        self.assertFalse(c.ollama_status(opener=offline)['online'])
        self.assertFalse(c.comfyui_status(opener=offline)['ready'])
    def test_malformed_response(self):
        self.assertFalse(c.comfyui_status(opener=lambda u,t:{'error':'no system'})['ready'])
