"""Find standalone 32-character hexadecimal strings in a UTF-8 text file."""

import argparse
import re


def extract_hex_strings(file):
    return re.findall(r"\b[A-Fa-f0-9]{32}\b", file.read())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="Path to an existing UTF-8 text file")
    args = parser.parse_args()
    try:
        with open(args.input_file, "r", encoding="utf-8") as file:
            matches = extract_hex_strings(file)
    except (OSError, UnicodeError) as error:
        parser.exit(1, f"Could not read input file: {error}\n")

    print(f"Found {len(matches)} matching hexadecimal strings:")
    for match in matches:
        print(match)


if __name__ == "__main__":
    main()
