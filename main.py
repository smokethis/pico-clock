# main.py
import asyncio
from clock_app import TimeCountdownApp

# This is all main.py does - create and run the app
app = TimeCountdownApp()
asyncio.run(app.run())