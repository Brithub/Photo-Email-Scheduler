import os
import uuid
from unittest.mock import patch, MagicMock

import yaml

from email_sender import (
    send_message,
    get_or_init_messages,
)


def test_get_or_init_messages():
    messages_path = f"/tmp/{uuid.uuid4()}/messages.yml"
    messages = get_or_init_messages(messages_path)

    assert len(messages.subjects) == 3

    existing_data = {
        "subjects": ["Subject 1", "Subject 2", "Subject 3", "Subject 4"],
        "contents": ["Content 1", "Content 2", "Content 3"],
        "responses": ["Response 1", "Response 2", "Response 3"],
    }

    with open(messages_path, "w") as yaml_file:
        yaml.dump(existing_data, yaml_file, default_flow_style=False)

    messages = get_or_init_messages(messages_path)
    assert len(messages.subjects) == 4


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
