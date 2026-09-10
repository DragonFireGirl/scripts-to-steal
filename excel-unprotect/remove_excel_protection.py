"""Disable worksheet protection and unhide worksheets in an .xlsx copy."""

import openpyxl


def remove_protection_and_unhide_sheets(excel_file, output_file):
    wb = openpyxl.load_workbook(excel_file)
    try:
        for sheet in wb.worksheets:
            # Disable worksheet protection, including password-based sheet protection.
            sheet.protection.sheet = False
            sheet.sheet_state = "visible"

        wb.save(output_file)
    finally:
        wb.close()


if __name__ == "__main__":
    input_file = "111.xlsx"
    output_file = "output.xlsx"
    remove_protection_and_unhide_sheets(input_file, output_file)
    print(f"Processed file saved as: {output_file}")
