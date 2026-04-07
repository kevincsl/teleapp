from teleapp import ContactResponse, PollResponse, TeleApp, VideoResponse

app = TeleApp()


@app.command("/video")
async def video(ctx):
    return VideoResponse(text="", file_path="output/demo.mp4", caption="video demo")


@app.command("/contact")
async def contact(ctx):
    return ContactResponse(text="", phone_number="123456789", first_name="Kevin", last_name="Lin")


@app.command("/poll")
async def poll(ctx):
    return PollResponse(text="", question="Choose one", options=["A", "B"], allows_multiple_answers=False)


@app.message
async def fallback(ctx):
    if ctx.video:
        return f"video duration: {ctx.video.duration}"
    if ctx.contact:
        return f"contact: {ctx.contact.first_name}"
    if ctx.poll:
        return f"poll: {ctx.poll.question}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
