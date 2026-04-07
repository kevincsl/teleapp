from teleapp import AudioResponse, StickerResponse, TeleApp, VoiceResponse

# Example: second media batch.
# Purpose:
# - demonstrates voice, audio, and sticker handling
# - shows both Telegram-native input inspection and media output responses
#
# Start:
# - create .env with TELEAPP_TOKEN and TELEAPP_ALLOWED_USER_ID
# - python examples/media_audio_app.py
# - or start_teleapp.bat examples/media_audio_app.py
#
# Stop:
# - Ctrl+C in the terminal running the process

app = TeleApp()


@app.command("/voice")
async def voice(ctx):
    # Return a voice message by local file path.
    return VoiceResponse(text="", file_path="output/demo.ogg", caption="voice demo")


@app.command("/audio")
async def audio(ctx):
    # Return an audio file by local file path.
    return AudioResponse(text="", file_path="output/demo.mp3", caption="audio demo")


@app.command("/sticker")
async def sticker(ctx):
    # Return a sticker by Telegram sticker file id.
    return StickerResponse(sticker="sticker-file-id")


@app.message
async def fallback(ctx):
    # Inspect incoming voice/audio/sticker payloads.
    if ctx.voice:
        return f"voice duration: {ctx.voice.duration}"
    if ctx.audio:
        return f"audio file: {ctx.audio.file_name or 'unknown'}"
    if ctx.sticker:
        return f"sticker emoji: {ctx.sticker.emoji or 'unknown'}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
