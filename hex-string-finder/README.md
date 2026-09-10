# Hex String Finder

Finds standalone 32-character hexadecimal strings in an existing UTF-8 text file and prints them. It reads the input without changing it.

A match is not proof of a password hash. This script does not inspect 7z archives or extract archive password hashes.

## Usage

Install Python 3, download this repository, and open a terminal in this folder. No extra packages are required.

```sh
python hex_string_finder.py example.txt
```

Replace `example.txt` with your own text file's path. Quote paths containing spaces.

## Example

The included example file produces:

```text
Found 1 matching hexadecimal strings:
abcdef1234567890abcdef1234567890
```

## Matching rules

- Matches exactly 32 hexadecimal characters: digits 0–9 and letters A–F, ignoring case.
- Requires word boundaries on both sides; strings attached to other letters, digits, or underscores do not match.
- Preserves matching text's capitalization, order, and duplicates.
- Reads the entire file into memory.
- Prints an error for missing, unreadable, or non-UTF-8 files.
