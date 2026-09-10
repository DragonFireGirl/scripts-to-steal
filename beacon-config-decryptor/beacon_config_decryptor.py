#!/usr/bin/env python3
"""Decrypt the specific seed/IV/length beacon format described in the README."""

import argparse
import hashlib
import json
import struct
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MODULUS = 0x354230D6895F8D45
EXPONENT = 0x2E77571CCD378630


def pkcs7_unpad(buf: bytes) -> bytes:
    if not buf or len(buf) % 16:
        raise ValueError("Invalid padded plaintext length")
    pad = buf[-1]
    if not 1 <= pad <= 16 or buf[-pad:] != bytes([pad]) * pad:
        raise ValueError("Invalid PKCS#7 padding; wrong format, key, or damaged input")
    return buf[:-pad]


def decrypt_beacon(path: Path) -> tuple[bytes, dict]:
    data = path.read_bytes()
    if len(data) < 28:
        raise ValueError("Input is too small for the 28-byte header")
    seed = struct.unpack("<Q", data[:8])[0]
    iv = data[8:24]
    ct_len = struct.unpack("<I", data[24:28])[0]
    if ct_len == 0 or ct_len % 16:
        raise ValueError("Ciphertext length must be a positive multiple of 16")
    if len(data) != 28 + ct_len:
        raise ValueError("Declared ciphertext length does not match file size")
    ct = data[28:]

    x = pow(seed % MODULUS, EXPONENT, MODULUS)
    key = hashlib.sha256(x.to_bytes(8, "little")).digest()[:16]
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    plaintext = pkcs7_unpad(dec.update(ct) + dec.finalize())
    return plaintext, {
        "seed_hex": f"0x{seed:016x}",
        "iv_hex": iv.hex(),
        "pow_result_hex": f"0x{x:016x}",
        "aes_key_hex": key.hex(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", nargs="?", type=Path, default=Path("beacon.enc"))
    parser.add_argument("--show-key", action="store_true",
                        help="Also print the derived AES key")
    args = parser.parse_args()
    try:
        plaintext, info = decrypt_beacon(args.input_file)
        parsed = json.loads(plaintext.decode("utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(1, f"Decryption failed: {error}\n")

    print("[+] Decrypted beacon configuration")
    for name, value in info.items():
        if name != "aes_key_hex" or args.show_key:
            print(f"    {name}: {value}")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
