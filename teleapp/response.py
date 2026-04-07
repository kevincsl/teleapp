from __future__ import annotations

from dataclasses import dataclass

from teleapp.context import MessageContext
from teleapp.protocol import AppEvent


@dataclass(slots=True)
class Response:
    text: str
    event_type: str = "output"

    def to_event(self, ctx: MessageContext) -> AppEvent:
        return AppEvent(
            type=self.event_type,
            text=self.text,
            chat_id=ctx.chat_id,
            request_id=ctx.request_id,
            stream="inprocess",
        )


@dataclass(slots=True)
class TextResponse(Response):
    event_type: str = "output"


@dataclass(slots=True)
class StatusResponse(Response):
    event_type: str = "status"


@dataclass(slots=True)
class ErrorResponse(Response):
    event_type: str = "error"


def coerce_response(result, ctx: MessageContext) -> AppEvent:
    if isinstance(result, AppEvent):
        return result
    if isinstance(result, Response):
        return result.to_event(ctx)
    if result is None:
        return StatusResponse("handler completed").to_event(ctx)
    return TextResponse(str(result)).to_event(ctx)
