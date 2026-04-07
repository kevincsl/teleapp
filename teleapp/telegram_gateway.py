from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from teleapp.config import TeleappConfig
from teleapp.protocol import AppEvent
from teleapp.supervisor import AppSupervisor


MESSAGE_LIMIT = 3900


def _clip(text: str) -> str:
    cleaned = (text or "").strip()
    if len(cleaned) <= MESSAGE_LIMIT:
        return cleaned
    return cleaned[: MESSAGE_LIMIT - 3] + "..."


class TelegramGateway:
    def __init__(self, config: TeleappConfig) -> None:
        self._config = config
        self._supervisor = AppSupervisor(config)
        self._consumer_task: asyncio.Task[None] | None = None
        self._custom_commands: set[str] = set()
        self._startup_hook = None
        self._shutdown_hook = None

    def build(self):
        app = ApplicationBuilder().token(self._config.telegram_token).build()
        app.add_handler(CommandHandler("start", self._start_command))
        app.add_handler(CommandHandler("help", self._help_command))
        app.add_handler(CommandHandler("status", self._status_command))
        app.add_handler(CommandHandler("restart", self._restart_command))
        for name in sorted(self._custom_commands):
            app.add_handler(CommandHandler(name, self._custom_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._text_message))
        app.post_init = self._post_init
        app.post_shutdown = self._post_shutdown
        return app

    @property
    def supervisor(self) -> AppSupervisor:
        return self._supervisor

    def set_custom_commands(self, names: set[str]) -> None:
        reserved = {"start", "help", "status", "restart"}
        self._custom_commands = {name for name in names if name not in reserved}

    def set_lifecycle_hooks(self, startup_hook, shutdown_hook) -> None:
        self._startup_hook = startup_hook
        self._shutdown_hook = shutdown_hook

    async def _post_init(self, app) -> None:
        if self._startup_hook is not None:
            await self._startup_hook()
        await self._supervisor.start()
        self._consumer_task = asyncio.create_task(self._event_consumer(app))

    async def _post_shutdown(self, app) -> None:
        if self._consumer_task is not None:
            self._consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._consumer_task
        await self._supervisor.stop()
        if self._shutdown_hook is not None:
            await self._shutdown_hook()

    def _is_allowed(self, update: Update) -> bool:
        user = update.effective_user
        return bool(user and user.id == self._config.allowed_user_id)

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        await update.message.reply_text(
            _clip(
                "\n".join(
                    [
                        "teleapp",
                        "/status",
                        "/restart",
                        "",
                        "Send any text to forward it to the hosted app.",
                    ]
                )
            )
        )

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self._start_command(update, context)

    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        state = self._supervisor.state
        lines = [
            f"running: {'yes' if state.running else 'no'}",
            f"pid: {state.pid or '-'}",
            f"app: {self._config.app_path}",
            f"busy: {'yes' if state.busy else 'no'}",
            f"active_chat_id: {state.active_chat_id or '-'}",
            f"active_request_id: {state.active_request_id or '-'}",
            f"queued_requests: {state.total_queued_requests}",
            f"last_restart_reason: {state.last_restart_reason or '-'}",
            f"last_error: {state.last_error or '-'}",
        ]
        for session in sorted(state.chat_sessions.values(), key=lambda item: item.chat_id):
            lines.append(
                f"chat {session.chat_id}: queued={session.queued_requests} active={session.active_request_id or '-'}"
            )
        await update.message.reply_text(_clip("\n".join(lines)))

    async def _restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        await self._supervisor.restart("manual /restart")
        await update.message.reply_text("Hosted app restarted.")

    async def _text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        message = update.message
        if message is None:
            return
        await self._supervisor.send_text(chat_id=update.effective_chat.id, text=message.text or "")

    async def _custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not self._is_allowed(update):
            return
        message = update.message
        if message is None:
            return
        command_name = ""
        if message.text:
            command_name = message.text.split()[0].lstrip("/").split("@", 1)[0].strip().lower()
        payload = ""
        if message.text:
            parts = message.text.split(maxsplit=1)
            if len(parts) > 1:
                payload = parts[1]
        await self._supervisor.send_text(
            chat_id=update.effective_chat.id,
            text=payload,
            command=command_name,
        )

    async def _event_consumer(self, app) -> None:
        while True:
            event = await self._supervisor.next_event()
            target_chat_id = event.chat_id or self._config.telegram_chat_id
            if not target_chat_id:
                continue
            await app.bot.send_message(chat_id=target_chat_id, text=_clip(self._render_event(event)))

    @staticmethod
    def _render_event(event: AppEvent) -> str:
        if event.type == "output":
            return event.text
        if event.type == "status":
            return f"[status] {event.text}"
        if event.type == "error":
            return f"[error] {event.text}"
        return f"[{event.type}] {event.text}"


import contextlib
