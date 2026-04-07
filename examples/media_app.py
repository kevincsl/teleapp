from teleapp import Button, ButtonResponse, DocumentResponse, LocationResponse, PhotoResponse, TeleApp

app = TeleApp()


@app.command("/where")
async def where(ctx):
    return LocationResponse(text="Taipei", latitude=25.0330, longitude=121.5654)


@app.command("/menu")
async def menu(ctx):
    return ButtonResponse(
        "Choose one",
        buttons=[
            Button("A", "choice:a"),
            Button("B", "choice:b"),
        ],
    )


@app.command("/image")
async def image(ctx):
    return PhotoResponse(text="", file_path="output/demo.png", caption="demo")


@app.command("/file")
async def file(ctx):
    return DocumentResponse(text="", file_path="reports/README.md", caption="report")


@app.message
async def fallback(ctx):
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
