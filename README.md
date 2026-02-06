# 💎 Pyxel Clear
### *Freeze your palette footprint. Maximize your scenes.*

**Pyxel Clear** is a free optimization tool built for **GB Studio** developers and GBC-style artists. It solves the "Palette Bloat" problem by forcing new scenes to conform to your existing project library, preventing the redundant "stacking" of near-identical palettes that eat up precious memory.

## 🚀 The Core Workflow
Instead of generating new palettes for every background, Pyxel Clear allows you to:
1.  **Load your existing library:** Point the tool to your project's palette folder.
2.  **Input your new scene:** Load a high-fidelity image with more than 4 colors.
3.  **Map & Re-use:** The tool identifies which of your *existing* palettes best represent each 8x8 tile and recolors the scene to match.

**The Result:** Your scene gets that authentic GBC look using **zero** new palette slots.

## ✨ Features
* **Palette Library Mapping:** Uses your established `.hex` or `.txt` library to recolor images.
* **Intelligent Tile-Assignment:** Automatically handles the 8-palette limit by calculating the mathematical best fit for every 8x8 grid cell.
* **Indexed Atlas Output:** Generates a high-res reference map with **"P0-P7" labels** so you know exactly how to configure your scene in GB Studio.
* **Green-Shade Preview:** Instantly see how your assets will look under classic Game Boy hardware constraints.
* **Dithering Support:** Maintains gradients and depth even when restricted to a 4-color-per-tile limit.

## 📦 What's in the Box?
When you run a process, Pyxel Clear exports:
* **`step1_recolored.png`**: Your final optimized scene.
* **`step2_green_preview.png`**: Hardware-accurate contrast check.
* **`step2_atlas.png`**: A coordinate map showing Palette Indices (P0, P1, etc.) for every tile.
* **`step2_palettes.json`**: A data file of the selected palettes for your records.



## 📥 Getting Started
1.  Download `Pyxel_Clear_v1.0.0.zip` from the **Releases** tab.
2.  Extract the ZIP and run `PyxelClear.exe`.
3.  *Note:* Because the app is not digitally signed, Windows may show a "SmartScreen" warning. Click **More Info** -> **Run Anyway**.

## 💬 Community & Feedback
This tool was built to help the GB Studio community save storage space and get that authentic "frozen" palette footprint. If you have suggestions for new output formats or features, feel free to open an issue or reach out!

### 📄 Project Links

* **Source Code:** [Pyxel_Tile.py (main branch)](https://github.com/contactpyxelmorph-afk/Pyxel-Clear/blob/main/Pyxel_Clear.py)
