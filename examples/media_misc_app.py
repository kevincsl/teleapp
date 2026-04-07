from teleapp import ContactResponse, PollResponse, TeleApp, VideoResponse

# Example: third media batch.
# Purpose:
# - demonstrates video, poll, and contact handling
# - shows both Telegram-native input inspection and output responses
#
# Start:
# - create .env with TELEAPP_TOKEN and TELEAPP_ALLOWED_USER_ID
# - python examples/media_misc_app.py
# - or start_teleapp.bat examples/media_misc_app.py
#
# Stop:
# - Ctrl+C in the terminal running the process

app = TeleApp()


@app.command("/video")
async def video(ctx):
    # Return a video by local file path.
    return VideoResponse(text="", file_path="output/demo.mp4", caption="video demo")


@app.command("/contact")
async def contact(ctx):
    # Return a Telegram contact card.
    return ContactResponse(text="", phone_number="123456789", first_name="Kevin", last_name="Lin")


@app.command("/poll")
async def poll(ctx):
    # Return a Telegram poll.
    return PollResponse(text="", question="Choose one", options=["A", "B"], allows_multiple_answers=False)


@app.message
async def fallback(ctx):
    # Inspect incoming video/contact/poll payloads.
    if ctx.video:
        return f"video duration: {ctx.video.duration}"
    if ctx.contact:
        return f"contact: {ctx.contact.first_name}"
    if ctx.poll:
        return f"poll: {ctx.poll.question}"
    return f"echo: {ctx.text}"


if __name__ == "__main__":
    app.run()
