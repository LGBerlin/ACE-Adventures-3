import hashlib,json,tempfile,unittest
from pathlib import Path
import addon_updates as c
class UpdateChannelTests(unittest.TestCase):
 def manifest(self,version,payload=b'{"chapter":"The Hollow Bell"}'):
  filename='stories/hollow-bell.json'
  url=c.ORIGIN+'/updates/'+version+'/'+filename
  d={'version':version,'files':[{'path':filename,'url':url,'sha256':hashlib.sha256(payload).hexdigest()}]}
  return json.dumps(d).encode(),url,payload
 def test_install_idempotent_incremental_and_rollback(self):
  with tempfile.TemporaryDirectory() as td:
   a,url,payload=self.manifest('1.0.0');responses={c.MANIFEST:a,url:payload}
   fetch=lambda x:responses[x]
   self.assertEqual(c.check_and_install(td,fetch)[0],'updated')
   self.assertEqual(c.check_and_install(td,fetch)[0],'current')
   b,url2,p2=self.manifest('1.0.1',b'NEW')
   responses[c.MANIFEST]=b;responses[url2]=p2
   self.assertEqual(c.check_and_install(td,fetch),('updated','1.0.1'))
   self.assertEqual(c.current(td),'1.0.1')
   responses[c.MANIFEST]=a
   self.assertEqual(c.check_and_install(td,fetch),('current','1.0.1'))
 def test_mismatched_hash_preserves_active(self):
  with tempfile.TemporaryDirectory() as td:
   a,url,payload=self.manifest('1.0.0');response={c.MANIFEST:a,url:payload}
   c.check_and_install(td,lambda x:response[x])
   b,url2,p2=self.manifest('1.0.1');response[c.MANIFEST]=b;response[url2]=b'CORRUPT'
   self.assertEqual(c.check_and_install(td,lambda x:response[x])[0],'unavailable')
   self.assertEqual(c.current(td),'1.0.0')
 def test_host_disallowed(self):
  with self.assertRaises(ValueError):c._download('https://evil.example/payload',10,lambda u:b'x')
 def test_offline_leaves_game_alone(self):
  with tempfile.TemporaryDirectory() as td:
   def offline(u):raise OSError('offline')
   self.assertEqual(c.check_and_install(td,offline)[0],'unavailable')
   self.assertFalse((Path(td)/'addons').exists())
if __name__=='__main__':unittest.main()