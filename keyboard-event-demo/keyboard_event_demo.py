"""Serve a local keyboard-event demo. Run, then open http://127.0.0.1:8000."""

from http.server import BaseHTTPRequestHandler, HTTPServer

PAGE = b"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Keyboard Event Demo</title>
<style>
body { font: 18px system-ui, sans-serif; max-width: 720px; margin: 60px auto; padding: 24px; }
textarea { box-sizing: border-box; width: 100%; font: inherit; padding: 12px; }
output { display: block; padding: 20px; background: #eef2f6; margin: 16px 0; white-space: pre-wrap; }
button { font: inherit; padding: 8px 16px; }
</style>
</head>
<body>
<h1>Keyboard Event Demo</h1>
<p>Type sample text in the practice field to see the latest keyboard event.
Do not enter passwords or personal information. Events stay on this page;
they are not sent to the server or saved.</p>
<label for="practice">Practice field</label>
<textarea id="practice" rows="4" autocomplete="off" spellcheck="false"
placeholder="Try letters, arrows, or Shift..."></textarea>
<output id="display" for="practice">No key pressed yet.</output>
<button id="clear" type="button">Clear</button>
<p>Only the focused practice field is observed. Refresh or close this page to
discard the display. Stop the local server with Ctrl+C.</p>
<script>
const practice = document.getElementById('practice');
const display = document.getElementById('display');
practice.addEventListener('keydown', (event) => {
    display.textContent = 'Key: ' + (event.key === ' ' ? 'Space' : event.key)
        + '\\nCode: ' + event.code
        + '\\nRepeated: ' + event.repeat;
});
document.getElementById('clear').addEventListener('click', () => {
    practice.value = '';
    display.textContent = 'No key pressed yet.';
    practice.focus();
});
window.addEventListener('pageshow', () => {
    practice.value = '';
    display.textContent = 'No key pressed yet.';
});
</script>
</body>
</html>
"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'unsafe-inline'; "
            "style-src 'unsafe-inline'; connect-src 'none'; "
            "form-action 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, format, *args):
        pass


def main():
    try:
        with HTTPServer(("127.0.0.1", 8000), DemoHandler) as server:
            print("Open http://127.0.0.1:8000 in your browser. Stop with Ctrl+C.")
            server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    except OSError as error:
        raise SystemExit(f"Could not run the local server: {error}")


if __name__ == "__main__":
    main()
