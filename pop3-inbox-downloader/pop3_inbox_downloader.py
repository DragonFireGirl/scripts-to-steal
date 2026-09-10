"""Download POP3 messages to a file; keep server copies unless --delete is set."""

import argparse
import getpass
import os
import poplib
import ssl


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="POP3 server hostname")
    parser.add_argument("--username", required=True, help="Mailbox username")
    parser.add_argument("--port", type=int, help="Default: 995 with SSL, 110 with --plain")
    parser.add_argument("--output", default="dump.txt", help="New output file")
    parser.add_argument("--plain", action="store_true",
                        help="Use unencrypted POP3 (including login credentials)")
    parser.add_argument("--delete", action="store_true",
                        help="Delete downloaded server messages after saving the file")
    args = parser.parse_args()
    password = getpass.getpass("POP3 password: ")
    connection = None
    try:
        if args.plain:
            connection = poplib.POP3(args.server, args.port or 110, timeout=30)
        else:
            connection = poplib.POP3_SSL(
                args.server, args.port or 995, timeout=30,
                context=ssl.create_default_context(),
            )
        connection.user(args.username)
        connection.pass_(password)
        _, message_list, _ = connection.list()
        print(f"Available messages: {len(message_list)}")
        downloaded = []
        # Exclusive creation prevents overwriting an earlier download.
        # Binary mode preserves original message bytes without decoding errors.
        with open(args.output, "xb") as dump_file:
            for entry in message_list:
                number = int(entry.split()[0])
                _, lines, _ = connection.retr(number)
                dump_file.write(f"===== Message {number} =====\r\n".encode("ascii"))
                for line in lines:
                    dump_file.write(line + b"\r\n")
                dump_file.write(b"\r\n")
                downloaded.append(number)
            dump_file.flush()
            os.fsync(dump_file.fileno())

        # Only mark messages after the complete local file is saved and closed.
        if args.delete:
            for number in downloaded:
                connection.dele(number)
        connection.quit()
        connection = None
        print(f"Downloaded {len(downloaded)} messages to '{args.output}'.")
        if args.delete:
            print("Server accepted deletion of downloaded messages.")
    except (OSError, EOFError, poplib.error_proto) as error:
        parser.exit(1, f"Download failed: {error}\n"
                    "A partial output file may remain. If --delete was used and "
                    "the connection failed during QUIT, check server deletion status.\n")
    finally:
        if connection is not None:
            # Close without QUIT so pending deletions are not committed on failure.
            connection.close()


if __name__ == "__main__":
    main()
