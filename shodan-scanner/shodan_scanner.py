"""Menu for Shodan host lookups, database searches, and public IP lookup."""

import argparse
import getpass
import ipaddress
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request

import shodan


def host(api):
    target = input("Enter an IP address or hostname: ").strip()
    if not target:
        raise ValueError("Enter an IP address or hostname.")
    try:
        address = str(ipaddress.ip_address(target))
    except ValueError:
        address = socket.gethostbyname(target)
    info = api.host(address, history=True)
    print("-" * 60)
    print(f"IP: {info.get('ip_str', address)}")
    print("Hostnames:")
    for name in info.get("hostnames") or []:
        print(f"  [+] {name}")
    for label, field in [
        ("Organization", "org"), ("Operating System", "os"),
        ("Latitude", "latitude"), ("Longitude", "longitude"), ("City", "city"),
    ]:
        value = info.get(field)
        print(f"{label}: {value if value is not None else 'n/a'}")
    print("-" * 60)


def search(api):
    query = input("Enter search query: ").strip()
    if not query:
        raise ValueError("Enter a search query.")
    result = api.search(query)
    matches = result.get("matches", [])
    print(f"Showing {len(matches)} matches from the first page; total: {result.get('total', 0)}")
    for service in matches:
        print(f"{service.get('ip_str', 'n/a')} | "
              f"{service.get('port', 'n/a')} | {service.get('org') or 'n/a'}")


def show_public_ip(key):
    query = urllib.parse.urlencode({"key": key})
    with urllib.request.urlopen(
        "https://api.shodan.io/tools/myip?" + query, timeout=30
    ) as response:
        address = json.load(response)
    print(f"Public IP: {ipaddress.ip_address(address)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-k", "--key", help="Shodan API key; hidden prompt is preferred")
    args = parser.parse_args()
    key = (args.key or os.environ.get("SHODAN_API_KEY") or
           getpass.getpass("Shodan API key: ")).strip()
    if not key:
        parser.exit(1, "No key supplied. Exiting.\n")
    api = shodan.Shodan(key)

    while True:
        print("\n1. Host lookup\n2. Search Shodan\n3. What's my public IP?\n0. Exit")
        option = input("Enter choice: ").strip()
        try:
            if option == "1":
                host(api)
            elif option == "2":
                search(api)
            elif option == "3":
                show_public_ip(key)
            elif option == "0":
                break
            else:
                print("Choose 0, 1, 2, or 3.")
        except urllib.error.HTTPError as error:
            print(f"Shodan HTTP error: {error.code}")
        except urllib.error.URLError:
            print("Could not connect to the public IP endpoint.")
        except shodan.APIError as error:
            print(f"Shodan API error: {str(error).replace(key, '[redacted]')}")
        except (OSError, ValueError) as error:
            print(f"Request failed: {str(error).replace(key, '[redacted]')}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
