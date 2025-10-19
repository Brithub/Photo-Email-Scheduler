import unittest
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
import yaml
import os
from fastapi.testclient import TestClient
from response_api import app, photo_taken, add_text

class TestResponseApi(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('random.choice')
    @patch('os.path.exists')
    @patch('response_api.now')
    def test_photo_taken_first_time(self, mock_now, mock_exists, mock_choice,
                                    mock_yaml_load, mock_file, mock_makedirs):
        # Test photo_taken endpoint for first photo of the day
        mock_now.return_value = MagicMock(year=2023, month=1, day=1)
        mock_exists.return_value = False
        mock_yaml_load.return_value = {"response": ["Test response"]}
        mock_choice.return_value = "Test response"

        response = self.client.get("/photo_taken/testuser/+0000")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '"Test response"')
        mock_makedirs.assert_called()
        mock_file.assert_called()

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    @patch('random.choice')
    @patch('os.path.exists')
    @patch('response_api.now')
    def test_photo_taken_already_taken(self, mock_now, mock_exists, mock_choice,
                                       mock_yaml_load, mock_file, mock_makedirs):
        # Test photo_taken when photo already taken today
        mock_now.return_value = MagicMock(year=2023, month=1, day=1)
        mock_exists.return_value = True
        mock_choice.return_value = "subject"

        response = self.client.get("/photo_taken/testuser/+0000")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("You are already real" in response.text)
        self.assertTrue("subject" in response.text)

    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('builtins.open', new_callable=mock_open)
    async def test_add_text(self, mock_file, mock_yaml_dump, mock_yaml_load):
        # Test adding text to existing message type
        mock_yaml_load.return_value = {"content": ["Existing content"]}

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b"New content")

        result = await add_text("content", mock_request)

        self.assertEqual(result, "Message added")
        expected_data = {"content": ["Existing content", "New content"]}
        mock_yaml_dump.assert_called_with(expected_data, mock_file())

    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('builtins.open', new_callable=mock_open)
    async def test_add_text_new_type(self, mock_file, mock_yaml_dump, mock_yaml_load):
        # Test adding text for new message type
        mock_yaml_load.return_value = {"content": ["Existing content"]}

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b"New type content")

        result = await add_text("new_type", mock_request)

        self.assertEqual(result, "Message added")
        expected_data = {
            "content": ["Existing content"],
            "new_type": ["New type content"]
        }
        mock_yaml_dump.assert_called_with(expected_data, mock_file())

    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('builtins.open', new_callable=mock_open)
    async def test_add_text_empty_messages(self, mock_file, mock_yaml_dump, mock_yaml_load):
        # Test handling of empty messages file
        mock_yaml_load.return_value = None

        mock_request = MagicMock()
        mock_request.body = AsyncMock(return_value=b"First content")

        result = await add_text("content", mock_request)

        self.assertEqual(result, "Message added")
        expected_data = {"content": ["First content"]}
        mock_yaml_dump.assert_called_with(expected_data, mock_file())