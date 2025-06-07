# sync_demo.py
#
# This script demonstrates the SYNCHRONOUS (standard) usage of the GlobalHotkeys class.
# Synchronous callbacks are regular Python functions. They are simple to write but
# will block the hotkey listener thread until they complete. This is suitable for
# very fast operations but can make your application feel unresponsive if the
# callback takes a long time to execute.

import time
import logging
from python_hotkeys import GlobalHotkeys

# --- 1. Setup Logging (Optional but Recommended) ---
# This helps you see what the GlobalHotkeys class is doing in the background.
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# --- 2. Define Your Synchronous Callback Functions ---
# These are standard Python functions. When a hotkey is pressed, the listener
# thread will execute this function directly.

def fast_action():
    """This is a fast, non-blocking function. It runs instantly."""
    print("ACTION: F9 was pressed. This message is displayed immediately.")

def slow_blocking_action():
    """
    This is a slow, BLOCKING function. 
    While this function is running, the hotkey listener cannot process any other hotkeys.
    Try pressing F9 or Ctrl+C while the 'Working...' message is displayed. 
    You'll notice that those actions are delayed until this function finishes.
    """
    print("\nACTION: F10 was pressed. Starting a slow 3-second task...")
    print("   (Try pressing F9 now - it won't register until this is done)")
    time.sleep(3) # The 'time.sleep()' call blocks the entire thread.
    print("...Finished slow task. The hotkey listener is now unblocked and can process new keys.\n")

def exit_program():
    """A simple function to stop the hotkey listener and exit."""
    print("ACTION: Ctrl+C was pressed. Shutting down.")
    hotkeys.stop() # This is the crucial call to stop the listener loop.

# --- 3. Initialize and Register Hotkeys ---
print("--- Synchronous Hotkey Demo ---")
print("Initializing hotkey listener...")

# Create an instance of the hotkey manager
hotkeys = GlobalHotkeys()

# Register the hotkeys and link them to their callback functions.
# The first argument is the key combination (case-insensitive).
# The second argument is the function to execute when the key is pressed.
print("Registering hotkeys:")
print("  - F9: A fast, immediate action.")
print("  - F10: A slow, blocking action.")
print("  - Ctrl+C: Exit the program.")

hotkeys.register_hotkey('f9', fast_action)
hotkeys.register_hotkey('f10', slow_blocking_action)
hotkeys.register_hotkey('ctrl+c', exit_program) # 'ctrl+c' is a special key

# --- 4. Start the Listener ---
# This starts the background thread that listens for keyboard input.
hotkeys.start()
print("\nListener started. Press a registered hotkey.")

# --- 5. Keep the Main Thread Alive ---
# The hotkey listener runs in a background thread (daemon). Your main program
# needs to keep running for the background thread to stay alive.
# This loop will run until the `hotkeys._running` flag is set to False,
# which is what our `exit_program` function does.
def main():
    try:
        while hotkeys._running:
            # You can do other work in your main thread here if needed.
            # We'll just sleep to prevent this loop from using 100% CPU.
            time.sleep(0.1)
    except KeyboardInterrupt:
        # This allows you to press Ctrl+C in the terminal as a fallback,
        # though our registered hotkey is the cleaner way to exit.
        print("\nKeyboardInterrupt caught. Forcing shutdown.")
        hotkeys.stop()

    print("Program finished.")

if __name__ == "__main__":
    main()