from teleapp import TeleApp

# Example: minimal decorator-based app.
# Purpose:
# - demonstrates the smallest in-process TeleApp app
# - this is the recommended first example when learning teleapp
#
# Start:
# - create .env with TELEAPP_TOKEN and TELEAPP_ALLOWED_USER_ID
# - python examples/hello_app.py
# - or start_teleapp.bat examples/hello_app.py
#
# Stop:
# - Ctrl+C in the terminal running the process

app = TeleApp()


@app.message
async def handle_message(ctx):
    # Default message handler for any plain text that does not match commands or routes.
    return f"hello: {ctx.text}"


if __name__ == "__main__":
    app.run()
