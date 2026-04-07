# teleapp

`teleapp` is a Telegram-hosted Python app runtime with a Flask-like programming model.

The project lets you write local Python apps that behave like Telegram services without teaching those apps about the Telegram Bot API directly.

At this stage, `teleapp` supports:

- subprocess-hosted apps over `stdin/stdout`
- in-process handlers and decorators
- per-chat request queues
- hot reload with debounce
- crash auto-restart
- `.env`-based configuration
- a small public API surface designed for reuse

## Quick start

### 1. Bootstrap the project

Windows:

```powershell
bootstrap_teleapp.bat
```

Linux/macOS:

```bash
./bootstrap_teleapp.sh
```

### 2. Create `.env`

Start from [`.env.example`](/C:/Users/kevin/codex/tgrobot/teleapp/.env.example) and fill at least:

```env
TELEAPP_TOKEN=<telegram-bot-token>
TELEAPP_ALLOWED_USER_ID=<telegram-user-id>
TELEAPP_APP=examples/echo_app.py
```

### 3. Run the bundled example

Windows:

```powershell
start_teleapp.bat
```

Linux/macOS:

```bash
./start_teleapp.sh
```

The bot will start polling Telegram and forward text into the hosted app.

## Core idea

There are two supported hosting modes.

### Subprocess mode

`teleapp` launches a Python file as a subprocess and talks to it over JSONL:

- input: `stdin`
- output: `stdout`
- errors: `stderr`

Example input:

```json
{"type":"input","chat_id":123,"request_id":"123-1","text":"hello"}
```

Example output:

```json
{"type":"output","chat_id":123,"request_id":"123-1","text":"echo: hello"}
```

### In-process mode

Instead of launching a subprocess, you attach Python callables or handler objects directly to `TeleApp`.

This is the mode that makes the framework feel Flask-like.

## Flask-like usage

### Minimal app

```python
from teleapp import TeleApp

app = TeleApp()


@app.message
async def handle_message(ctx):
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
```

### Command handlers

```python
from teleapp import TeleApp

app = TeleApp()


@app.command("/hello")
async def hello(ctx):
    return f"hello {ctx.text}"


if __name__ == "__main__":
    app.run()
```

### Route handlers

```python
from teleapp import TeleApp

app = TeleApp()


@app.route(lambda ctx: ctx.text.startswith("ping"))
async def ping_route(ctx):
    return "pong"


@app.message
async def fallback(ctx):
    return f"default: {ctx.text}"


if __name__ == "__main__":
    app.run()
```

### Handler object

```python
from teleapp import TeleApp


class MyHandler:
    async def on_text(self, ctx):
        return f"handled: {ctx.text}"


app = TeleApp()
app.attach_handler(MyHandler())


if __name__ == "__main__":
    app.run()
```

## Hooks

The current hook surface:

- `@app.before_message`
- `@app.after_message`
- `@app.on_error`
- `@app.on_startup`
- `@app.on_shutdown`

Example:

```python
from teleapp import TeleApp

app = TeleApp()


@app.on_startup
async def startup():
    print("starting")


@app.before_message
async def before(ctx):
    print("before", ctx.text)


@app.after_message
async def after(ctx, response):
    print("after", response.text)


@app.on_error
async def on_error(ctx, exc):
    print("error", exc)


@app.message
async def handler(ctx):
    return f"echo: {ctx.text}"
```

## Response model

Handlers may return:

- plain `str`
- `None`
- [`Response`](/C:/Users/kevin/codex/tgrobot/teleapp/teleapp/response.py)
- [`TextResponse`](/C:/Users/kevin/codex/tgrobot/teleapp/teleapp/response.py)
- [`StatusResponse`](/C:/Users/kevin/codex/tgrobot/teleapp/teleapp/response.py)
- [`ErrorResponse`](/C:/Users/kevin/codex/tgrobot/teleapp/teleapp/response.py)
- [`AppEvent`](/C:/Users/kevin/codex/tgrobot/teleapp/teleapp/protocol.py)

Examples:

```python
from teleapp import ErrorResponse, StatusResponse, TeleApp, TextResponse

app = TeleApp()


@app.command("/ping")
async def ping(ctx):
    return TextResponse("pong")


@app.command("/noop")
async def noop(ctx):
    return StatusResponse("nothing to do")


@app.command("/fail")
async def fail(ctx):
    return ErrorResponse("something failed")
```

## Configuration

`teleapp` should be configured primarily through `.env`.

Important variables:

- `TELEAPP_TOKEN`
- `TELEAPP_ALLOWED_USER_ID`
- `TELEAPP_CHAT_ID`
- `TELEAPP_APP`
- `TELEAPP_PYTHON`
- `TELEAPP_HOT_RELOAD`
- `TELEAPP_AUTO_RESTART_ON_CRASH`
- `TELEAPP_RELOAD_QUIET_SECONDS`
- `TELEAPP_RELOAD_POLL_SECONDS`
- `TELEAPP_RESTART_BACKOFF_SECONDS`

The full template lives in [`.env.example`](/C:/Users/kevin/codex/tgrobot/teleapp/.env.example).

## Dispatch priority

Current in-process dispatch order is fixed:

1. command handler
2. route handler
3. default message handler

Before and after that:

