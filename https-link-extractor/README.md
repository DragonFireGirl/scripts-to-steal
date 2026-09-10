# HTTPS Link Extractor

Downloads one webpage and saves its explicit HTTPS anchor links to a UTF-8 text file, one link per line.

## Setup and usage

Install Python 3, download this repository, and open a terminal in this folder.

```sh
python -m pip install -r requirements.txt
python https_link_extractor.py "https://example.com"
```

The default output is `resultsScrapes.txt`. To choose another filename:

```sh
python https_link_extractor.py "https://example.com" --output links.txt
```

An existing output file is not overwritten. Choose a new filename before running again.

## What it extracts

- Anchor tags whose href begins with https://, ignoring capitalization.
- Source order and duplicate links are preserved.
- HTTP, relative, protocol-relative, mailto, and JavaScript links are excluded.
- No linked pages are crawled and no JavaScript is executed.
- A page with no matching links produces an empty output file.

The request uses an identifying User-Agent, follows normal HTTP redirects, checks HTTP errors, and applies a 30-second connection/read timeout. This is not a strict total download deadline. The page is loaded into memory.

No live webpage was requested while preparing this script; it has not been run locally.
