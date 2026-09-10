# Scripts to Steal

A collection of handy scripts for people to use.

## PDF text extractor

[The Python script](pdf-text-extractor/extract_pdf_text.py) copies the words from a PDF into a plain text file. It does not remove text from or change the original PDF.

### How to use it

1. Install Python and download this repository.
2. Open a terminal in the `pdf-text-extractor` folder.
3. Install the dependency:

   ```sh
   python -m pip install -r requirements.txt
   ```

4. Put your PDF in that folder. Change `pdf_path` in the script to your PDF's filename, or name your PDF `ThePDFfile.pdf`.
5. Optionally change `output_path` to the text filename you want. An existing file with that name will be overwritten.
6. Run:

   ```sh
   python extract_pdf_text.py
   ```

The result is saved as `CanCopyHa.txt` by default.

### Limitations

- Extracts embedded text only; scanned images need OCR first.
- Joins words with spaces, so original formatting and line breaks are not preserved.
- The extracted word order may differ from the visual reading order, especially in multi-column documents.

## Excel worksheet protection remover

[Script and instructions](excel-unprotect/README.md) to disable worksheet protection and unhide worksheets in an .xlsx copy. Does not remove passwords required to open encrypted files.

## L33t Wordlists Python

[Script and instructions](l33t-wordlists/README.md) to convert text files to leetspeak using fixed character replacements. No extra packages required.

## POP3 Inbox Downloader Python

[Script and instructions](pop3-inbox-downloader/README.md) to download POP3 email messages. Prompts for a password, uses SSL by default, and keeps server messages unless deletion is explicitly requested.

## IMAP Downloader Python

[Script and instructions](imap-downloader/README.md) to download messages from selected IMAP folders using SSL and read-only access. Prompts for your password and preserves message flags.

## Hex String Finder

[Script and instructions](hex-string-finder/README.md) to find standalone 32-character hexadecimal strings in text files without modifying them. Includes sample input; matches are not necessarily password hashes.

## Directory Lister PowerShell

[Script and instructions](directory-lister/README.md) to list immediate subfolders and calculate their recursive file sizes without modifying files.
