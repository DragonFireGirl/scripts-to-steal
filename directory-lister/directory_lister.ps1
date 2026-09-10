<#
.SYNOPSIS
Lists immediate subfolders and the total size of their accessible files.
#>
param(
    [string]$FolderPath = "."
)

if (-not (Test-Path -LiteralPath $FolderPath -PathType Container)) {
    throw "Folder does not exist or cannot be accessed: $FolderPath"
}

$folders = Get-ChildItem -LiteralPath $FolderPath -Directory -ErrorAction Stop

foreach ($folder in $folders) {
    $scanErrors = @()
    $folderSize = Get-ChildItem -LiteralPath $folder.FullName -Recurse -File -Force `
        -ErrorAction SilentlyContinue -ErrorVariable scanErrors |
        Measure-Object -Property Length -Sum
    $sizeInMB = [math]::Round($folderSize.Sum / 1MB, 2)

    Write-Host "Folder: $($folder.Name)"
    Write-Host "Size: $sizeInMB MB"
    if ($scanErrors.Count -gt 0) {
        Write-Warning "Some contents could not be read; this folder's size may be incomplete."
    }
    Write-Host "------------------------"
}
