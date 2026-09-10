# Remove Excel Worksheet Protection and Unhide Sheets

Disables worksheet protection and makes every worksheet visible, then saves a separate .xlsx file.

## How to use

1. Install Python and download this repository.
2. Open a terminal in this folder.
3. Install the dependency:

   ```sh
   python -m pip install -r requirements.txt
   ```

4. Place your workbook in this folder as `111.xlsx`, or change `input_file` in the script.
5. Run:

   ```sh
   python remove_excel_protection.py
   ```

The result is saved as `output.xlsx`. Change `output_file` to choose another name. An existing output file will be overwritten; keep the input and output filenames different to preserve the original.

## What this handles

- Disables worksheet protection, including worksheet protection configured with a password.
- Unhides hidden and very hidden worksheets.
- Does not decrypt files that require a password to open.
- Does not remove workbook structure protection or recover passwords.
- Intended for .xlsx files; this script is not configured to preserve macros in .xlsm files. Some advanced Excel features may not survive an openpyxl save.

See the [openpyxl protection documentation](https://openpyxl.readthedocs.io/en/stable/protection.html) for the distinction between worksheet protection and file encryption.
