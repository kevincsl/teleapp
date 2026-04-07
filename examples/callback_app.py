from teleapp import Button, ButtonResponse, TeleApp

app = TeleApp()


@app.command("/menu")
async def menu(ctx):
    return ButtonResponse(
        "Choose one",
        buttons=[
            Button("Choice A", "choice:a"),
            Button("Choice B", "choice:b"),
        ],
    )


@app.command("choice:a")
async def choice_a(ctx):
    return "You clicked A"


@app.command("choice:b")
async def choice_b(ctx):
    return "You clicked B"


@app.message
async def fallback(ctx):
    return "Send /menu"


if __name__ == "__main__":
    app.run()
