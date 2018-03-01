import unittest
import json

from flask import current_app
from promsd.promsd import create_app, db
from promsd.models import Target


class TargetTestCases(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.app.debug = False

        self.app_context = self.app.app_context()
        self.app_context.push()

        self.app_client = self.app.test_client()
        # self.app_context = self.app.app_context()
        # self.app_context.push()


    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        self.app_context.pop()


    # def test_adding_target(self):
    #     t = Target.create(host='test.foo.bar', job='1')
    #     self.assertEqual(t.host, "test.foo.bar")


    def test_get_all_targets(self):
        """Retrieve all targets"""

        resp = self.app_client.get('/api/v1/targets/')
        self.assertEqual(resp.status_code, 200)

        data = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(data[0]['target'], "target2.examples.org")
        self.assertEqual(data[0]['job'], "node")

    def test_get_target(self):
        """Retrieve single target"""

        resp = self.app_client.get('/api/v1/targets/1/')
        self.assertEqual(resp.status_code, 200)
        # assert resp.status_code == 200

        data = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(data['target'], "target2.examples.org")
        self.assertEqual(data['job'], "node")


    def test_post_target(self):
        """Create new target using POST"""
        params = {
            "target": "test.foo.bar",
            "job": "node",
            "labels": {
                "label1": "value1",
                "label2": "value2"
            }
        }

        resp_post = self.app_client.post('/api/v1/targets/', data=json.dumps(params), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

        target_id = json.loads(resp_post.data.decode('utf-8'))['id']

        rest_get = self.app_client.get('/api/v1/targets/{}/'.format(target_id))
        self.assertEqual(rest_get.status_code, 200)

        data = json.loads(rest_get.data.decode('utf-8'))
        self.assertEqual(data['target'], "test.foo.bar")
        self.assertEqual(data['job'], "node")

    def test_post_target_without_labels(self):
        """Create single target without labels"""

        params = {
            "target": "test.foo.bar",
            "job": "node",
        }

        resp_post = self.app_client.post('/api/v1/targets/', data=json.dumps(params), content_type='application/json')
        self.assertEqual(resp_post.status_code, 201)

        target_id = json.loads(resp_post.data.decode('utf-8'))['id']

        rest_get = self.app_client.get('/api/v1/targets/{}/'.format(target_id))
        self.assertEqual(rest_get.status_code, 200)

        data = json.loads(rest_get.data.decode('utf-8'))
        self.assertEqual(data['target'], "test.foo.bar")
        self.assertEqual(data['job'], "node")
        self.assertEqual(data['labels'], {})

    def test_put_target_create_new(self):
        """Create new target via PUT request."""
        params = {
            "target": "test2.foo.bar",
            "job": "mysql"
        }

        target_id = 10

        resp_post = self.app_client.put('/api/v1/targets/{}/'.format(target_id), data=json.dumps(params), content_type='application/json')
        # Returns 201 Created
        self.assertEqual(resp_post.status_code, 201)        # target_id = json.loads(resp_post.data.decode('utf-8'))['id']

        rest_get = self.app_client.get('/api/v1/targets/{}/'.format(target_id))
        self.assertEqual(rest_get.status_code, 200)

        data = json.loads(rest_get.data.decode('utf-8'))
        self.assertEqual(data['target'], "test2.foo.bar")
        self.assertEqual(data['job'], "mysql")


    def test_put_target_update(self):
        """Update target via PUT request."""

        target_id = 10

        # Create record
        params = {
            "target": "test1.foo.bar",
            "job": "mysql"
        }
        self.app_client.put('/api/v1/targets/{}/'.format(target_id), data=json.dumps(params),
                                        content_type='application/json')
        # Update record
        params['target'] = "test2.foo.bar"
        update_record = self.app_client.put('/api/v1/targets/{}/'.format(target_id), data=json.dumps(params),
                                            content_type='application/json')

        # Returns 200 OK on update
        self.assertEqual(update_record.status_code, 200)

        # Check if updated record seen in GET request
        rest_get = self.app_client.get('/api/v1/targets/{}/'.format(target_id))
        self.assertEqual(rest_get.status_code, 200)

        data = json.loads(rest_get.data.decode('utf-8'))
        self.assertEqual(data['target'], "test2.foo.bar")
        self.assertEqual(data['job'], "mysql")


    def test_delete_target(self):
        """Delete target."""

        target_id = 1

        # Delete record
        rest_delete = self.app_client.delete('/api/v1/targets/{}/'.format(target_id), content_type='application/json')

        # Returns 204 No Content on update
        self.assertEqual(rest_delete.status_code, 204)

        # Check if updated record seen in GET request
        rest_get = self.app_client.get('/api/v1/targets/{}/'.format(target_id))
        self.assertEqual(rest_get.status_code, 404)

        data = json.loads(rest_get.data.decode('utf-8'))
        self.assertEqual(data['error'], "Target with this ID doesn't exists.")

