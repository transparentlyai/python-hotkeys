# Python Hotkeys

[![PyPI version](https://badge.fury.io/py/python-hotkeys.svg)](https://badge.fury.io/py/python-hotkeys)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Unix](https://img.shields.io/badge/platform-Unix%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://en.wikipedia.org/wiki/Unix-like)

A robust, single-file, dependency-free library for capturing global terminal hotkeys on Unix-like systems. It is designed for simplicity, reliability, and modern asynchronous applications, while remaining fully compatible with traditional synchronous code.

This entire library is contained in the `src/python_hotkeys/__init__.py` file, making it easy to drop into any project.

---

## Key Features

✨ **Zero Dependencies** - Pure Python standard library implementation, no external packages required

⚡ **Dual Mode Support** - Works with both synchronous functions and async coroutines seamlessly

🎯 **Smart Suspend/Resume** - Pause hotkey listening to hand control to TUI apps, then resume without restart

🔧 **Advanced Key Parsing** - Handles complex combinations like `Ctrl+Shift+Alt+F1`, all function keys (F1-F24), arrow keys, and ANSI escape sequences

🖥️ **Terminal Intelligence** - Auto-detects TTY environments and gracefully handles non-interactive shells

🧵 **Thread-Safe Operation** - Runs in background threads, integrates seamlessly into existing threaded applications

🛡️ **Safe Terminal Handling** - Automatically restores terminal settings on exit, preventing broken states

⚙️ **Unhandled Key Queue** - Access keys that weren't bound to hotkeys for advanced integration patterns

🔄 **UTF-8 Support** - Robust Unicode handling with incremental decoding for international keyboards

⏱️ **Timeout-Based Parsing** - Intelligently handles multi-character escape sequences with configurable timeout

🎛️ **Key Aliases** - Support for common key name variations (`enter`/`return`, `backspace`/`ctrl+h`)

📦 **Single File Library** - Entire implementation in one file for easy integration into any project

## Installation

### From PyPI (Recommended)

```bash
uv add python-hotkeys
```

### From Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/mauro-stran/python-hotkeys.git
cd python-hotkeys

# Install with uv
uv add -e .
```

## Quick Start

### Basic Example

```python
from python_hotkeys import GlobalHotkeys

def on_hotkey():
    print("Hotkey pressed!")

hotkeys = GlobalHotkeys()
hotkeys.register_hotkey('ctrl+shift+h', on_hotkey)
hotkeys.start()

# Keep the program running
try:
    while hotkeys._running:
        pass
except KeyboardInterrupt:
    hotkeys.stop()
```

### Async Example

```python
import asyncio
from python_hotkeys import GlobalHotkeys

async def async_action():
    print("Async hotkey triggered!")
    await asyncio.sleep(1)  # Non-blocking operation
    print("Async task completed!")

hotkeys = GlobalHotkeys()
hotkeys.register_hotkey('ctrl+alt+a', async_action)
hotkeys.start()

# Keep running
try:
    while hotkeys._running:
        pass
except KeyboardInterrupt:
    hotkeys.stop()
```

### Threading Integration

The library is designed to work seamlessly in multi-threaded applications:

```python
import threading
from python_hotkeys import GlobalHotkeys

def worker_thread():
    # Your existing application logic
    while True:
        # Do work...
        time.sleep(1)

def on_pause():
    print("Application paused via hotkey!")

# Start your application threads
hotkeys = GlobalHotkeys()
hotkeys.register_hotkey('ctrl+p', on_pause)
hotkeys.start()  # Runs in background threads

# Start other application threads
worker = threading.Thread(target=worker_thread, daemon=True)
worker.start()

# Main thread remains free for other work
try:
    while True:
        # Main application logic
        time.sleep(0.1)
except KeyboardInterrupt:
    hotkeys.stop()
```

### Complete Examples

For more detailed examples, see:
- `sync_demo.py` - Synchronous callback demonstrations
- `async_demo.py` - Asynchronous callback demonstrations

## Integrating with TUI Applications

Since both this library and other terminal-based UI libraries need exclusive control over terminal input, you must carefully manage who is in control. The `suspend()` and `resume()` methods are the perfect tools for this.

### Option 1: Suspend and Resume Around a TUI App (Recommended)

This is the most efficient and robust pattern. The global listener runs, and when a hotkey is pressed to launch a TUI, you `suspend()` the listener. This restores normal terminal behavior, allowing the TUI application to take over. When the TUI exits, you `resume()` the listener.

**Use Case**: A `ctrl+space` hotkey that launches a command palette TUI.

```python
import asyncio
from python_hotkeys import GlobalHotkeys

hotkeys = GlobalHotkeys()

# A placeholder for any TUI (Text-based User Interface) application.
class YourTUIApp:
    async def run_async(self):
        # In a real app, this would draw the UI and handle input.
        # For this demo, we'll just print some text and wait.
        print("\n--- TUI is Active ---")
        print("Pretend there is a cool interface here.")
        print("It will close in 3 seconds.")
        await asyncio.sleep(3) # Simulate TUI running
        print("--- TUI is Exiting ---")
        return "Some result from the TUI"

async def launch_tui():
    print("\nHotkey pressed! Suspending global listener and launching TUI...")
    hotkeys.suspend()

    # --- Your TUI App Runs Here ---
    # The terminal is now in a normal state for your TUI library to use.
    tui_app = YourTUIApp()
    try:
        result = await tui_app.run_async()
        print(f"TUI result: '{result}'")
    finally:
        # --- Resume Global Listener on Exit ---
        print("Resuming global hotkey listener...")
        hotkeys.resume()

# Register the global hotkey
hotkeys.register_hotkey('ctrl+space', launch_tui)
hotkeys.start()

print("Global listener active. Press Ctrl+Space to launch the TUI.")
print("Press Ctrl+C to exit the program.")

# Main event loop to keep the script alive
async def main():
    # Add a hotkey to exit the whole program cleanly
    hotkeys.register_hotkey('ctrl+c', lambda: asyncio.create_task(shutdown()))
    while hotkeys._running:
        await asyncio.sleep(1)

async def shutdown():
    print("\nExiting.")
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

### Option 2: Using a TUI Library for All Key Bindings

If your application is a persistent, full-screen TUI, it is often simpler to let the TUI library handle all key bindings directly. In this scenario, you don't need this `python-hotkeys` library at all.

**Use Case**: A text editor or file manager where all key presses are handled within the application itself.

### Option 3: Advanced Integration with `get_unhandled_key`

This is an advanced and less common pattern. You can run the `python-hotkeys` listener and have your TUI application periodically poll for unhandled keys from its queue. This could be useful if you want to react to global hotkeys *while* a TUI app is running but without using its native key-binding system.

**This approach is complex and can lead to race conditions. Use with caution.**

## Supported Terminals and Environments

The key parsing engine is designed for maximum compatibility across **Unix-like terminals** that follow standard ANSI/VT escape code conventions. It includes multiple escape sequence patterns for each key to ensure broad terminal support.

### ✅ Fully Tested and Supported

- **`xterm`** and derivatives (xterm-256color, etc.)
- **`gnome-terminal`** (GNOME desktop default)
- **`rxvt-unicode`** (urxvt)
- **`kitty`** 
- **Linux console** (text mode, no GUI)
- **macOS Terminal.app** and **iTerm2**
- **VS Code** integrated terminal
- **tmux** and **screen** multiplexers
- **SSH sessions** and remote terminals

### 🔧 Key Compatibility Features

- **Multiple escape patterns** per key (F1 works as `\x1bOP`, `\x1b[[A`, or `\x1b[11~`)
- **Application mode support** for arrow keys and navigation
- **Extended function keys** support (F13-F24)
- **Modified key combinations** (Ctrl+arrows, Shift+arrows, Alt+arrows)
- **Fallback sequences** for terminal-specific variations

### Windows Support

This script is **not compatible with Windows `cmd.exe` or PowerShell** because it relies on the `termios` and `tty` modules, which are specific to POSIX (Unix-like) operating systems. For Windows support, a different library like `pynput` or `keyboard` would be required.

## API Reference

### `GlobalHotkeys(timeout=0.1)`

- `timeout`: The time in seconds to wait for subsequent characters in a multi-key escape sequence before processing the buffer.

### Core Methods

- `register_hotkey(key, callback)`: Binds a `callback` function to a `key` string
- `unregister_hotkey(key)`: Removes a registered hotkey
- `start()`: Starts the listener threads and event loop
- `stop()`: Permanently stops the listener threads and restores the terminal

### Suspend/Resume Control

- `suspend()`: Temporarily gives up terminal control by restoring its original settings and pausing the listener. This allows other programs to read input
- `resume()`: Re-acquires terminal control (setting it to cbreak mode) and resumes the listener

### Advanced Queue Management

- `get_unhandled_key()`: Retrieves an unhandled key from the queue (non-blocking, returns `None` if empty)
- `clear_unhandled_keys()`: Clears all unhandled keys from the queue
- `get_queue_size()`: Returns the current number of unhandled keys in the queue (max 1000)

## How It Works

The library operates by setting the terminal to `cbreak` mode, allowing it to read individual characters as they are typed without requiring the user to press Enter. The `suspend()` and `resume()` methods toggle this `cbreak` mode on and off, allowing for seamless interoperability with other terminal applications.

## Development

### Setting up the Development Environment

```bash
# Clone the repository
git clone https://github.com/mauro-stran/python-hotkeys.git
cd python-hotkeys

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install in editable mode
uv add -e .
```

### Running Examples

```bash
# Run synchronous demo
python sync_demo.py

# Run asynchronous demo  
python async_demo.py
```

### Building and Publishing

```bash
# Build the package
uv build

# Publish to PyPI (maintainers only)
uv publish
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
