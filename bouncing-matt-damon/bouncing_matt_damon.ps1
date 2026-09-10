<#
.SYNOPSIS
Bounces a chosen image around a fullscreen Windows overlay. Press Esc to close.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ImagePath
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

if (-not (Test-Path -LiteralPath $ImagePath -PathType Leaf)) {
    throw "Image file not found: $ImagePath"
}

$form = $null
$timer = $null
$image = $null
try {
    $image = [System.Drawing.Image]::FromFile(
        (Get-Item -LiteralPath $ImagePath).FullName
    )
    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Bouncing Matt Damon - Esc to close"
    $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
    $form.Bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $form.ShowInTaskbar = $true
    $form.TopMost = $true
    $form.KeyPreview = $true
    $form.BackColor = [System.Drawing.Color]::Magenta
    $form.TransparencyKey = $form.BackColor

    $scale = [math]::Min(1.0, [math]::Min(
        $form.ClientSize.Width * 0.4 / $image.Width,
        $form.ClientSize.Height * 0.4 / $image.Height
    ))
    $pictureBox = New-Object System.Windows.Forms.PictureBox
    $pictureBox.Image = $image
    $pictureBox.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
    $pictureBox.Size = New-Object System.Drawing.Size(
        [math]::Max(1, [int]($image.Width * $scale)),
        [math]::Max(1, [int]($image.Height * $scale))
    )
    $pictureBox.BackColor = [System.Drawing.Color]::Transparent
    $form.Controls.Add($pictureBox)

    # A mutable object keeps animation state across timer callbacks.
    $motion = @{
        X = [int](($form.ClientSize.Width - $pictureBox.Width) / 2)
        Y = [int](($form.ClientSize.Height - $pictureBox.Height) / 2)
        DX = 5
        DY = 5
    }
    $pictureBox.Location = New-Object System.Drawing.Point($motion.X, $motion.Y)

    $form.Add_KeyDown({
        param($sender, $eventArgs)
        if ($eventArgs.KeyCode -eq [System.Windows.Forms.Keys]::Escape) {
            $form.Close()
        }
    })
    $pictureBox.Add_DoubleClick({ $form.Close() })

    $timer = New-Object System.Windows.Forms.Timer
    $timer.Interval = 30
    $timer.Add_Tick({
        $right = [math]::Max(0, $form.ClientSize.Width - $pictureBox.Width)
        $bottom = [math]::Max(0, $form.ClientSize.Height - $pictureBox.Height)
        $motion.X += $motion.DX
        $motion.Y += $motion.DY

        if ($motion.X -lt 0 -or $motion.X -gt $right) {
            $motion.DX = -$motion.DX
            $motion.X = [math]::Max(0, [math]::Min($right, $motion.X))
        }
        if ($motion.Y -lt 0 -or $motion.Y -gt $bottom) {
            $motion.DY = -$motion.DY
            $motion.Y = [math]::Max(0, [math]::Min($bottom, $motion.Y))
        }
        $pictureBox.Location = New-Object System.Drawing.Point($motion.X, $motion.Y)
    })
    $form.Add_Shown({ $timer.Start() })
    $form.Add_FormClosing({ $timer.Stop() })
    [void]$form.ShowDialog()
}
finally {
    if ($null -ne $timer) { $timer.Dispose() }
    if ($null -ne $form) { $form.Dispose() }
    if ($null -ne $image) { $image.Dispose() }
}
