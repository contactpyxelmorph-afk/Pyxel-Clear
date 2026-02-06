import os
import sys
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw


# --- BUNDLING HELPER ---
def resource_path(relative_path):
    import sys, os
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# --- UTILITIES ---
def dist_sq(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2))


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(c):
    return "#{:02X}{:02X}{:02X}".format(*c)


def clamp(v):
    return max(0, min(255, int(v)))


def extract_palettes_from_folder(folder_path):
    hex_pattern = re.compile(r'#?([A-Fa-f0-9]{6})')
    unique_palettes = []
    filenames = sorted(os.listdir(folder_path))
    for filename in filenames:
        file_path = os.path.join(folder_path, filename)
        if not os.path.isfile(file_path): continue
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                matches = hex_pattern.findall(content)
                colors = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in matches]
                for i in range(0, len(colors) - 3, 4):
                    p = list(colors[i:i + 4])
                    if p not in unique_palettes: unique_palettes.append(p)
        except:
            continue
    return unique_palettes


# --- APP ---
class PaletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyxel Clear")
        self.root.geometry("600x850") # Set a default window size

        # Set Silver Grey background
        self.bg_color = "#C0C0C0"
        self.root.configure(bg=self.bg_color)

        # Assets Paths - UPDATED FOR BUNDLING
        # These now look inside the .exe at runtime
        self.logo_path = resource_path("l_png.png")
        self.icon_path = resource_path("l_ico.ico")

        # Set Window Icon (top left)
        try:
            self.root.iconbitmap(self.icon_path)
        except:
            # Fallback for systems that don't support .ico directly
            pass

        self.img_path = ""
        self.folder_path = ""
        self.out_path = os.getcwd()
        self.processed_img = None
        self.final_pals = []
        self.tile_assignments = []
        self.use_dithering = tk.BooleanVar(value=False)

        self.setup_ui()

    def setup_ui(self):
        # Configure styles for ttk to match silver grey
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color)
        style.configure("TCheckbutton", background=self.bg_color)

        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky="nsew")

        # 1. Logo at Center
        try:
            raw_logo = Image.open(self.logo_path)
            # Resize logo slightly if it's too large for the UI
            raw_logo.thumbnail((250, 250))
            self.logo_img = ImageTk.PhotoImage(raw_logo)
            logo_label = tk.Label(frame, image=self.logo_img, bg=self.bg_color)
            logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        except:
            ttk.Label(frame, text="[ Logo Not Found ]", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=20)

        # 2. File Selection Buttons
        ttk.Button(frame, text="1. Select Input Image", command=self.load_image).grid(row=1, column=0, pady=5,
                                                                                      sticky="w")
        self.img_label = ttk.Label(frame, text="No file selected", width=45)
        self.img_label.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Button(frame, text="2. Select Palette Folder", command=self.load_folder).grid(row=2, column=0, pady=5,
                                                                                          sticky="w")
        self.folder_label = ttk.Label(frame, text="No folder selected", width=45)
        self.folder_label.grid(row=2, column=1, padx=5, sticky="w")

        ttk.Button(frame, text="3. Select Output Folder", command=self.load_out_folder).grid(row=3, column=0, pady=5,
                                                                                             sticky="w")
        self.out_label = ttk.Label(frame, text=self.out_path, width=45)
        self.out_label.grid(row=3, column=1, padx=5, sticky="w")

        # 3. Options
        opt_frame = ttk.Frame(frame)
        opt_frame.grid(row=4, column=0, columnspan=2, pady=15, sticky="w")

        ttk.Label(opt_frame, text="Max Palettes (N):").pack(side="left")
        self.max_pals_entry = ttk.Entry(opt_frame, width=5)
        self.max_pals_entry.insert(0, "8")
        self.max_pals_entry.pack(side="left", padx=5)

        ttk.Checkbutton(opt_frame, text="Enable Dithering", variable=self.use_dithering).pack(side="left", padx=20)

        # 4. Action Buttons
        self.btn_step1 = ttk.Button(frame, text="RUN STEP 1: Recolor & Choose Palettes", command=self.run_step1)
        self.btn_step1.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

        self.btn_step2 = ttk.Button(frame, text="RUN STEP 2: Generate Map & Assets", command=self.run_step2,
                                    state="disabled")
        self.btn_step2.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")

        # 5. Preview Area
        self.preview_canvas = tk.Label(frame, text="Preview Area", background="#A0A0A0", relief="sunken", width=60,
                                       height=15)
        self.preview_canvas.grid(row=7, column=0, columnspan=2, pady=20)

    # --- LOGIC METHODS ---
    def load_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path: self.img_label.config(text=os.path.basename(self.img_path))

    def load_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path: self.folder_label.config(text=self.folder_path)

    def load_out_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.out_path = path
            self.out_label.config(text=self.out_path)

    def run_step1(self):
        # ... (Identical to your provided Step 1 logic) ...
        if not self.img_path or not self.folder_path:
            messagebox.showerror("Error", "Missing inputs.")
            return

        img = Image.open(self.img_path).convert("RGB")
        w, h = img.size
        max_p = int(self.max_pals_entry.get())
        library = extract_palettes_from_folder(self.folder_path)
        dither_enabled = self.use_dithering.get()

        if not library:
            messagebox.showerror("Error", "No valid palettes found.")
            return

        # Visual inventory of input palettes
        sw_s = 40
        input_pals_img = Image.new("RGB", (sw_s * 4, sw_s * len(library)))
        i_draw = ImageDraw.Draw(input_pals_img)
        for i, pal in enumerate(library):
            for j, c in enumerate(pal):
                i_draw.rectangle([j * sw_s, i * sw_s, (j + 1) * sw_s, (i + 1) * sw_s], fill=c)
        input_pals_img.save(os.path.join(self.out_path, "step1_all_inputs.png"))

        tiles_wide = (w + 7) // 8
        tiles_high = (h + 7) // 8
        tiles_data = []
        for ty in range(tiles_high):
            for tx in range(tiles_wide):
                x, y = tx * 8, ty * 8
                tile_px = [img.getpixel((x + dx, y + dy)) if x + dx < w and y + dy < h else (0, 0, 0)
                           for dy in range(8) for dx in range(8)]
                tiles_data.append(tile_px)

        def get_weighted_dist(c1, c2):
            dr = (c1[0] - c2[0]) ** 2 * 0.30
            dg = (c1[1] - c2[1]) ** 2 * 0.59
            db = (c1[2] - c2[2]) ** 2 * 0.11
            return dr + dg + db

        def get_palette_score(tile, pal):
            base_error = sum(min(get_weighted_dist(px, pc) for pc in pal) for px in tile)
            if dither_enabled:
                internal_dist = sum(get_weighted_dist(pal[i], pal[j]) for i in range(4) for j in range(i + 1, 4))
                return base_error + (internal_dist * 0.1)
            return base_error

        error_matrix = [[get_palette_score(tile, pal) for pal in library] for tile in tiles_data]
        selected_indices = []
        best_errs = [float('inf')] * len(tiles_data)

        for _ in range(min(max_p, len(library))):
            best_gain, best_idx = -1, -1
            for p_idx in range(len(library)):
                if p_idx in selected_indices: continue
                gain = sum(max(0, best_errs[t] - error_matrix[t][p_idx]) for t in range(len(tiles_data)))
                if gain > best_gain: best_gain, best_idx = gain, p_idx
            if best_idx == -1: break
            selected_indices.append(best_idx)
            for t in range(len(tiles_data)):
                best_errs[t] = min(best_errs[t], error_matrix[t][selected_indices[-1]])

        self.final_pals = [library[i] for i in selected_indices]

        self.tile_assignments = []
        for t_idx in range(len(tiles_data)):
            best_choice = 0
            min_err = float('inf')
            for i, pal in enumerate(self.final_pals):
                err = get_palette_score(tiles_data[t_idx], pal)
                if err < min_err:
                    min_err = err
                    best_choice = i
            self.tile_assignments.append(best_choice)

        self.processed_img = Image.new("RGB", (w, h))
        out_pix = self.processed_img.load()
        pixels = [list(p) for p in list(img.getdata())]

        for y in range(h):
            y_offset, ty = y * w, y // 8
            for x in range(w):
                tx = x // 8
                t_idx = ty * tiles_wide + tx
                pal = self.final_pals[self.tile_assignments[t_idx]]
                idx = y_offset + x
                old_rgb = pixels[idx]
                new_rgb = min(pal, key=lambda c: get_weighted_dist(old_rgb, c))
                out_pix[x, y] = new_rgb
                if dither_enabled:
                    err = [(old_rgb[i] - new_rgb[i]) / 8 for i in range(3)]
                    neighbors = [(1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2)]
                    for dx, dy in neighbors:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            n_idx = ny * w + nx
                            for i in range(3):
                                pixels[n_idx][i] = clamp(pixels[n_idx][i] + err[i])

        self.processed_img.save(os.path.join(self.out_path, "step1_recolored.png"))
        ratio = min(350 / w, 350 / h)
        prev = self.processed_img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(prev)
        self.preview_canvas.config(image=self.tk_img, text="", width=350, height=350)
        self.btn_step2.config(state="normal")
        messagebox.showinfo("Done", "Recolor complete!")

    def run_step2(self):
        GB_HEX = ["#E0F8CF", "#86C06C", "#071821", "#306850"]
        gb_rgbs = [hex_to_rgb(h) for h in GB_HEX]
        ATLAS_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
                        (255, 255, 255), (255, 165, 0)]

        w, h = self.processed_img.size
        green_preview = Image.new("RGB", (w, h))
        atlas_img = Image.new("RGB", (w, h))
        atlas_draw = ImageDraw.Draw(atlas_img)

        t_idx = 0
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                p_idx = self.tile_assignments[t_idx]
                target_pal = self.final_pals[p_idx]

                # Fill the base atlas tile
                atlas_draw.rectangle([x, y, x + 7, y + 7], fill=ATLAS_COLORS[p_idx % len(ATLAS_COLORS)])

                # Generate the Green/Gameboy preview
                for dy in range(8):
                    for dx in range(8):
                        if x + dx < w and y + dy < h:
                            curr_c = self.processed_img.getpixel((x + dx, y + dy))
                            try:
                                color_idx = target_pal.index(curr_c)
                            except:
                                color_idx = [dist_sq(curr_c, pc) for pc in target_pal].index(
                                    min([dist_sq(curr_c, pc) for pc in target_pal]))
                            green_preview.putpixel((x + dx, y + dy), gb_rgbs[color_idx])
                t_idx += 1

        # --- SCALE UP ATLAS & DRAW LABELS ---
        scale = 32  # Increased scale to make text clearer
        large_atlas = atlas_img.resize((w * scale, h * scale), resample=Image.NEAREST)
        l_draw = ImageDraw.Draw(large_atlas)

        t_idx = 0
        for y_tile, y_pos in enumerate(range(0, h, 8)):
            for x_tile, x_pos in enumerate(range(0, w, 8)):
                p_idx = self.tile_assignments[t_idx]

                # Coordinates (Top Left)
                coord_text = f"{x_tile},{y_tile}"
                l_draw.text((x_pos * scale + 2, y_pos * scale + 2), coord_text, fill=(0, 0, 0))

                # PALETTE INDEX (Center - Bold)
                pal_label = f"P{p_idx}"
                # Draw a small shadow/border for readability
                center_x, center_y = (x_pos * scale) + (scale // 2) - 5, (y_pos * scale) + (scale // 2) - 5
                l_draw.text((center_x + 1, center_y + 1), pal_label, fill=(255, 255, 255))  # Shadow
                l_draw.text((center_x, center_y), pal_label, fill=(0, 0, 0))  # Main text

                t_idx += 1

        # --- SAVE ASSETS ---
        json_data = {f"palette_{idx}": [rgb_to_hex(c) for c in pal] for idx, pal in enumerate(self.final_pals)}
        with open(os.path.join(self.out_path, "step2_palettes.json"), "w") as f:
            json.dump(json_data, f, indent=4)

        swatch_img = Image.new("RGB", (160, 40 * len(self.final_pals)))
        s_draw = ImageDraw.Draw(swatch_img)
        for i, pal in enumerate(self.final_pals):
            for j, c in enumerate(pal):
                s_draw.rectangle([j * 40, i * 40, (j + 1) * 40, (i + 1) * 40], fill=c)
                # Add text label to swatches too
                s_draw.text((5, i * 40 + 5), f"P{i}", fill=(255, 255, 255) if sum(pal[0]) < 380 else (0, 0, 0))

        green_preview.save(os.path.join(self.out_path, "step2_green_preview.png"))
        large_atlas.save(os.path.join(self.out_path, "step2_atlas.png"))
        swatch_img.save(os.path.join(self.out_path, "step2_palettes.png"))
        messagebox.showinfo("Success", "Assets generated with palette indexing!")


if __name__ == "__main__":
    root = tk.Tk()
    app = PaletteApp(root)
    root.mainloop()