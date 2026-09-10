# Proxy Connection Checker

Checks each HTTP/HTTPS proxy against one test URL and prints the HTTP status and time to response headers. No username lists, password lists, or login attempts are used.

## Setup

Install Python 3 and download this repository. Open a terminal in this folder:

```sh
python -m pip install -r requirements.txt
```

Create `proxy.txt` containing one proxy per line:

```text
http://your-proxy-host:8080
```

Addresses without a scheme default to HTTP. Blank lines and lines starting with # are ignored. The included `proxy.example.txt` contains a documentation-only address, not a working proxy.

## Run

```sh
python proxy_connection_checker.py --url https://example.com --proxies proxy.txt
```

Choose a test URL you are allowed to request. Optionally set `--timeout 10` to change the connect/read timeout.

## Results and limits

- Makes one GET request per proxy, sequentially.
- Prints each proxy's line-order number, HTTP status, and elapsed time to headers.
- Does not download or print response bodies and does not follow redirects.
- An HTTP response means a response was received through the configured route; it does not prove that the proxy is trustworthy, anonymous, or reached the intended server.
- TLS certificate verification stays enabled.
- Environment proxy settings and automatic netrc credentials are disabled.
- Does not support SOCKS or authenticated proxies.
- Timeout applies to connection/read operations, not a strict total elapsed-time deadline.
- Request errors are reported by type without printing full request URLs.

No live proxies were contacted during preparation.
