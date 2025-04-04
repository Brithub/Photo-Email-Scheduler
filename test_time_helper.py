import unittest
from unittest.mock import patch, mock_open
import datetime
import os
from time_helper import user_timezone, now

class TestTimeHelper(unittest.TestCase):

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="+0800\n")
    def test_user_timezone_existing_file(self, mock_file, mock_exists):
        # Test timezone reading from file
        mock_exists.return_value = True
        tz = user_timezone("test_user")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=8))
        mock_exists.assert_called_with(os.path.dirname(os.path.realpath(__file__)) + "/timezones/test_user")

    @patch('os.path.exists')
    def test_user_timezone_no_file(self, mock_exists):
        # Test default timezone when no file exists
        mock_exists.return_value = False
        tz = user_timezone("test_user")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="invalid")
    def test_user_timezone_invalid_file(self, mock_file, mock_exists):
        # Test error handling with invalid timezone format
        mock_exists.return_value = True
        tz = user_timezone("test_user")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5))

    @patch('time_helper.user_timezone')
    @patch('datetime.datetime')
    def test_now_function(self, mock_datetime, mock_user_timezone):
        # Test the now function uses the correct timezone
        mock_tz = datetime.timezone(datetime.timedelta(hours=2))
        mock_user_timezone.return_value = mock_tz
        mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=mock_tz)
        mock_datetime.now.return_value = mock_now

        result = now("test_user")

        mock_user_timezone.assert_called_with("test_user")
        mock_datetime.now.assert_called_with(mock_tz)
        self.assertEqual(result, mock_now)