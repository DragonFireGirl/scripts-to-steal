"""Convert a browser bookmark HTML export into Markdown tables."""

import argparse
import html
from html.parser import HTMLParser


class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.path = []
        self.levels = []
        self.pending_folder = None
        self.capture = None
        self.parts = []
        self.url = ""
        self.groups = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("h3", "a"):
            self.capture = tag
            self.parts = []
            self.url = attrs.get("href") or ""
        elif tag == "dl":
            entered_folder = self.pending_folder is not None
            self.levels.append(entered_folder)
            if entered_folder:
                self.path.append(self.pending_folder)
                self.groups.setdefault(tuple(self.path), [])
                self.pending_folder = None

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            title = "".join(self.parts).strip()
            if tag == "h3":
                self.pending_folder = title or "Untitled folder"
            elif tag == "a" and self.url:
                self.groups.setdefault(tuple(self.path), []).append(
                    (title or self.url, self.url)
                )
            self.capture = None
            self.parts = []
        elif tag == "dl" and self.levels:
            if self.levels.pop():
                self.path.pop()


def escape_cell(value):
    value = html.escape(" ".join(value.split()), quote=False)
    for char in ("\\", "*", "_", "[", "]", "`"):
        value = value.replace(char, "\\" + char)
    return value.replace("|", "&#124;")


def format_markdown(groups):
    sections = ["# Bookmarks\n"]
    for path, bookmarks in groups.items():
        name = " / ".join(path) if path else "Unfiled bookmarks"
        sections.append(f"## {escape_cell(name)}\n")
        sections.append("| Description | URL |\n| --- | --- |")
        for title, url in bookmarks:
            sections.append(f"| {escape_cell(title)} | {escape_cell(url)} |")
        sections.append("")
    return "\n".join(sections) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", nargs="?", default="bookmark.html")
    parser.add_argument("--output", default="output.md")
    args = parser.parse_args()
    try:
        with open(args.input_file, "r", encoding="utf-8-sig") as source:
            content = source.read()
        bookmarks = BookmarkParser()
        bookmarks.feed(content)
        bookmarks.close()
        # Exclusive creation keeps earlier output and the source from being overwritten.
        with open(args.output, "x", encoding="utf-8") as output:
            output.write(format_markdown(bookmarks.groups))
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"Conversion failed: {error}\n")
    count = sum(len(items) for items in bookmarks.groups.values())
    print(f"Saved {count} bookmarks to {args.output}")


if __name__ == "__main__":
    main()
