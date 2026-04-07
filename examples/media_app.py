from teleapp import Button, ButtonResponse, DocumentResponse, LocationResponse, PhotoResponse, TeleApp

# Example: first media batch.
# Purpose:
# - demonstrates photo, document, location, sticker, and button handling
# - shows both media input inspection and media output responses
#
# Start:
# - create .env with TELEAPP_TOKEN and TELEAPP_ALLOWED_USER_ID
# - python examples/media_app.py
# - or start_teleapp.bat examples/media_app.py
#
# Stop:
# - Ctrl+C in the terminal running the process

app = TeleApp()


@app.command("/where")
async def where(ctx):
    # Return a Telegram-native location message.
    return LocationResponse(text="Taipei", latitude=25.0330, longitude=121.5654)


@app.command("/menu")
async def menu(ctx):
    # Return an inline keyboard so callback queries can be tested.
    return ButtonResponse(
        "Choose one",
        buttons=[
            Button("A", "choice:a"),
            Button("B", "choice:b"),
        ],
    )


@app.command("/image")
async def image(ctx):
    # Return a photo by local file path. The file must exist when this command is used.
    return PhotoResponse(text="", file_path="output/demo.png", caption="demo")


@app.command("/file")
async def file(ctx):
    # Return a document by local file path.
    return DocumentResponse(text="", file_path="reports/README.md", caption="report")


@app.message
async def fallback(ctx):
    # Inspect the incoming Telegram-native fields before falling back to plain text.
    if ctx.location:
        return f"location: {ctx.location.latitude}, {ctx.location.longitude}"
    if ctx.photos:
        return f"photos: {len(ctx.photos)}"
    if ctx.document:
        return f"document: {ctx.document.file_name or 'unnamed'}"
    if ctx.sticker:
        return f"sticker: {ctx.sticker.emoji or 'unknown'}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
