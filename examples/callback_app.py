from teleapp import Button, ButtonResponse, TeleApp

# Example: callback query handling.
# Purpose:
# - demonstrates how ButtonResponse output maps to callback query input
# - shows a simple interactive menu flow
#
# Start:
# - create .env with TELEAPP_TOKEN and TELEAPP_ALLOWED_USER_ID
# - python examples/callback_app.py
# - or start_teleapp.bat examples/callback_app.py
#
# Stop:
# - Ctrl+C in the terminal running the process

app = TeleApp()


@app.command("/menu")
async def menu(ctx):
    # Send two inline buttons that map back to callback query commands.
    return ButtonResponse(
        "Choose one",
        buttons=[
            Button("Choice A", "choice:a"),
            Button("Choice B", "choice:b"),
        ],
    )


@app.command("choice:a")
async def choice_a(ctx):
    # This handler is triggered when the user presses the "Choice A" inline button.
    return "You clicked A"


@app.command("choice:b")
async def choice_b(ctx):
    # This handler is triggered when the user presses the "Choice B" inline button.
    return "You clicked B"


@app.message
async def fallback(ctx):
    # Default guidance shown before the user opens the menu.
    return "Send /menu"


if __name__ == "__main__":
    app.run()
