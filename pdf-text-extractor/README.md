# PDF Text Extractor

[← Back to the collection](../README.md)

[The Python script](extract_pdf_text.py) copies the words from a PDF into a plain text file. It does not remove text from or change the original PDF.

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

