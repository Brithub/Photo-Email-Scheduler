import os
from unittest.mock import patch, MagicMock

from email_sender import (
    send_message,
)


@patch("smtplib.SMTP")
def test_send_message(mock_smtp):
    # Test sending an email
    os.environ["GMAIL_AUTOMATION_PASSWORD"] = "test_password"

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    send_message("test@example.com")

    mock_server.ehlo.assert_called_once()
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(
        "sammie.b.automation@gmail.com", "test_password"
    )
    mock_server.sendmail.assert_called_once()
