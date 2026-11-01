import os
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml


@dataclass
class MessagesResponse:
    subjects: list[str]
    contents: list[str]
    responses: list[str]
    statuses: list[str]


def read_saved_messages() -> MessagesResponse:

    # initialization route
    messages_path = os.environ.get("META_DIRECTORY", "/tmp") + "/messages.yml"
    if not os.path.exists(messages_path):
        Path(messages_path).parent.mkdir(exist_ok=True, parents=True)
        with open(messages_path, "w") as f:
            yaml.dump({}, f)

    loaded_messages = yaml.safe_load(open(messages_path))
    messages = MessagesResponse(
        subjects=loaded_messages.get("subjects", []),
        contents=loaded_messages.get("contents", []),
        responses=loaded_messages.get("responses", []),
        statuses=loaded_messages.get("statuses", []),
    )

    return messages


def write_message(message_text: str, message_type: str) -> None:

    all_messages = read_saved_messages()

    setattr(
        all_messages,
        message_type,
        getattr(all_messages, message_type).append(message_text),
    )

    # write the new messages to the file
    messages_path = os.environ.get("META_DIRECTORY", "/tmp") + "/messages.yml"
    with open(messages_path, "w") as file:
        yaml.dump(asdict(all_messages), file)
