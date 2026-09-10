"""Convert text to leetspeak using a fixed set of character replacements."""


def replace_characters(input_str):
    replacements = {
        "A": "4",
        "a": "@",
        "s": "$",
        "S": "$",
        "O": "0",
        "o": "0",
        "E": "3",
        "e": "3",
        "i": "1",
        "I": "1",
        "b": "8",
        "B": "8",
        "t": "7",
        "T": "7",
        " ": "_",
    }
    for char, replacement in replacements.items():
        input_str = input_str.replace(char, replacement)
    return input_str


def main():
    input_file = "Countries"  # Change this to the path of your input file.
    output_file = "tryme.txt"

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            data = file.read()
            replaced_data = replace_characters(data)
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(replaced_data)
        print(f"Characters replaced successfully. Check '{output_file}' for the output.")
    except FileNotFoundError:
        print(f"Error: File or directory not found. Check '{input_file}' and '{output_file}'.")


if __name__ == "__main__":
    main()
