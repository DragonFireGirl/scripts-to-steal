# SSH Command Wrapper

Runs one remote shell command through the installed OpenSSH client and returns its output and exit status. This is a command-line wrapper, not an MCP server. An existing MCP integration would need to invoke it separately.

## Requirements

- Python 3 and an OpenSSH client available as `ssh`.
- An account on the destination machine.
- Working key authentication, such as an SSH agent or an identity file.
- The destination's host key already verified and recorded in your SSH known_hosts file.

No extra Python packages are required. Connect manually first and verify the host-key fingerprint through a trusted channel before accepting it. Batch mode deliberately fails instead of prompting for passwords or trusting an unknown host.

## Usage

```sh
python ssh_command_wrapper.py --host user@hostname "hostname"
python ssh_command_wrapper.py --host user@hostname --port 31337 --identity "/path/to/private-key" "whoami"
```

The port defaults to 22. Pass `--port 31337` for the port in the original example. Use `--timeout 120` for a longer local timeout.

## Behavior

- Uses existing SSH configuration and agent authentication.
- Keeps host-key verification enabled.
- Streams remote output and errors to the terminal.
- Returns SSH's exit status, or 124 on local timeout.
- Passes arguments to SSH without a local shell.
- The remote command is still interpreted by the remote shell. Do not construct it from untrusted input.
- A local timeout does not guarantee the remote process has stopped.
- Does not create tunnels, perform network discovery, or implement MCP tools.
- Does not embed or save a password.

The wrapper was reviewed but not run against a remote machine.
