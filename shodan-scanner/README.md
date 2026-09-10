# Shodan Scanner Python

An interactive menu for looking up Shodan's existing host records, searching its database, and checking your public IP address. It does not initiate new network scans.

## Setup

Install Python 3 and download this repository. Open a terminal in this folder:

```sh
python -m pip install -r requirements.txt
python shodan_scanner.py
```

Enter your Shodan API key at the hidden prompt. You can also provide it through the `SHODAN_API_KEY` environment variable. The original `-k` / `--key` option is supported, but command-line keys can appear in shell history or process listings.

## Menu

1. **Host lookup:** Enter an IP address or hostname. Hostnames resolve to a single IPv4 address using your system's DNS resolver. Displays hostnames, organization, operating system, and location fields when available. Requests historical host data.
2. **Search Shodan:** Enter a Shodan search query. Shows the first page's IP addresses, ports, and organizations, plus the total match count.
3. **What's my public IP?:** Uses Shodan's API with the same key; no separate CLI initialization is needed.
0. **Exit.**

Missing host fields display as `n/a`. Invalid choices return to the menu, and API errors are reported.

Your Shodan account determines which features and queries are available. Requests may use query credits. No live API calls were made while preparing this script.

References: [Python API documentation](https://shodan.readthedocs.io/en/latest/api.html) and [Shodan REST API](https://developer.shodan.io/api).
