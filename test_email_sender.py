import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import random
import datetime
import yaml
import smtplib
from email_sender import (
    get_or_init_messages,
    send_message,
    pick_time,
    schedule_message,
    main,
    user_map,
)


class TestEmailSender(unittest.TestCase):

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.dump")
    def test_get_or_init_messages_no_file(self, mock_yaml_dump, mock_file, mock_exists):
        # Test creating new messages.yml file
        mock_exists.return_value = False

        result = get_or_init_messages()

        mock_yaml_dump.assert_called_once()
        self.assertIn("subject", result)
        self.assertIn("content", result)
        self.assertIn("response", result)

    @patch("os.path.exists")
    @patch("yaml.safe_load")
    @patch("builtins.open", new_callable=mock_open)
    def test_get_or_init_messages_existing_file(
        self, mock_file, mock_yaml_load, mock_exists
    ):
        # Test loading existing messages.yml
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "subject": ["Test subject"],
            "content": ["Test content"],
            "response": ["Test response"],
        }

        result = get_or_init_messages()

        mock_yaml_load.assert_called_once()
        self.assertEqual(result["subject"], ["Test subject"])
        self.assertEqual(result["content"], ["Test content"])
        self.assertEqual(result["response"], ["Test response"])

    @patch("os.getenv")
    @patch("smtplib.SMTP")
    @patch("email_sender.get_or_init_messages")
    @patch("random.choice")
    def test_send_message(self, mock_choice, mock_get_messages, mock_smtp, mock_getenv):
        # Test sending an email
        mock_get_messages.return_value = {
            "subject": ["Test subject"],
            "content": ["Test content"],
        }
        mock_choice.side_effect = ["Test subject", "Test content"]

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_message("test@example.com")

        mock_server.ehlo.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            "sammie.b.automation@gmail.com", "test_password"
        )
        mock_server.sendmail.assert_called_once()

    @patch("os.getenv")
    @patch("smtplib.SMTP")
    @patch("email_sender.get_or_init_messages")
    @patch("random.choice")
    def test_send_message_fallback_password(
        self, mock_choice, mock_get_messages, mock_smtp, mock_getenv
    ):
        # Test password fallback to environment variable
        mock_getenv.return_value = "env_password"
        mock_get_messages.return_value = {
            "subject": ["Test subject"],
            "content": ["Test content"],
        }
        mock_choice.side_effect = ["Test subject", "Test content"]

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        send_message("test@example.com")

        mock_server.login.assert_called_once_with(
            "sammie.b.automation@gmail.com", "env_password"
        )

    @patch("email_sender.user_timezone")
    @patch("email_sender.now")
    @patch("random.random")
    @patch("random.randint")
    def test_pick_time_weekday_early(
        self, mock_randint, mock_random, mock_now, mock_user_timezone
    ):
        # Test pick_time on weekday with early start (9am)
        mock_tz = datetime.timezone(datetime.timedelta(hours=-5))
        mock_user_timezone.return_value = mock_tz
        mock_now.return_value = MagicMock(weekday=lambda: 1)  # Tuesday
        mock_random.return_value = 0.95  # > 0.9, so use 9am start time
        mock_randint.side_effect = [10, 30]  # hour=10, minute=30

        result = pick_time("test_user")

        self.assertEqual(result.hour, 10)
        self.assertEqual(result.minute, 30)
        self.assertEqual(result.tzinfo, mock_tz)

    @patch("email_sender.user_timezone")
    @patch("email_sender.now")
    @patch("random.random")
    @patch("random.randint")
    def test_pick_time_weekday_regular(
        self, mock_randint, mock_random, mock_now, mock_user_timezone
    ):
        # Test pick_time on weekday with regular start (5pm)
        mock_tz = datetime.timezone(datetime.timedelta(hours=-5))
        mock_user_timezone.return_value = mock_tz
        mock_now.return_value = MagicMock(weekday=lambda: 1)  # Tuesday
        mock_random.return_value = 0.5  # <= 0.9, so use 5pm start time
        mock_randint.side_effect = [19, 15]  # hour=19, minute=15

        result = pick_time("test_user")

        self.assertEqual(result.hour, 19)
        self.assertEqual(result.minute, 15)
        self.assertEqual(result.tzinfo, mock_tz)

    @patch("email_sender.user_timezone")
    @patch("email_sender.now")
    @patch("random.randint")
    def test_pick_time_weekend(self, mock_randint, mock_now, mock_user_timezone):
        # Test pick_time on weekend
        mock_tz = datetime.timezone(datetime.timedelta(hours=-5))
        mock_user_timezone.return_value = mock_tz
        mock_now.return_value = MagicMock(weekday=lambda: 5)  # Saturday
        mock_randint.side_effect = [14, 45]  # hour=14, minute=45

        result = pick_time("test_user")

        self.assertEqual(result.hour, 14)
        self.assertEqual(result.minute, 45)
        self.assertEqual(result.tzinfo, mock_tz)

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("email_sender.now")
    @patch("email_sender.pick_time")
    @patch("time.sleep")
    def test_schedule_message_new_schedule(
        self,
        mock_sleep,
        mock_pick_time,
        mock_now,
        mock_file,
        mock_makedirs,
        mock_exists,
    ):
        # Test schedule_message creating a new schedule
        # Set up to break after first iteration
        mock_sleep.side_effect = Exception("Stop loop")

        mock_now.return_value = MagicMock(
            year=2023, month=1, day=1, time=lambda: datetime.time(8, 0)
        )

        # First check if schedule exists for each user (no), then break
        mock_exists.side_effect = [False, False]

        mock_pick_time.return_value = datetime.time(17, 30)  # 5:30pm

        with self.assertRaises(Exception):
            schedule_message()

        self.assertEqual(mock_makedirs.call_count, 2)  # One for each user
        self.assertEqual(mock_file.call_count, 2)  # One for each user
