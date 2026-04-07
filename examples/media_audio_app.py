from teleapp import AudioResponse, StickerResponse, TeleApp, VoiceResponse

app = TeleApp()


@app.command("/voice")
async def voice(ctx):
    return VoiceResponse(text="", file_path="output/demo.ogg", caption="voice demo")


@app.command("/audio")
async def audio(ctx):
    return AudioResponse(text="", file_path="output/demo.mp3", caption="audio demo")


@app.command("/sticker")
async def sticker(ctx):
    return StickerResponse(sticker="sticker-file-id")


@app.message
async def fallback(ctx):
    if ctx.voice:
        return f"voice duration: {ctx.voice.duration}"
    if ctx.audio:
        return f"audio file: {ctx.audio.file_name or 'unknown'}"
    if ctx.sticker:
        return f"sticker emoji: {ctx.sticker.emoji or 'unknown'}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
