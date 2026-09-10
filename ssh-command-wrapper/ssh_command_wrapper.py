#!/usr/bin/env python3
"""Run one command on an SSH host using keys and verified host keys."""

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="SSH destination, such as user@hostname")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--identity", help="Optional private-key file")
    parser.add_argument("--timeout", type=float, default=60,
                        help="Local SSH process timeout in seconds")
    parser.add_argument("command", help="Remote shell command as one quoted argument")
    args = parser.parse_args()

    if args.host.startswith("-") or any(char.isspace() for char in args.host):
        parser.error("--host must be an SSH destination without spaces or leading '-'.")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535.")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero.")

    ssh_args = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=yes",
        "-o", "ConnectTimeout=15",
        "-p", str(args.port),
    ]
    if args.identity:
        ssh_args.extend(["-i", args.identity])
    ssh_args.extend([args.host, args.command])
    try:
        result = subprocess.run(ssh_args, timeout=args.timeout, check=False)
        return result.returncode if result.returncode >= 0 else 1
    except FileNotFoundError:
        print("OpenSSH client not found. Install it and ensure ssh is on PATH.", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("SSH timed out. The remote command may still be running.", file=sys.stderr)
        return 124
    except OSError as error:
        print(f"Could not start SSH: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
