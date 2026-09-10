# L33t Wordlists Python

Converts a text file to leetspeak using fixed character substitutions. Each input word gets one converted version; the script does not generate every possible spelling.

## How to use

1. Install Python 3 and download this repository. No extra packages are required.
2. Open a terminal in the `l33t-wordlists` folder.
3. Put a UTF-8 text file named `Countries` (with no extension) in this folder, or edit `input_file` in the script to match your file, such as `Countries.txt`.
4. Run:

   ```sh
   python l33t_wordlists.py
   ```

5. Find the converted text in `tryme.txt`. Edit `output_file` to choose another filename.

An existing output file will be overwritten. Keep the input and output filenames different to preserve the original.

## Replacements

| Input | Output |
| --- | --- |
| A | 4 |
| a | @ |
| s, S | $ |
| O, o | 0 |
| E, e | 3 |
| i, I | 1 |
| b, B | 8 |
| t, T | 7 |
| Space | _ |

Other characters remain unchanged. Words on separate lines stay on separate lines.

For example, `Albania South Africa` becomes `4l8@n1@_$0u7h_4fr1c@`.
