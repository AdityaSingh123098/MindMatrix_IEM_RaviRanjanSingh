import unittest
import json
from app import app

class TestAppEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_get_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Communication Gap Detector", response.data)

    def test_get_api_samples(self):
        response = self.client.get("/api/samples")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("samples", data)
        self.assertEqual(len(data["samples"]), 6)

    def test_post_analyze_json(self):
        payload = {
            "conversation": "Neha: What time is the meeting?\nRavi: I am working on the report.\nSoham: I'll send the dataset."
        }
        response = self.client.post("/analyze", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("gaps", data)
        self.assertTrue(any(g["type"] == "Unanswered Question" for g in data["gaps"]))

    def test_post_analyze_empty(self):
        response = self.client.post("/analyze", json={"conversation": ""})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_post_analyze_form_data(self):
        response = self.client.post("/analyze", data={"conversation": "Ravi: Can you send the dataset?\nSoham: Okay.\nRavi: Can you send the dataset?"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(any(g["type"] == "Repeated Request" for g in data["gaps"]))

if __name__ == "__main__":
    unittest.main()
