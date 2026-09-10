# Directory Lister PowerShell

Lists each immediate subfolder of a chosen folder and totals the sizes of files inside it, including nested files. It does not modify any files.

## Usage

Download this repository and open PowerShell in this folder.

```powershell
.\directory_lister.ps1 -FolderPath "C:\Users\YourName\Documents"
```

Replace the example path with the folder you want to inspect. If you omit `-FolderPath`, it scans the current folder.

## Output

```text
Folder: Projects
Size: 12.5 MB
------------------------
```

- Totals file lengths and rounds to two decimal places.
- PowerShell's `1MB` is 1,048,576 bytes, so these values are technically MiB.
- Includes hidden files within listed subfolders. Hidden immediate subfolders are not listed.
- Files directly inside the chosen parent folder are not included.
- Prints a warning when unreadable contents make a total incomplete.
- Empty folders show 0 MB.
- Large directory trees may take time to scan.
