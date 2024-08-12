import unittest
from tilores import TiloresAPI

class IntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tilores = TiloresAPI.from_environ()

    def test_access_token(self):
        self.assertIsNotNone(self.tilores.access_token)
