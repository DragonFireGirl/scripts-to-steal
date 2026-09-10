# Bouncing Matt Damon PowerShell

Bounces a picture around your primary screen in a transparent, always-on-top window. Use your own Matt Damon image—or any other picture.

## Run

Windows only. Download this repository and open a terminal in this folder:

```powershell
powershell.exe -NoProfile -STA -File .\bouncing_matt_damon.ps1 -ImagePath "C:\Pictures\matt-damon.png"
```

Use the path to an existing local image. A transparent PNG works best. No image is included or downloaded automatically.

## Close the overlay

- Press **Esc** while the overlay is focused.
- Double-click the bouncing image.
- Or select its taskbar entry and press **Alt+F4**.

## Details

- Large images are scaled to fit within 40% of the screen dimensions.
- Moves five pixels every 30 milliseconds and bounces off the edges.
- Change `DX`, `DY`, or the timer interval in the script to adjust speed.
- Magenta is the transparency color; magenta areas of your image will also appear transparent.
- The overlay may cover other apps while running. It remains listed in the taskbar.
- The image file is released when the window closes.

The PowerShell syntax was checked without launching the overlay. The animation has not been visually tested.
