import unittest
from app import configured_app

class HomeViewTest(unittest.TestCase):
    def setUp(self):
        self.app = configured_app().test_client()
        self.app.testing = True

    def test_home_app(self):
        home = self.app.get('/')
        self.assertIn('topic', str(home.data))


if __name__ == '__main__':
    unittest.main()