#!/usr/bin/env python3
import unittest
from flask_testing import TestCase
from service import app, ssh_connections, task_queue, workers

class TestApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @classmethod
    def tearDownClass(cls):
        # Stop worker threads
        for _ in range(len(workers)):
            task_queue.put(None)
        for worker in workers:
            worker.join()
        # Close SSH connections
        while not ssh_connections.empty():
            ssh_client = ssh_connections.get()
            ssh_client.close()

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