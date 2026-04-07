# teleapp Architecture

## Overview

`teleapp` is a Telegram-hosted Python app runtime.

The runtime has one job: connect Telegram input to a hosted application while supervising lifecycle, queueing, restart, and reload behavior.

There are two execution modes:

1. subprocess mode
2. in-process mode

## Main components

### `teleapp.app`

The high-level public facade.

Responsibilities:

- exposes the public framework API
- stores handlers, routes, and hooks
- resolves dispatch priority
- attaches the final dispatch callable to the runtime supervisor

### `teleapp.telegram_gateway`

The Telegram polling adapter.

Responsibilities:

- configures command handlers
- validates the allowed Telegram user
- forwards plain text and custom commands into the supervisor
- relays events from the supervisor back to Telegram

### `teleapp.supervisor`

The runtime core.

Responsibilities:

- owns process state
- owns per-chat queues
- serializes execution across chats
- manages restart behavior
- coordinates hot reload
- emits normalized events

### `teleapp.runner`

Subprocess transport for hosted apps.

Responsibilities:

- starts the hosted process
- writes requests to `stdin`
- reads `stdout` and `stderr`
- emits events tagged with process identity

### `teleapp.protocol`

Subprocess JSONL protocol helpers.

Responsibilities:

- encode input events
- decode output lines
- normalize `chat_id`, `request_id`, and event type

### `teleapp.response`

Framework-level response abstraction for in-process mode.

Responsibilities:

- define response classes
- convert handler return values into runtime events

### `teleapp.hot_reload`

Polling-based file watcher.

Responsibilities:

- watch tracked `*.py` files
- debounce changes
- request restart only after the quiet window

## Dispatch flow

### Inbound flow

1. Telegram receives text or command.
2. `telegram_gateway` validates the user.
3. The gateway calls `supervisor.send_text(...)`.
4. The supervisor enqueues the request by chat id.
5. If no request is active, the supervisor dispatches the next request.

### In-process dispatch

1. Build `MessageContext`
2. Run `before_message` hooks
3. Try command handler
4. Try route handlers
5. Fall back to default message handler
6. Normalize the result via `response.py`
7. Run `after_message` hooks
8. Emit final event

### Subprocess dispatch

1. Build input JSON
2. Write line to process `stdin`
3. Read process `stdout` / `stderr`
4. Decode line into `AppEvent`
5. Route event back to Telegram

## Dispatch priority

Current priority is fixed:

1. command handler
2. route handler
3. default message handler

Hooks wrap the resolved handler:

- `before_message` before dispatch
- `after_message` after response normalization
- `on_error` when dispatch raises

## Queue model

The queue model is intentionally conservative:

- one queue per chat
- one active request globally
- per-chat ordering preserved
- cross-chat execution serialized

This matches the assumption that one hosted app instance is active at a time.

## Restart model

### Manual restart

- `restart("manual /restart")`
- if idle: restart immediately
- if busy: queue the restart reason and defer until no requests are active

### Hot reload restart

- file change detected by `hot_reload`
- quiet window elapses
- restart is requested
- if busy: restart is deferred

### Crash auto-restart

- subprocess exits with non-zero code
- if exit was not expected
- and `auto_restart_on_crash` is enabled
- restart after backoff

## Process identity rule

Subprocess exit events are tagged with the originating pid.

The supervisor ignores stale exit events from old processes after a restart.

This rule is important and should not be removed without replacing it with an equally explicit identity check.

## Configuration sources

Priority order:

1. explicit runtime overrides
2. CLI args
3. `.env` / environment variables
4. defaults

The recommended user path is `.env`, not hardcoded credentials.

## Public API boundary

Safe public imports:

- `teleapp`
- `teleapp.app`
- `teleapp.config`
- `teleapp.context`
- `teleapp.protocol`
- `teleapp.response`

Internal modules:

- `teleapp.runner`
- `teleapp.supervisor`
- `teleapp.telegram_gateway`
- `teleapp.hot_reload`
- `teleapp.state`
- `teleapp.scaffold`

## Current limitations

- one hosted app instance
- one allowed Telegram user
- no media/file transport
- no persistent session replay
- no watchdog-based reloader yet
- no completed real Telegram soak test yet
