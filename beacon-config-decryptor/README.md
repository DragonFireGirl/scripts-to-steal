# Beacon Configuration Decryptor

Decrypts a specific encrypted configuration format and prints its UTF-8 JSON contents. This is not a general-purpose beacon decryptor: the input must match the layout and fixed constants in the script.

## Install and run

Requires Python 3.9 or newer:

```sh
python -m pip install -r requirements.txt
python beacon_config_decryptor.py beacon.enc
```

If you omit the filename, it reads `beacon.enc` from the current folder. Add `--show-key` to display the derived AES key. The JSON itself may contain sensitive configuration values.

The source file is read without modification. No decrypted content is executed and no network connection is made.

## Expected format

| Offset | Length | Content |
| --- | --- | --- |
| 0 | 8 bytes | Unsigned seed, little-endian |
| 8 | 16 bytes | AES-CBC IV |
| 24 | 4 bytes | Ciphertext length, little-endian |
| 28 | Declared length | AES-CBC ciphertext with PKCS#7 padding |

The script applies modular exponentiation with the supplied MODULUS and EXPONENT constants, hashes the 8-byte little-endian result with SHA-256, and uses the first 16 hash bytes as the AES key.

It rejects truncated data, trailing bytes, invalid ciphertext lengths, invalid padding, and non-UTF-8/non-JSON plaintext. This strict version assumes PKCS#7 padding; files using a different scheme are unsupported.

AES-CBC in this format has no authentication tag. Successful padding and JSON parsing do not prove authenticity or integrity.

## Validation

Tested offline with a synthetic encrypted JSON fixture, malformed lengths, invalid padding, and an empty file. No real beacon file was supplied, so compatibility with your particular sample is unverified.
