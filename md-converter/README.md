# MD Converter Python

Converts a browser bookmark HTML export into Markdown tables grouped by folder. Nested folder names appear as paths, and bookmarks outside folders appear under **Unfiled bookmarks**.

## Usage

Install Python 3, download this repository, and open a terminal in this folder. No extra packages are required.

1. Export bookmarks from your browser as an HTML file.
2. Place the export here as `bookmark.html`.
3. Run:

   ```sh
   python md_converter.py
   ```

The Markdown is saved to `output.md`. To choose different paths:

```sh
python md_converter.py "my bookmarks.html" --output bookmarks.md
```

The script reads your source file without modifying it and refuses to overwrite an existing output file. Choose a new output name when rerunning.

## Supported format

- Standard browser bookmark exports with H3 folder headings, DL lists, and A links.
- Nested folders, HTML entities, and bookmarks outside folders.
- Markdown table escaping for titles and URL text, including pipe characters.
- Preserves duplicate bookmarks. Folders with identical full paths are combined.
- URLs are displayed as table text; clickable rendering depends on your Markdown viewer.
- Expects UTF-8 input and reads the export into memory.

This converts bookmark exports, not arbitrary webpages. No local execution test has been completed.
