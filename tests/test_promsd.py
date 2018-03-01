import unittest

from flask import current_app
from promsd.promsd import create_app


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.app.debug = False
        self.app_client = self.app.test_client()
        # with app_client.app_context():
        #     flaskr.init_db()

        # self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # db.connect()


    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        self.app_context.pop()


    def test_app_exists(self):
        self.assertFalse(current_app is None)
#
#
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])


    def test_empty_db(self):
        rv = self.app_client.get('/')
        self.assertEqual(rv.status_code, 404)
        self.assertIn(b'The requested URL was not found on the server', rv.data )
