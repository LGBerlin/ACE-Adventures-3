import unittest
from app_release_checker import check,parse_version
class AppReleaseCheckTests(unittest.TestCase):
 def test_valid_versions(self):
  self.assertEqual(parse_version('v1.2.3'),(1,2,3))
  with self.assertRaises(ValueError):parse_version('v1.2.3/../../')
 def test_does_not_advertise_prerelease(self):
  result=check('1.0.0',lambda:{'tag_name':'v1.1.0','prerelease':True})
  self.assertEqual(result['status'],'unavailable')
 def test_verified_named_asset(self):
  record={'tag_name':'v1.1.0','draft':False,'prerelease':False,'assets':[{'name':'ACE Adventures 3 Mac App.zip','browser_download_url':'https://github.com/LGBerlin/ACE-Adventures-3/releases/download/v1.1.0/ACE%20Adventures%203%20Mac%20App.zip'}]}
  self.assertEqual(check('v1.0.0',lambda:record)['status'],'available')
  self.assertEqual(check('v2.0.0',lambda:record)['status'],'current')
 def test_bad_url_or_missing_asset(self):
  record={'tag_name':'v2.0.0','draft':False,'prerelease':False,'assets':[{'name':'ACE Adventures 3 Mac App.zip','browser_download_url':'https://evil.test/file.zip'}]}
  self.assertEqual(check('1.0.0',lambda:record)['status'],'unavailable')
  self.assertEqual(check('1.0.0',lambda:{'tag_name':'v2.0.0','assets':[]})['status'],'unavailable')
