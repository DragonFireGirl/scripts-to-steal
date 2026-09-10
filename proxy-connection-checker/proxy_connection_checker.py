"""Check HTTP/HTTPS proxies against a test URL, without login attempts."""

import argparse
import time
from urllib.parse import urlsplit

import requests


def normalize_proxy(value):
    value = value if "://" in value else "http://" + value
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use an HTTP or HTTPS proxy address.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Proxy credentials are not supported.")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Proxy address must not include a path, query, or fragment.")
    if parsed.port is None:
        raise ValueError("Include the proxy port.")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Test URL you are allowed to request")
    parser.add_argument("--proxies", default="proxy.txt", help="One proxy per line")
    parser.add_argument("--timeout", type=float, default=5, help="Connect/read timeout in seconds")
    args = parser.parse_args()
    try:
        target = urlsplit(args.url)
        if target.scheme not in ("http", "https") or not target.hostname:
            parser.error("--url must be an HTTP or HTTPS URL.")
        if target.username is not None or target.password is not None:
            parser.error("Do not include login credentials in the test URL.")
        if args.timeout <= 0:
            parser.error("--timeout must be greater than zero.")
        with open(args.proxies, encoding="utf-8-sig") as source:
            proxies = [
                line.strip() for line in source
                if line.strip() and not line.lstrip().startswith("#")
            ]
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if not proxies:
        parser.error("The proxy list is empty.")

    for index, entry in enumerate(proxies, 1):
        label = f"Proxy {index}"
        try:
            proxy = normalize_proxy(entry)
        except ValueError as error:
            print(f"{label}: invalid entry ({error})")
            continue
        started = time.perf_counter()
        try:
            # Separate sessions prevent cookies being shared between checks.
            with requests.Session() as session:
                session.trust_env = False
                with session.get(
                    args.url,
                    proxies={"http": proxy, "https": proxy},
                    timeout=args.timeout,
                    allow_redirects=False,
                    stream=True,
                ) as response:
                    elapsed = time.perf_counter() - started
                    print(f"{label}: HTTP {response.status_code} | {elapsed:.2f}s to headers")
        except requests.RequestException as error:
            elapsed = time.perf_counter() - started
            print(f"{label}: {type(error).__name__} | {elapsed:.2f}s")


if __name__ == "__main__":
    main()