- all `before_message` hooks run before the selected handler
- all `after_message` hooks run after the handler response is normalized
- `on_error` hooks run if dispatch raises

## Queue and session model

The current runtime uses:

- one global execution lane
- one queue per chat
- preserved ordering within each chat
- serialized dispatch across all chats

This means:

- chat A cannot overtake its own earlier messages
- chat B can queue while chat A is active
- requests are completed one at a time

The current session state is runtime-only and not persisted across restarts.

## Status output

`/status` currently reports:

- running state
- current pid
- configured app path
- busy state
- active chat id
- active request id
- total queued request count
- last restart reason
- last error
- per-chat queue summary

## Stability behavior

Implemented:

- stale exit event protection
- per-chat queue ordering
- deferred reload while requests are active
- crash auto-restart with backoff

Still pending:

- real Telegram integration stress testing
- long-running soak tests outside unit tests
- repeated real filesystem hot reload under live edits

## Public API

Public modules:

- `teleapp`
- `teleapp.app`
- `teleapp.config`
- `teleapp.context`
- `teleapp.protocol`
- `teleapp.response`

Public objects:

- `TeleApp`
- `TeleappConfig`
- `MessageContext`
- `AppEvent`
- `Response`
- `TextResponse`
- `StatusResponse`
- `ErrorResponse`
- `build_parser`
- `build_runtime_config`
- `load_config`
- `encode_input_event`
- `decode_output_line`

Internal runtime modules that should not be imported unless you are extending internals:

- `teleapp.runner`
- `teleapp.supervisor`
- `teleapp.telegram_gateway`
- `teleapp.hot_reload`
- `teleapp.state`
- `teleapp.scaffold`

## Scaffold command

Create a starter app:

```powershell
python -m teleapp init my_teleapp_app
```

This generates:

- `app.py`
- `.env.example`
- `README.md`

## Stability scripts

These scripts are intended for manual or semi-automated stability checks:

- [`scripts/run_soak.py`](/C:/Users/kevin/codex/tgrobot/teleapp/scripts/run_soak.py)
  Runs a larger multi-chat request batch and verifies response ordering.

- [`scripts/run_reload_probe.py`](/C:/Users/kevin/codex/tgrobot/teleapp/scripts/run_reload_probe.py)
  Confirms that a restart changes the hosted process pid.

- [`scripts/run_telegram_smoke.py`](/C:/Users/kevin/codex/tgrobot/teleapp/scripts/run_telegram_smoke.py)
  Verifies `.env` prerequisites before doing a manual Telegram smoke test.

Example:

```powershell
python scripts/run_soak.py --requests 200 --chats 5 --report-dir reports
python scripts/run_reload_probe.py --app examples/echo_app.py
python scripts/run_telegram_smoke.py
python scripts/build_report_index.py
```

`run_soak.py` writes both:

- a JSON report
- a Markdown report

This is intended to support both machine-readable review and human-readable review.

Use [`scripts/build_report_index.py`](/C:/Users/kevin/codex/tgrobot/teleapp/scripts/build_report_index.py) to rebuild:

- `reports/index.json`
- `reports/README.md`

## Project layout

```text
teleapp/
  .env.example
  bootstrap_teleapp.bat
  bootstrap_teleapp.sh
  PLAN.md
  pyproject.toml
  README.md
  scripts/
    build_report_index.py
    run_reload_probe.py
    run_soak.py
    run_telegram_smoke.py
  start_teleapp.bat
  start_teleapp.sh
  examples/
    echo_app.py
  teleapp/
    __init__.py
    __main__.py
    app.py
    cli.py
    config.py
    context.py
    handlers.py
    hot_reload.py
    protocol.py
    response.py
    runner.py
    scaffold.py
    state.py
    supervisor.py
    telegram_gateway.py
  tests/
    test_app.py
    test_config.py
    test_gateway.py
    test_protocol.py
    test_supervisor.py
```

## Testing

Run all tests:

```powershell
python -m unittest discover -s tests -v
```

Current automated coverage includes:

- public facade construction
- config loading and env defaults
- protocol encode/decode
- gateway rendering and status output
- command/route/hook registration
- in-process dispatch behavior
- per-chat queue ordering
- stale exit handling
- crash auto-restart
- reload deferral under in-flight requests
- repeated multi-request stability checks

Manual helper coverage now also exists for:

- soak runs
- restart probes
- Telegram prerequisite smoke checks

## Limitations

Current limitations still worth keeping in mind:

- only one hosted app per runtime process
- only one allowed Telegram user
- no media/file transport yet
- no persistent request replay
- hot reload is still polling-based
- no real-world Telegram soak test has been completed yet

## Read next

- High-level architecture and maintenance memory: [`LLM_MEMORY.md`](/C:/Users/kevin/codex/tgrobot/teleapp/LLM_MEMORY.md)
- Runtime architecture: [`ARCHITECTURE.md`](/C:/Users/kevin/codex/tgrobot/teleapp/ARCHITECTURE.md)
- Operational runbook: [`OPERATIONS.md`](/C:/Users/kevin/codex/tgrobot/teleapp/OPERATIONS.md)
- Historical design direction: [`PLAN.md`](/C:/Users/kevin/codex/tgrobot/teleapp/PLAN.md)
