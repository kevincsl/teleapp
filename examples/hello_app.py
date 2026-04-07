from teleapp import TeleApp

app = TeleApp()


@app.message
async def handle_message(ctx):
    return f"hello: {ctx.text}"


if __name__ == "__main__":
    app.run()
