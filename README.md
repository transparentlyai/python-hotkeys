# Python Hotkeys

A robust, single-file, dependency-free library for capturing global terminal hotkeys on Unix-like systems. It is designed for simplicity, reliability, and modern asynchronous applications, while remaining fully compatible with traditional synchronous code.

This entire library is contained in the `main.py` file, making it easy to drop into any project.

![Demo](https://github.com/mauro-stran/python-hotkeys/blob/main/assets/demo.gif)

---

## Key Features

- **Zero Dependencies**: Pure Python standard library implementation. Drop `main.py` into your project and go.
- **Sync and Async Support**: Register standard `def` functions or `async def` coroutines as callbacks. The library handles both seamlessly.
- **Suspend and Resume**: Temporarily pause the listener to cede terminal control to other applications (like a TUI or shell command) and then resume without a full restart.
- **Robust Key Parsing**: Built with a sophisticated key sequence parser inspired by `prompt_toolkit`, it correctly handles complex escape sequences, multi-key chords (e.g., `Alt+X`), and modifier keys (`Ctrl`, `Shift`).
- **Terminal-Aware**: Automatically detects if it's running in a TTY and gracefully handles non-interactive environments.
- **Thread-Safe**: Uses a background thread for listening, ensuring your main application remains responsive.
- **Clean Exit**: Automatically restores terminal settings on exit, preventing a broken terminal state.

## Installation

This project uses `uv` for fast environment management.

1.  **Create a Virtual Environment**:

    ```bash
    uv venv
    ```

2.  **Activate the Environment**:

    ```bash
    source .venv/bin/activate
    ```

3.  **Install in Editable Mode**:
    Installing in editable mode (`-e`) links the package to your source files, so any changes you make are immediately reflected.

    ```bash
    uv pip install -e .
    ```

## How to Use

Using the library involves four simple steps:

1.  **Import** the `GlobalHotkeys` class.
2.  **Define** your callback functions (sync or async).
3.  **Instantiate** `GlobalHotkeys` and **register** your hotkeys.
4.  **Start** the listener and keep your main thread alive.

*For basic examples, see the `sync_demo.py` and `async_demo.py` files.*

## Integrating with `prompt_toolkit`

Since both this library and `prompt_toolkit` need exclusive control over terminal input, you must carefully manage who is in control. The new `suspend()` and `resume()` methods are the perfect tools for this.

### Option 1: Suspend and Resume Around a TUI App (Recommended)

This is the most efficient and robust pattern. The global listener runs, and when a hotkey is pressed to launch a TUI, you `suspend()` the listener. This restores normal terminal behavior, allowing `prompt_toolkit` to take over. When the TUI exits, you `resume()` the listener.

**Use Case**: A `ctrl+space` hotkey that launches a command palette TUI.

```python
import asyncio
from prompt_toolkit import PromptSession
from main import GlobalHotkeys

hotkeys = GlobalHotkeys()

async def launch_tui():
    print("Hotkey pressed! Suspending global listener and launching TUI...")
    hotkeys.suspend()

    # --- Your prompt_toolkit App Runs Here ---
    # The terminal is now in a normal state for prompt_toolkit to use.
    session = PromptSession()
    try:
        result = await session.prompt_async('TUI Prompt> ')
        print(f"You entered: {result}")
    finally:
        # --- Resume Global Listener on Exit ---
        print("TUI exited. Resuming global hotkey listener...")
        hotkeys.resume()

# Register the global hotkey
hotkeys.register_hotkey('ctrl+space', launch_tui)
hotkeys.start()

print("Global listener active. Press Ctrl+Space to launch the TUI.")

# Main event loop to keep the script alive
async def main():
    # Add a hotkey to exit the whole program cleanly
    hotkeys.register_hotkey('ctrl+c', lambda: asyncio.create_task(shutdown()))
    while hotkeys._running:
        await asyncio.sleep(1)

async def shutdown():
    print("Exiting.")
    hotkeys.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        if hotkeys._running:
            hotkeys.stop()
```

### Option 2: Using `prompt_toolkit` for All Key Bindings

If your application is a persistent, full-screen TUI, it is often simpler to let `prompt_toolkit` handle all key bindings directly. In this scenario, you don't need this `python-hotkeys` library at all.

**Use Case**: A text editor or file manager where all key presses are handled within the application itself.

*See the `README.md` from the previous version for a code example.*

### Option 3: Advanced Integration with `get_unhandled_key`

This is an advanced and less common pattern. You can run the `python-hotkeys` listener and have your `prompt_toolkit` application periodically poll for unhandled keys from its queue. This could be useful if you want to react to global hotkeys *while* a `prompt_toolkit` app is running but without using its native key-binding system.

**This approach is complex and can lead to race conditions. Use with caution.**

*See the `README.md` from the previous version for a code example.*


## Supported Terminals and Environments

The key parsing is designed to work on a wide variety of **Unix-like terminals** that follow standard ANSI/VT escape code conventions. It has been tested and is known to work well with:

- **`gnome-terminal`**
- **`xterm`** and its derivatives
- **`rxvt-unicode`**
- **Linux console** (non-GUI)
- **macOS Terminal** and **iTerm2**
- Terminals used in **VS Code**, **PyCharm**, and other IDEs.

### Windows Support

This script is **not compatible with Windows `cmd.exe` or PowerShell** because it relies on the `termios` and `tty` modules, which are specific to POSIX (Unix-like) operating systems. For Windows support, a different library like `pynput` or `keyboard` would be required.

## API Reference

### `GlobalHotkeys(timeout=0.1)`

- `timeout`: The time in seconds to wait for subsequent characters in a multi-key escape sequence before processing the buffer.

### Methods

- `register_hotkey(key, callback)`: Binds a `callback` function to a `key` string.
- `unregister_hotkey(key)`: Removes a registered hotkey.
- `start()`: Starts the listener threads.
- `stop()`: Permanently stops the listener threads and restores the terminal.
- `suspend()`: Temporarily gives up terminal control by restoring its original settings and pausing the listener. This allows other programs to read input.
- `resume()`: Re-acquires terminal control (setting it to cbreak mode) and resumes the listener.
- `get_unhandled_key()`: (Advanced) Retrieves an unhandled key from the input queue.

## How It Works

The library operates by setting the terminal to `cbreak` mode, allowing it to read individual characters as they are typed without requiring the user to press Enter. The `suspend()` and `resume()` methods toggle this `cbreak` mode on and off, allowing for seamless interoperability with other terminal applications.
