import unittest
from .test_client import TestClient
from api.app import create_app
from api.models import db, User


class TestAPI(unittest.TestCase):
    default_username = 'jonah'
    default_password = 'whale'

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        u = User(username=self.default_username,
                 password=self.default_password)
        db.session.add(u)
        db.session.commit()
        self.client = TestClient(self.app, u.generate_auth_token(), '')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_password_auth(self):
        self.app.config['USE_TOKEN_AUTH'] = False
        good_client = TestClient(self.app, self.default_username,
                                 self.default_password)
        rv, json = good_client.get('/api/v1.0/pxcodes/')
        self.assertTrue(rv.status_code == 200)

        self.app.config['USE_TOKEN_AUTH'] = True
        u = User.query.get(1)
        good_client = TestClient(self.app, u.generate_auth_token(), '')
        rv, json = good_client.get('/api/v1.0/pxcodes/')
        self.assertTrue(rv.status_code == 200)

    def test_bad_auth(self):
        bad_client = TestClient(self.app, 'abc', 'def')
        rv, json = bad_client.get('/api/v1.0/pxcodes/')
        self.assertTrue(rv.status_code == 401)

        self.app.config['USE_TOKEN_AUTH'] = True
        bad_client = TestClient(self.app, 'bad_token', '')
        rv, json = bad_client.get('/api/v1.0/pxcodes/')
        self.assertTrue(rv.status_code == 401)

    def test_rate_limits(self):
        self.app.config['USE_RATE_LIMITS'] = True

        rv, json = self.client.get('/api/v1.0/cases/')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue('X-RateLimit-Remaining' in rv.headers)
        self.assertTrue('X-RateLimit-Limit' in rv.headers)
        self.assertTrue('X-RateLimit-Reset' in rv.headers)
        self.assertTrue(int(rv.headers['X-RateLimit-Limit']) == int(rv.headers['X-RateLimit-Remaining']) + 1)
        while int(rv.headers['X-RateLimit-Remaining']) > 0:
            rv, json = self.client.get('/api/v1.0/cases/')
        self.assertTrue(rv.status_code == 429)

    def test_cache_control(self):
        client = TestClient(self.app, self.default_username,
                            self.default_password)
        rv, json = client.get('/auth/request-token')
        self.assertTrue(rv.status_code == 200)
        self.assertTrue('Cache-Control' in rv.headers)
        cache = [c.strip() for c in rv.headers['Cache-Control'].split(',')]
        self.assertTrue('no-cache' in cache)
        self.assertTrue('no-store' in cache)
        self.assertTrue('max-age=0' in cache)
        self.assertTrue(len(cache) == 3)
