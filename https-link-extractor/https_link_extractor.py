"""Extract explicit HTTPS links from one webpage into a text file."""

import argparse
import re
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup


def scrape_https_links_and_save(url, output_file):
    with requests.get(
        url,
        headers={"User-Agent": "HTTPSLinkExtractor/1.0"},
        timeout=30,
    ) as response:
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

    links = [
        link["href"]
        for link in soup.find_all("a", href=re.compile(r"^https://", re.IGNORECASE))
    ]
    # Preserve source order and duplicates, as in the original script.
    # Exclusive creation avoids replacing an existing file.
    with open(output_file, "x", encoding="utf-8") as output:
        for link in links:
            output.write(link + "\n")
    return len(links)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="HTTP or HTTPS webpage URL")
    parser.add_argument("--output", default="resultsScrapes.txt")
    args = parser.parse_args()
    try:
        parsed = urlsplit(args.url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            parser.error("Provide a complete HTTP or HTTPS URL.")
        count = scrape_https_links_and_save(args.url, args.output)
    except (requests.RequestException, OSError, ValueError) as error:
        parser.exit(1, f"Extraction failed: {error}\n")
    print(f"Saved {count} HTTPS links to {args.output}")


if __name__ == "__main__":
    main()
