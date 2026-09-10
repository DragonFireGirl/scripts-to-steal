# Keyboard Event Demo Python

A local practice page showing the most recent key, physical key code, and repeat status while you type in a clearly labeled field.

## Run

Install Python 3, download this repository, and open a terminal in this folder:

```sh
python keyboard_event_demo.py
```

Open http://127.0.0.1:8000 in your browser. Type sample text into the practice field. Click **Clear** to reset it and press **Ctrl+C** in the terminal to stop the server.

No extra packages are required. If port 8000 is already in use, stop this script and resolve the port conflict before retrying.

## Behavior

- Observes only the practice field, while it is focused.
- Displays only the latest event; does not build a key-history log.
- No page cloning, login form, or password field.
- No event uploads, analytics, or browser storage.
- Server binds to the local computer only and serves the practice page.
- The page blocks network connections from its JavaScript.
- Browser shortcuts and input methods may behave differently from ordinary key presses.

This demo has not been run locally.
