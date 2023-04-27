#!/usr/bin/env python3
import unittest
from unittest.mock import patch
from flask_testing import TestCase
from service import app, init_worker_resources, release_resources

class TestApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @classmethod
    def setUpClass(cls):
        init_worker_resources()

    @classmethod
    def tearDownClass(cls):
        release_resources()

    @patch('service.ssh_connections.put')
    @patch('service.ssh_connections.get')
    @patch('service.execute_ssh_task')
    def test_submit(self, mock_execute_ssh_task,mock_ssh_get,_):
        mock_execute_ssh_task.return_value = ("Hello, World!", "")
        mock_ssh_get.return_value = None

        data = {"command": "echo 'Hello, World!'"}
        response = self.client.post('/submit', json=data)
        self.assertEqual(response.status_code, 200)

        result = response.json
        self.assertIn("output", result)
        self.assertIn("error", result)
        self.assertEqual(result["output"].strip(), "Hello, World!")
        self.assertEqual(result["error"].strip(), "")

    def test_invalid_request(self):
        response = self.client.post('/submit', json={})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()