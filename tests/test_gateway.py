from __future__ import annotations

import unittest
from argparse import Namespace
from types import SimpleNamespace

from teleapp.config import load_config
from teleapp.protocol import AppEvent
from teleapp.state import ChatSessionState
from teleapp.telegram_gateway import TelegramGateway


class DummyMessage:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.sent.append(text)


class GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.config = load_config(
            Namespace(
                app="examples/echo_app.py",
                token="dummy",
                allowed_user_id=1,
                chat_id=1,
                python_executable="python",
                no_hot_reload=True,
                reload_quiet_seconds=2,
                reload_poll_seconds=1,
                watch=[],
            )
        )

    def test_render_event_formats_known_types(self) -> None:
        self.assertEqual(TelegramGateway._render_event(AppEvent(type="output", text="ok")), "ok")
        self.assertEqual(TelegramGateway._render_event(AppEvent(type="status", text="up")), "[status] up")
        self.assertEqual(TelegramGateway._render_event(AppEvent(type="error", text="bad")), "[error] bad")

    async def test_status_command_includes_queue_summary(self) -> None:
        gateway = TelegramGateway(self.config)
        state = gateway.supervisor.state
        state.running = True
        state.pid = 321
        state.busy = True
        state.active_chat_id = 7
        state.active_request_id = "7-1"
        state.total_queued_requests = 2
        state.last_restart_reason = "queued: file changed"
        state.last_error = "none"
        state.chat_sessions[7] = ChatSessionState(chat_id=7, queued_requests=1, active_request_id="7-1")
        state.chat_sessions[8] = ChatSessionState(chat_id=8, queued_requests=1, active_request_id=None)

        message = DummyMessage()
        update = SimpleNamespace(
            effective_user=SimpleNamespace(id=1),
            effective_chat=SimpleNamespace(id=1),
            message=message,
        )

        await gateway._status_command(update, None)
        self.assertEqual(len(message.sent), 1)
        body = message.sent[0]
        self.assertIn("running: yes", body)
        self.assertIn("active_chat_id: 7", body)
        self.assertIn("queued_requests: 2", body)
        self.assertIn("chat 7: queued=1 active=7-1", body)
        self.assertIn("chat 8: queued=1 active=-", body)


if __name__ == "__main__":
    unittest.main()
