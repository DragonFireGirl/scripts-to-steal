# Glowing Cursor Trails

[← Back to the collection](../README.md)

A standalone HTML animation featuring **INSOMNIA** on a dark background, with glowing, color-changing trails that follow your mouse or touch.

## Open it

1. Download the repository using **Code → Download ZIP** and extract it.
2. Open `glowing-cursor-trails.html` in a browser.
3. Move your mouse, or drag a finger across the page on a touchscreen.

No installation, external assets, or extra packages are needed. The file works offline. GitHub displays its source code; download it to see the animation.

## Make it yours

Open [glowing-cursor-trails.html](../glowing-cursor-trails.html) in a text editor.

| Change | Where to look |
| :--- | :--- |
| Browser tab title | `<title>INSOMNIA</title>` |
| Large text on the page | `<h1>INSOMNIA</h1>` |
| Number of trails | `trails: 20` in `settings` |
| Nodes in each trail | `size: 50` in `settings` |
| Text size and glow | The `h1` CSS rule |
| Trail colors | The `hue` calculation in `animate()` |

Save your changes and refresh the browser to see them.

## Notes

The page hides the normal mouse pointer to highlight the trails. The animation runs continuously while the page is open and does not currently include a pause control or a reduced-motion setting.
