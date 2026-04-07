# teleapp Plan

## Positioning

`teleapp` is not a Telegram bot wrapper and not a web framework clone.

It is a runtime that hosts a local Python app behind Telegram:

- Telegram is the transport layer
- `app.py` is the hosted program
- the runtime bridges stdin/stdout/stderr
- the runtime supervises the hosted process
- file changes trigger hot reload

The hosted app should not need to know about Telegram, process lifecycle, or restart logic.

## Core Contract

The first version uses a simple process contract:

- input comes from `stdin`
- normal output goes to `stdout`
- error output goes to `stderr`
- line buffering or explicit flush is required

The transport protocol should be JSONL rather than raw text.

Example:

```json
{"type":"input","text":"hello"}
{"type":"output","text":"world"}
{"type":"status","text":"processing"}
{"type":"error","text":"something failed"}
```

## Runtime Responsibilities

`teleapp` is responsible for:

- receiving Telegram messages
- validating allowed users or chats
- starting and stopping the hosted app
- writing user input into the app process
- reading stdout and stderr continuously
- forwarding app events back to Telegram
- watching files and restarting the app on change
- reporting runtime status

## Hosted App Responsibilities

The hosted app is responsible for:

- reading input events
- producing output events
- flushing output promptly
- keeping domain logic separate from transport logic

The hosted app should not:

- call the Telegram API directly
- self-restart
- manage file watching
- manage process supervision

## MVP Scope

The first milestone should include only:

- one hosted app entrypoint
- Telegram polling transport
- text input to app stdin
- app stdout back to Telegram
- app stderr back to Telegram
- `/status`
- `/restart`
- file watch with debounce
- automatic restart after app file changes

The first milestone should exclude:

- multiple hosted apps
- media and file pipelines
- webhook deployment
- multi-chat isolation beyond a basic whitelist
- plugin architecture

## Suggested Package Layout

```text
teleapp/
  teleapp/
    __init__.py
    cli.py
    config.py
    protocol.py
    runner.py
    supervisor.py
    hot_reload.py
    telegram_gateway.py
    state.py
  examples/
    echo_app.py
  pyproject.toml
  .env.example
  README.md
```

## Module Roles

- `protocol.py`
  Defines JSONL message schema and encode/decode helpers.

- `runner.py`
  Starts the hosted app and manages stdin/stdout/stderr.

- `supervisor.py`
  Owns process lifecycle, restart policy, and crash recovery.

- `hot_reload.py`
  Watches files with debounce and requests a supervised restart.

- `telegram_gateway.py`
  Handles Telegram polling, commands, and message delivery.

- `state.py`
  Stores runtime state such as pid, busy status, last error, and last restart time.

- `cli.py`
  Provides a command such as `teleapp run examples/echo_app.py`.

## Naming Decision

Project name:

- `teleapp`

Reason:

- it describes a Telegram-hosted application runtime better than a generic bot name
- it matches the future role of `app.py`
- it can grow into a reusable framework instead of staying tied to the current `tgrobot` naming

## Implementation Order

1. Create the `teleapp` project skeleton.
2. Implement `protocol.py`.
3. Implement `runner.py`.
4. Implement `telegram_gateway.py`.
5. Add `hot_reload.py`.
6. Add `examples/echo_app.py`.
7. Document setup and runtime flow.
