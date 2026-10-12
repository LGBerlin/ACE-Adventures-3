import hashlib,tempfile,unittest
import update_addons as u

class UpdateSecurityTests(unittest.TestCase):
    def manifest(self,paths=('assets/a.png',),urls=None):
        content=b'image'
        urls=urls or ['https://example.test/updates/a.png']*len(paths)
        return {'version':'1.2.3','files':[{'path':p,'url':v,'sha256':hashlib.sha256(content).hexdigest()} for p,v in zip(paths,urls)]}
    def test_duplicate_files_rejected_before_disk_write(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):u.apply(d,self.manifest(('assets/a.png','assets/a.png')),lambda _:b'image','https://example.test/updates')
    def test_url_with_query_or_credentials_rejected(self):
        for url in ('https://example.test/updates/a.png?change=1','https://user@example.test/updates/a.png','https://example.test.evil/updates/a.png'):
            with self.subTest(url=url),tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError):u.apply(d,self.manifest(urls=[url]),lambda _:b'image','https://example.test/updates')
    def test_hidden_files_and_bad_types_rejected(self):
        for value in (None,123,'assets/.secret','themes/x:code','stories/../old','assets\\bad'):
            self.assertFalse(u.valid_path(value),repr(value))
    def test_version_is_strict(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):u.apply(d,{'version':'..','files':[]},lambda _:b'','https://example.test/updates')