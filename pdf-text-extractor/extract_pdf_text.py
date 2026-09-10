"""Copy words from a PDF into a UTF-8 text file without changing the PDF."""

import fitz

pdf_path = "ThePDFfile.pdf"
output_path = "CanCopyHa.txt"

all_words = []

with fitz.open(pdf_path) as doc:
    for page in doc:
        words = page.get_text("words")
        for word in words:
            all_words.append(word[4])

with open(output_path, "w", encoding="utf-8") as output_file:
    output_file.write(" ".join(all_words))

print(f"Extracted {len(all_words)} words to {output_path}")
