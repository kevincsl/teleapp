# teleapp examples

This folder contains runnable examples for the `teleapp` framework.

## Shared start method

All in-process examples use the same startup pattern:

1. Create `.env` in the `teleapp` project root
2. Fill in:

```env
TELEAPP_TOKEN=<telegram-bot-token>
TELEAPP_ALLOWED_USER_ID=<telegram-user-id>
```

3. Start one example:

Windows:

```powershell
python examples/<example>.py
```

or

```powershell
start_teleapp.bat examples/<example>.py
```

Linux/macOS:

```bash
python examples/<example>.py
```

or

```bash
./start_teleapp.sh examples/<example>.py
```

## Shared stop method

Stop any running example by:

- pressing `Ctrl+C` in the terminal
- closing the terminal window that started the process

`/restart` only restarts the runtime. It does not permanently stop it.

## Example list

### `echo_app.py`

- type: subprocess contract example
- purpose: validates the low-level JSONL stdin/stdout protocol
- note: used by tests and stability probes

### `hello_app.py`

- type: minimal decorator-based example
- purpose: simplest in-process text app and the recommended first learning example

### `media_app.py`

- type: first media batch example
- purpose: photo, document, location, sticker, and button handling

### `media_audio_app.py`

- type: second media batch example
- purpose: voice, audio, and sticker handling

### `media_misc_app.py`

- type: third media batch example
- purpose: video, poll, and contact handling

### `media_ai_app.py`

- type: AI-oriented media example
- purpose: animation and venue handling

### `callback_app.py`

- type: callback query example
- purpose: inline button output and callback query input flow
