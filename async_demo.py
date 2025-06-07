# async_demo.py
#
# This script demonstrates the ASYNCHRONOUS usage of the GlobalHotkeys class.
# Asynchronous callbacks are defined with `async def`. When triggered, they are
# scheduled to run on a background event loop. This is a key advantage: the
# hotkey listener thread is NOT blocked. It schedules the task and immediately
# returns to listening for more keys, keeping your application responsive.

import asyncio
import time
import logging
from main import GlobalHotkeys # Assuming 'main.py' contains the GlobalHotkeys class

# --- 1. Setup Logging (Optional but Recommended) ---
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# --- 2. Define Your Asynchronous Callback Functions ---
# Note the `async def` syntax. This marks them as coroutine functions.

async def fast_async_action():
    """This is a fast async function. It runs almost instantly."""
    print("ACTION: F9 was pressed. This async message is displayed immediately.")
    # `await asyncio.sleep(0)` can be used to yield control back to the event
    # loop briefly, which is good practice in async programming.
    await asyncio.sleep(0)

async def slow_non_blocking_action():
    """
    This is a slow, NON-BLOCKING function.
    The `await asyncio.sleep(3)` call pauses THIS function, but it does NOT block
    the hotkey listener. The listener thread schedules this task and is immediately
    free to process other hotkeys.
    
    Try pressing F9 while the 'Working...' message is displayed. You'll see that
    it registers and prints its message instantly, even while this slow task is "sleeping".
    """
    print("\nACTION: F10 was pressed. Starting a slow 3-second NON-BLOCKING task...")
    print("   (Try pressing F9 now - it will register and run immediately!)")
    await asyncio.sleep(3) # This pauses this coroutine, but not the listener thread.
    print("...Finished slow async task. The hotkey listener was never blocked.\n")

def exit_program():
    """ 
    This is a standard synchronous function. It's perfectly fine to mix and match.
    It stops the hotkey listener and allows the program to exit cleanly.
    """
    print("ACTION: Ctrl+C was pressed. Shutting down.")
    hotkeys.stop()

# --- 3. Initialize and Register Hotkeys ---
print("--- Asynchronous Hotkey Demo ---")
print("Initializing hotkey listener...")

# Create an instance of the hotkey manager
hotkeys = GlobalHotkeys()

# Register the hotkeys and link them to their callback functions.
# The `GlobalHotkeys` class automatically detects that the callbacks are
# `async def` functions and handles them correctly.
print("Registering hotkeys:")
print("  - F9: A fast, non-blocking async action.")
print("  - F10: A slow, non-blocking async action.")
print("  - Ctrl+C: Exit the program.")

hotkeys.register_hotkey('f9', fast_async_action)
hotkeys.register_hotkey('f10', slow_non_blocking_action)
hotkeys.register_hotkey('ctrl+c', exit_program)

# --- 4. Start the Listener ---
# This starts both the keyboard listener thread AND the asyncio event loop thread.
hotkeys.start()
print("\nListener started. Press a registered hotkey.")

# --- 5. Keep the Main Thread Alive ---
# The logic is the same as in the sync demo. We wait until the `exit_program`
# function tells the hotkeys instance to stop.
try:
    while hotkeys._running:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt caught. Forcing shutdown.")
    hotkeys.stop()

print("Program finished.")
