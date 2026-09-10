# POP3 Inbox Downloader Python

Downloads all messages available in a POP3 mailbox to `dump.txt`. POP3 lists messages in a mailbox, not separate inboxes or folders.

## Usage

Install Python 3, download this repository, and open a terminal in this folder. No extra packages are required.

```sh
python pop3_inbox_downloader.py --server pop.example.com --username you@example.com
```

Enter your password at the hidden prompt. Login details are not saved in the script.

SSL with certificate verification is enabled by default on port 995. Use `--port NUMBER` for a different port. For a server that only supports unencrypted POP3, use `--plain` (default port 110); this sends credentials and email without encryption.

## Output

- Saves raw message headers and bodies separated by message markers.
- Preserves message bytes; encoded MIME bodies and attachments are not converted into readable text.
- Use `--output another-dump.txt` to choose a filename.
- Refuses to overwrite existing files. A failed download may leave a partial file; choose a new output filename before retrying.
- Repeated runs download all available messages again.

## Optional deletion

Messages stay on the server by default. Adding `--delete` explicitly requests server deletion after all messages are saved locally. Deletion is committed when the server accepts QUIT. If that connection fails, verify the server state before retrying.

```sh
python pop3_inbox_downloader.py --server pop.example.com --username you@example.com --output saved-mail.txt --delete
```

The script does not support OAuth login. Some providers require an app password or enabling POP3 in account settings.
