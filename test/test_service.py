#!/usr/bin/env python3
import unittest
from flask_testing import TestCase
from service import app

class TestApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_submit(self):
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