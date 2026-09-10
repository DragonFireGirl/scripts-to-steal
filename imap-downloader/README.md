# IMAP Downloader Python

Downloads messages from selected IMAP mailboxes into `smack.txt`. Uses read-only mailbox access and BODY.PEEK to avoid marking messages as read. It does not delete messages.

## Usage

Install Python 3.9 or newer, download this repository, and open a terminal in this folder. No extra packages are required.

```sh
python imap_downloader.py --server imap.example.com --username you@example.com
```

Enter your password at the hidden prompt. The default mailboxes are `Notes`, `Meetings`, `Important`, and `INBOX`.

To download only your inbox:

```sh
python imap_downloader.py --server imap.example.com --username you@example.com --mailboxes INBOX
```

Specify other folders by their exact server names; quote names containing spaces:

```sh
python imap_downloader.py --server imap.example.com --username you@example.com --mailboxes INBOX "Sent Items" --output saved-mail.txt
```

## Details

- Uses SSL with certificate verification on port 993. Set `--port` for a different SSL port.
- Prompts for the password rather than storing credentials in the script.
- Saves message headers and raw bodies with mailbox and UID labels.
- Preserves raw bytes; MIME-encoded content and attachments are not decoded for display.
- Refuses to overwrite an existing output file.
- Stops and reports an error if a mailbox cannot be selected or a message cannot be downloaded. A partial file may remain.
- Downloads all messages in the requested folders on each run; it does not track previous downloads.
- Does not implement OAuth or automatic encoding of international mailbox names. Some providers require an app password or IMAP to be enabled.

No mail server was contacted while preparing this script.
