# teleapp Operations

## Purpose

This document is for running and verifying `teleapp` in practice.

It focuses on:

- setup
- startup
- local verification
- restart and reload checks
- manual Telegram smoke checks

## Environment

Use `.env` for configuration.

Minimum required values:

```env
TELEAPP_TOKEN=<telegram-bot-token>
TELEAPP_ALLOWED_USER_ID=<telegram-user-id>
TELEAPP_APP=examples/echo_app.py
```

Recommended optional values:

```env
TELEAPP_HOT_RELOAD=1
TELEAPP_AUTO_RESTART_ON_CRASH=1
TELEAPP_RELOAD_QUIET_SECONDS=2
TELEAPP_RESTART_BACKOFF_SECONDS=1
TELEAPP_WATCH_MODE=app-dir
```

## Bootstrap

Windows:

```powershell
bootstrap_teleapp.bat
```

Linux/macOS:

```bash
./bootstrap_teleapp.sh
```

## Start the runtime

Windows:

```powershell
start_teleapp.bat
```

Linux/macOS:

```bash
./start_teleapp.sh
```

To override the hosted app:

```powershell
start_teleapp.bat examples/echo_app.py
```

## Core verification steps

### 1. Package test suite

```powershell
python -m unittest discover -s tests -v
```

### 2. Soak script

```powershell
python scripts/run_soak.py --requests 200 --chats 5 --report-dir reports
python scripts/build_report_index.py
```

Expected result:

- request ordering preserved
- no queue leak
- no busy flag stuck at the end
- JSON and Markdown reports written under `reports/`
- index files refreshed under `reports/`

### 3. Restart probe

```powershell
python scripts/run_reload_probe.py --app examples/echo_app.py
```

Expected result:

- pid changes after restart

### 4. Telegram smoke prerequisites

```powershell
python scripts/run_telegram_smoke.py
```

Expected result:

- no missing env variables
- hosted app path resolves

### 5. Manual Telegram smoke test

1. Start `teleapp`
2. Send `/start`
3. Send a plain text message
4. Confirm response arrives
5. Send `/status`
6. Confirm runtime summary is sensible
7. Send `/restart`
8. Confirm runtime restarts and still responds

## Hot reload check

To manually test hot reload:

1. Start `teleapp`
2. Edit the hosted app source file
3. Save the file
4. Wait for the quiet window to expire
5. Confirm the hosted app restarts
6. Send another Telegram message and confirm behavior still works

Default watch semantics:

- `TELEAPP_APP` is the process that gets restarted
- `TELEAPP_WATCH_MODE=app-dir` means the hosted app directory is watched
- `TELEAPP_WATCH_MODE=app-file-only` means only the hosted app file is watched

## Crash auto-restart check

To manually test crash handling:

1. Use a subprocess-hosted app
2. Make the hosted app exit with a non-zero code after one request
3. Send a request
4. Confirm `/status` or logs show a crash
5. Confirm the hosted app restarts after backoff

## Troubleshooting

### Bot does not respond

Check:

- token is valid
- allowed user id is correct
- hosted app path exists
- the hosted app flushes output

### Hosted app looks stuck

Check:

- active request id in `/status`
- queued request count in `/status`
- whether the hosted app is still running

### Reload does not happen

Check:

- `TELEAPP_HOT_RELOAD=1`
- watched path includes the modified file
- file extension is `*.py`
- quiet window has elapsed

### Crash does not restart

Check:

- subprocess mode is being used
- exit code is non-zero
- `TELEAPP_AUTO_RESTART_ON_CRASH=1`
- `TELEAPP_RESTART_BACKOFF_SECONDS` is not extremely large

## Recommended future operational checks

Still needed outside the current automated suite:

- long-running real Telegram soak test
- real filesystem live-edit stress test
- network interruption behavior
- bot restart behavior while requests are queued
