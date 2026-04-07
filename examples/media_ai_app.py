from teleapp import AnimationResponse, TeleApp, VenueResponse

app = TeleApp()


@app.command("/gif")
async def gif(ctx):
    return AnimationResponse(text="", file_path="output/demo.gif", caption="animation demo")


@app.command("/place")
async def place(ctx):
    return VenueResponse(
        text="",
        latitude=25.0330,
        longitude=121.5654,
        title="Taipei 101",
        address="Xinyi District, Taipei",
    )


@app.message
async def fallback(ctx):
    if ctx.animation:
        return f"animation file: {ctx.animation.file_name or 'unknown'}"
    if ctx.venue:
        return f"venue: {ctx.venue.title}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
