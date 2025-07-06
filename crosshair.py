import tkinter as tk
from tkinter import colorchooser, messagebox
import ctypes
import json
import os

CONFIG_FILE = "crosshair_config.json"

class CrosshairOverlay:
    def __init__(self):
        self.size = 20
        self.color = "#FF0000"
        self.thickness = 2
        self.style = "Classique"  # Classique, Cercle, Point
        self.alpha = 0.3
        self.show_crosshair = True
        self.bg_color = "white"  # couleur transparente en blanc par défaut

        self.root = tk.Tk()
        self.root.title("Crosshair Overlay Settings")
        self.root.geometry("350x320")
        self.root.resizable(False, False)

        self.load_config()
        self.create_controls()

        self.root.after(100, self.create_overlay)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def create_overlay(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.wm_attributes("-topmost", True)
        self.overlay.wm_attributes("-transparentcolor", self.bg_color)
        self.overlay.attributes("-alpha", self.alpha)

        self.canvas = tk.Canvas(self.overlay, width=screen_width, height=screen_height,
                                bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()

        # Rendre clic-through
        hwnd = ctypes.windll.user32.GetParent(self.overlay.winfo_id())
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, ex_style | 0x80000 | 0x20)

        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

        self.overlay.bind("<Up>", self.move_up)
        self.overlay.bind("<Down>", self.move_down)
        self.overlay.bind("<Left>", self.move_left)
        self.overlay.bind("<Right>", self.move_right)
        self.overlay.bind("<Escape>", lambda e: self.root.destroy())

        self.draw_crosshair()

    def create_controls(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # Taille
        tk.Label(frame, text="Taille:").grid(row=0, column=0, sticky="w")
        self.size_var = tk.IntVar(value=self.size)
        size_slider = tk.Scale(frame, from_=5, to=100, orient="horizontal", variable=self.size_var, command=self.update_size)
        size_slider.grid(row=0, column=1, sticky="ew")

        # Épaisseur
        tk.Label(frame, text="Épaisseur:").grid(row=1, column=0, sticky="w")
        self.thickness_var = tk.IntVar(value=self.thickness)
        thickness_slider = tk.Scale(frame, from_=1, to=10, orient="horizontal", variable=self.thickness_var, command=self.update_thickness)
        thickness_slider.grid(row=1, column=1, sticky="ew")

        # Couleur du crosshair
        tk.Label(frame, text="Couleur:").grid(row=2, column=0, sticky="w")
        self.color_button = tk.Button(frame, text="Choisir couleur", command=self.choose_color, bg=self.color, fg="white")
        self.color_button.grid(row=2, column=1, sticky="ew")

        # Style du crosshair
        tk.Label(frame, text="Style:").grid(row=3, column=0, sticky="w")
        self.style_var = tk.StringVar(value=self.style)
        style_options = ["Classique", "Cercle", "Point"]
        style_menu = tk.OptionMenu(frame, self.style_var, *style_options, command=self.update_style)
        style_menu.grid(row=3, column=1, sticky="ew")

        # Transparence overlay
        tk.Label(frame, text="Transparence:").grid(row=4, column=0, sticky="w")
        self.alpha_var = tk.DoubleVar(value=self.alpha)
        alpha_slider = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", variable=self.alpha_var, command=self.update_alpha)
        alpha_slider.grid(row=4, column=1, sticky="ew")

        # Couleur fond transparent
        tk.Label(frame, text="Couleur fond:").grid(row=5, column=0, sticky="w")
        self.bg_color_button = tk.Button(frame, text="Choisir couleur", command=self.choose_bg_color, bg=self.bg_color)
        self.bg_color_button.grid(row=5, column=1, sticky="ew")

        # Afficher / Masquer crosshair
        self.show_var = tk.BooleanVar(value=self.show_crosshair)
        show_check = tk.Checkbutton(frame, text="Afficher crosshair", variable=self.show_var, command=self.toggle_crosshair)
        show_check.grid(row=6, column=0, columnspan=2, sticky="w", pady=10)

        frame.columnconfigure(1, weight=1)

    def update_size(self, val):
        self.size = int(val)
        self.draw_crosshair()

    def update_thickness(self, val):
        self.thickness = int(val)
        self.draw_crosshair()

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choisir la couleur du crosshair", initialcolor=self.color)
        if color_code[1]:
            self.color = color_code[1]
            self.color_button.configure(bg=self.color)
            self.draw_crosshair()

    def update_style(self, val):
        self.style = val
        self.draw_crosshair()

    def update_alpha(self, val):
        self.alpha = float(val)
        if hasattr(self, 'overlay'):
            self.overlay.attributes("-alpha", self.alpha)

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choisir la couleur du fond transparent", initialcolor=self.bg_color)
        if color_code[1]:
            self.bg_color = color_code[1]
            self.bg_color_button.configure(bg=self.bg_color)
            if hasattr(self, 'overlay'):
                self.overlay.wm_attributes("-transparentcolor", self.bg_color)
                self.canvas.configure(bg=self.bg_color)
            self.draw_crosshair()

    def toggle_crosshair(self):
        self.show_crosshair = self.show_var.get()
        if hasattr(self, 'canvas'):
            if self.show_crosshair:
                self.draw_crosshair()
            else:
                self.canvas.delete("all")

    def draw_crosshair(self):
        if not hasattr(self, 'canvas') or not self.show_crosshair:
            return
        self.canvas.delete("all")
        s = self.size
        x = self.center_x
        y = self.center_y
        t = self.thickness
        c = self.color

        if self.style == "Classique":
            self.canvas.create_line(x - s, y, x + s, y, fill=c, width=t)
            self.canvas.create_line(x, y - s, x, y + s, fill=c, width=t)
        elif self.style == "Cercle":
            self.canvas.create_oval(x - s, y - s, x + s, y + s, outline=c, width=t)
        elif self.style == "Point":
            self.canvas.create_oval(x - t, y - t, x + t, y + t, fill=c, outline=c)

    def move_up(self, event):
        self.center_y = max(0, self.center_y - 5)
        self.draw_crosshair()

    def move_down(self, event):
        self.center_y = min(self.overlay.winfo_height(), self.center_y + 5)
        self.draw_crosshair()

    def move_left(self, event):
        self.center_x = max(0, self.center_x - 5)
        self.draw_crosshair()

    def move_right(self, event):
        self.center_x = min(self.overlay.winfo_width(), self.center_x + 5)
        self.draw_crosshair()

    def on_close(self):
        self.save_config()
        self.root.destroy()

    def save_config(self):
        data = {
            "size": self.size,
            "color": self.color,
            "thickness": self.thickness,
            "style": self.style,
            "alpha": self.alpha,
            "bg_color": self.bg_color,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "show_crosshair": self.show_crosshair
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder la configuration:\n{e}")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.size = data.get("size", self.size)
                self.color = data.get("color", self.color)
                self.thickness = data.get("thickness", self.thickness)
                self.style = data.get("style", self.style)
                self.alpha = data.get("alpha", self.alpha)
                self.bg_color = data.get("bg_color", self.bg_color)
                self.center_x = data.get("center_x", None)
                self.center_y = data.get("center_y", None)
                self.show_crosshair = data.get("show_crosshair", True)
        except Exception as e:
            messagebox.showwarning("Attention", f"Impossible de charger la configuration:\n{e}")

if __name__ == "__main__":
    CrosshairOverlay()
