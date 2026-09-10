<p align="center">
  <img src="assets/banner.svg" alt="INSOMNIA — Scripts to Steal. Small tools. Late-night ideas." width="100%">
</p>

<p align="center">
  <strong>A collection of useful scripts, desktop experiments, and browser effects.</strong><br>
  Browse the collection, pick a tool, and open its guide to get started.
</p>

<p align="center">
  <a href="#visuals--experiments">Visuals</a> ·
  <a href="#files--text">Files &amp; text</a> ·
  <a href="#email--media">Email &amp; media</a> ·
  <a href="#network--analysis">Network &amp; analysis</a> ·
  <a href="#getting-started">Getting started</a>
</p>

---

## Featured: Glowing Cursor Trails

**INSOMNIA in neon.** A standalone browser animation with colorful trails that follow your mouse or touch, a dark background, and glowing text.

**[Open the guide](docs/glowing-cursor-trails.md)** · **[View the HTML file](glowing-cursor-trails.html)**

Download the HTML file and open it in your browser. No installation or extra packages required.

## The collection

### Visuals & experiments

| Tool | What it does | Runs with |
| :--- | :--- | :--- |
| [Glowing Cursor Trails](docs/glowing-cursor-trails.md) | Draws glowing trails around the INSOMNIA title as you move your mouse or touch the screen. | Browser |
| [Bouncing Matt Damon](bouncing-matt-damon/README.md) | Bounces a local image around a Windows desktop overlay. | PowerShell / Windows |
| [Keyboard Event Demo](keyboard-event-demo/README.md) | Displays keyboard events in a local practice field without sending or storing them. | Python |

### Files & text

| Tool | What it does | Runs with |
| :--- | :--- | :--- |
| [PDF Text Extractor](pdf-text-extractor/README.md) | Copies embedded PDF text into a plain text file. | Python |
| [Excel Worksheet Unprotect](excel-unprotect/README.md) | Disables worksheet protection and unhides sheets in an .xlsx copy; does not unlock encrypted files. | Python |
| [Directory Lister](directory-lister/README.md) | Lists immediate subfolders and calculates their recursive file sizes. | PowerShell |
| [Bookmark to Markdown Converter](md-converter/README.md) | Turns browser bookmark HTML exports into Markdown tables, including nested folders. | Python |
| [Hex String Finder](hex-string-finder/README.md) | Finds standalone 32-character hexadecimal strings in text files. | Python |
| [L33t Wordlists](l33t-wordlists/README.md) | Converts text files to leetspeak using fixed character replacements. | Python |

### Email & media

| Tool | What it does | Runs with |
| :--- | :--- | :--- |
| [IMAP Downloader](imap-downloader/README.md) | Downloads messages from selected folders using SSL and read-only access. | Python |
| [POP3 Inbox Downloader](pop3-inbox-downloader/README.md) | Downloads email over POP3; keeps server messages unless deletion is requested. | Python |
| [YouTube MP3 Downloader](youtube-mp3-downloader/README.md) | Saves video audio as MP3 with configurable output and bitrate. | Python / FFmpeg |

### Network & analysis

| Tool | What it does | Runs with |
| :--- | :--- | :--- |
| [HTTPS Link Extractor](https-link-extractor/README.md) | Extracts explicit HTTPS links from one webpage into a text file. | Python |
| [Proxy Connection Checker](proxy-connection-checker/README.md) | Checks HTTP/HTTPS proxies against a test URL and reports status and response time. | Python |
| [Shodan Scanner](shodan-scanner/README.md) | Provides an interactive menu for host lookups, database searches, and public IP lookup. | Python / Shodan |
| [SSH Command Wrapper](ssh-command-wrapper/README.md) | Runs a remote command through OpenSSH using key authentication and verified host keys. | Python / OpenSSH |
| [Elementor Pro Upload Checker](elementor-upload-checker/README.md) | Discovers forms and offers optional marker upload tests with conservative result reporting. | Python |
| [Beacon Configuration Decryptor](beacon-config-decryptor/README.md) | Decrypts the documented AES-CBC configuration format and displays JSON. | Python |

## Getting started

1. **Choose a tool** from the catalog and read its guide.
2. **Download the repository** using **Code → Download ZIP**, then extract it.
3. **Open the tool's folder** and follow its setup and run instructions. Each tool is independent.

For Python tools, install the packages in that tool's `requirements.txt` when one is provided. Individual guides list any additional software or configuration needed.

For the browser animation, open `glowing-cursor-trails.html` directly in your browser after downloading it. GitHub's file view shows the source code.

## Finding your way around

Each tool folder contains its script, a README guide, and any tool-specific dependencies or examples. The standalone cursor animation lives in the main folder, with its guide in `docs/`.

Adding another tool? Use a descriptive folder name and include a short README covering what it does, what it needs, how to run it, and what it produces. Add its link to the matching category above.

---

<p align="center"><sub>INSOMNIA · Scripts to Steal · By <a href="https://github.com/DragonFireGirl">DragonFireGirl</a></sub></p>
