from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MessageContext:
    chat_id: int
    text: str
    request_id: str | None = None
    command: str | None = None
