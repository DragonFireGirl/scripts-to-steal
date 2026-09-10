"""Download selected IMAP mailboxes without changing message flags."""

import argparse
import getpass
import imaplib
import ssl


def require_ok(status, operation):
    if status != "OK":
        raise RuntimeError(f"{operation} failed (server status: {status}).")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="IMAP server hostname")
    parser.add_argument("--username", required=True, help="Mailbox username")
    parser.add_argument("--port", type=int, default=993)
    parser.add_argument("--mailboxes", nargs="+",
                        default=["Notes", "Meetings", "Important", "INBOX"])
    parser.add_argument("--output", default="smack.txt", help="New output file")
    args = parser.parse_args()
    password = getpass.getpass("IMAP password: ")
    connection = None
    total = 0
    try:
        connection = imaplib.IMAP4_SSL(
            args.server, args.port, ssl_context=ssl.create_default_context(),
            timeout=30,
        )
        connection.login(args.username, password)
        # Exclusive creation avoids overwriting an earlier download.
        # Keep original message bytes, including non-UTF-8 MIME content.
        with open(args.output, "xb") as output:
            for mailbox in args.mailboxes:
                quoted_mailbox = '"' + mailbox.replace("\\", "\\\\").replace('"', '\\"') + '"'
                status, _ = connection.select(quoted_mailbox, readonly=True)
                require_ok(status, f"Selecting mailbox {mailbox!r}")
                status, data = connection.uid("search", None, "ALL")
                require_ok(status, f"Searching mailbox {mailbox!r}")
                message_ids = data[0].split() if data and data[0] else []
                output.write(
                    f"Mailbox: {mailbox}\r\nTotal emails: {len(message_ids)}\r\n".encode("utf-8")
                )
                for message_id in message_ids:
                    status, email_data = connection.uid(
                        "fetch", message_id, "(BODY.PEEK[])"
                    )
                    require_ok(status, f"Fetching UID {message_id.decode('ascii')}")
                    bodies = [
                        item[1] for item in email_data
                        if isinstance(item, tuple) and isinstance(item[1], bytes)
                    ]
                    if not bodies:
                        raise RuntimeError("Server returned no message body.")
                    output.write(b"Email UID: " + message_id + b"\r\nEmail Content:\r\n")
                    for body in bodies:
                        output.write(body)
                    output.write(b"\r\n\r\n")
                    total += 1
        print(f"Downloaded {total} emails to '{args.output}'.")
    except (OSError, EOFError, imaplib.IMAP4.error, RuntimeError) as error:
        parser.exit(1, f"Download failed: {error}\n"
                    "A partial output file may remain. Choose a new filename before retrying.\n")
    finally:
        if connection is not None:
            try:
                connection.logout()
            except (OSError, EOFError, imaplib.IMAP4.error):
                pass


if __name__ == "__main__":
    main()
