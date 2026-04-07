# teleapp LLM Memory

This file is for future maintainers and LLMs. It should be read before making architectural changes.

## Project identity

`teleapp` is a Telegram-hosted Python app runtime with a Flask-like API.

It is not:

- a web framework
- a webhook server
- a multi-app orchestrator

It is:

- a runtime that accepts Telegram input
- a dispatcher that forwards requests into a hosted app
- a supervisor that manages process lifecycle, reload, and restart behavior

## Supported hosting modes

There are two valid hosting modes.

### 1. Subprocess mode

- hosted app is a Python file
- communication is JSONL over `stdin/stdout`
- `runner.py` owns process pipes
- `supervisor.py` owns queueing and restart logic

### 2. In-process mode

- hosted app is a callable or handler object
- `TeleApp` attaches it directly
- `supervisor.py` dispatches it without spawning a subprocess
- results are normalized through `response.py`

## Framework-style API surface

The intended high-level user API is:

- `TeleApp()`
- `app.message`
- `app.command("/name")`
- `app.route(predicate)`
- `app.before_message`
- `app.after_message`
- `app.on_error`
- `app.on_startup`
- `app.on_shutdown`
- `app.attach_callable(...)`
- `app.attach_handler(...)`
- `app.run(...)`

Anything below that is an implementation detail unless explicitly promoted.

## Public vs internal modules

Public:

- `teleapp`
- `teleapp.app`
- `teleapp.config`
- `teleapp.context`
- `teleapp.protocol`
- `teleapp.response`

Internal:

- `teleapp.runner`
- `teleapp.supervisor`
- `teleapp.telegram_gateway`
- `teleapp.hot_reload`
- `teleapp.state`
- `teleapp.scaffold`

Do not casually expand the public API. If something can stay internal, keep it internal.

## Dispatch rules

Current dispatch priority:

1. command handler
2. route handler
3. default message handler

Hooks:

- `before_message` run before handler selection result is executed
- `after_message` run after response normalization
- `on_error` run when dispatch raises

If this order changes, update both tests and README.

## Queue model

Current queue/session design:

- one queue per chat
- one active request globally
- per-chat ordering is preserved
- all chats share one execution lane

This design is intentional because the runtime still assumes one hosted app instance.

If future work introduces parallel execution, this is a major architectural change and should not be done casually.

## Stability rules already implemented

- stale process exit events are ignored using process identity
- reload is deferred while requests are active
- crash auto-restart exists for subprocess mode
- crash backoff is configurable

Important:

- the system has unit-level stability checks
- it does not yet have real-world Telegram soak testing
- it does not yet have real-world live-edit filesystem stress testing

Manual stability helper scripts now exist:

- `scripts/run_soak.py`
- `scripts/run_reload_probe.py`
- `scripts/run_telegram_smoke.py`
- `scripts/build_report_index.py`

If these scripts change, update both `README.md` and this file.

## Config philosophy

Default configuration should come from `.env` / environment variables.

Do not encourage users to hardcode:

- Telegram token
- allowed user id
- runtime app path

The code should keep supporting explicit overrides, but docs should prefer `.env`.

## Response philosophy

Handlers may return:

- `str`
- `None`
- `Response`
- `TextResponse`
- `StatusResponse`
- `ErrorResponse`
- `AppEvent`

If richer output types are added later, extend `response.py` rather than scattering coercion logic.

## Files most likely to need coordinated edits

When changing framework behavior, these files usually need to move together:

- `teleapp/app.py`
- `teleapp/supervisor.py`
- `teleapp/telegram_gateway.py`
- `teleapp/response.py`
- `README.md`
- `tests/test_app.py`
- `tests/test_gateway.py`
- `tests/test_supervisor.py`

## Current missing work

Not complete yet:

- real Telegram integration stress testing
- long-running soak tests
- media/file response model
- watchdog-based hot reload alternative
- persistent session storage

These are natural next phases, but none should be merged into unrelated refactors.

## Maintenance rule

Prefer making the framework more explicit rather than more magical.

Good direction:

- clearer API boundaries
- stricter response types
- explicit hook order
- stronger tests

Bad direction:

- hidden side effects
- expanding public API without documentation
- bypassing queue/session rules in ad hoc ways
