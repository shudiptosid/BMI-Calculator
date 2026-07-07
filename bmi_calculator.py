import tkinter as tk
from tkinter import ttk
import math


# ─────────────────────────────────────────────
#  COLOUR PALETTE  (minimal dark theme)
# ─────────────────────────────────────────────
BG        = "#0f1117"
CARD      = "#1a1d27"
BORDER    = "#2a2d3a"
TEXT_PRI  = "#e8eaf0"
TEXT_SEC  = "#8b8fa8"
ACCENT    = "#6c63ff"
DANGER    = "#ef4444"
INPUT_BG  = "#12141c"

BMI_COLORS = {
    "gauge_bg":     "#1e2130",
    "severe_under": "#3b82f6",
    "underweight":  "#60a5fa",
    "normal":       "#22c55e",
    "overweight":   "#f59e0b",
    "obese_1":      "#f97316",
    "obese_2":      "#ef4444",
    "obese_3":      "#dc2626",
}

BMI_RANGES = [
    (0,    16.0,  "Severely Underweight",  "Consult a doctor immediately",          BMI_COLORS["severe_under"]),
    (16.0, 18.5,  "Underweight",           "You need to gain weight",               BMI_COLORS["underweight"]),
    (18.5, 25.0,  "Normal / Perfect",      "Great! Keep it up",                     BMI_COLORS["normal"]),
    (25.0, 30.0,  "Overweight",            "Needs improvement – diet & exercise",   BMI_COLORS["overweight"]),
    (30.0, 35.0,  "Obesity – Class I",     "Moderate obesity, seek guidance",       BMI_COLORS["obese_1"]),
    (35.0, 40.0,  "Obesity – Class II",    "Severe obesity, consult a specialist",  BMI_COLORS["obese_2"]),
    (40.0, 100.0, "Obesity – Class III",   "Morbid obesity, medical care needed",   BMI_COLORS["obese_3"]),
]


# ─────────────────────────────────────────────
#  UNIT CONVERSION HELPERS
# ─────────────────────────────────────────────
def height_to_meters(value, unit):
    conversions = {
        "Meter (m)":       value,
        "Centimeter (cm)": value / 100,
        "Millimeter (mm)": value / 1000,
        "Feet (ft)":       value * 0.3048,
        "Inches (in)":     value * 0.0254,
    }
    return conversions[unit]


def weight_to_kg(value, unit):
    conversions = {
        "Kilogram (kg)":  value,
        "Pound (lbs/lb)": value * 0.453592,
        "Gram (g)":       value / 1000,
    }
    return conversions[unit]


def get_bmi_category(bmi):
    for lo, hi, label, tip, color in BMI_RANGES:
        if lo <= bmi < hi:
            return label, tip, color
    last = BMI_RANGES[-1]
    return last[2], last[3], last[4]


# ─────────────────────────────────────────────
#  GAUGE  (arc-style semi-circle)
# ─────────────────────────────────────────────
class GaugeWidget(tk.Canvas):
    W, H     = 380, 210
    CX, CY   = 190, 195
    R_OUT    = 160
    R_IN     = 105
    NEEDLE_R = 155

    GAUGE_SEGMENTS = [
        (0,    16,   BMI_COLORS["severe_under"]),
        (16,   18.5, BMI_COLORS["underweight"]),
        (18.5, 25,   BMI_COLORS["normal"]),
        (25,   30,   BMI_COLORS["overweight"]),
        (30,   35,   BMI_COLORS["obese_1"]),
        (35,   40,   BMI_COLORS["obese_2"]),
        (40,   50,   BMI_COLORS["obese_3"]),
    ]
    BMI_MIN, BMI_MAX = 10, 50

    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=BG, highlightthickness=0, **kwargs)
        self._bmi      = None
        self._needle   = None
        self._val_text = None
        self._cat_text = None
        self._draw_static()

    def _bmi_to_angle(self, bmi):
        bmi   = max(self.BMI_MIN, min(self.BMI_MAX, bmi))
        ratio = (bmi - self.BMI_MIN) / (self.BMI_MAX - self.BMI_MIN)
        return 180 - ratio * 180

    def _arc_coords(self, r):
        return (self.CX - r, self.CY - r, self.CX + r, self.CY + r)

    def _draw_static(self):
        # background fill
        self.create_arc(*self._arc_coords(self.R_OUT + 8),
                        start=0, extent=180,
                        fill=BMI_COLORS["gauge_bg"], outline="", style=tk.PIESLICE)

        # coloured arc segments
        total_range = self.BMI_MAX - self.BMI_MIN
        for lo, hi, color in self.GAUGE_SEGMENTS:
            lo_c = max(lo, self.BMI_MIN)
            hi_c = min(hi, self.BMI_MAX)
            if lo_c >= hi_c:
                continue
            start_a  = self._bmi_to_angle(hi_c)
            extent_a = ((hi_c - lo_c) / total_range) * 180
            self.create_arc(*self._arc_coords(self.R_OUT),
                            start=start_a, extent=extent_a,
                            fill=color, outline="", style=tk.ARC, width=30)

        # donut mask
        self.create_arc(*self._arc_coords(self.R_IN),
                        start=0, extent=180,
                        fill=BG, outline="", style=tk.PIESLICE)

        # base line
        self.create_line(self.CX - self.R_OUT - 5, self.CY,
                         self.CX + self.R_OUT + 5, self.CY,
                         fill=BORDER, width=2)

        # tick labels
        for bmi_val in [10, 16, 18.5, 25, 30, 35, 40, 50]:
            angle_rad = math.radians(self._bmi_to_angle(bmi_val))
            lx = self.CX + (self.R_IN - 18) * math.cos(angle_rad)
            ly = self.CY - (self.R_IN - 18) * math.sin(angle_rad)
            label = str(int(bmi_val)) if bmi_val == int(bmi_val) else str(bmi_val)
            self.create_text(lx, ly, text=label,
                             fill=TEXT_SEC, font=("Segoe UI", 7, "bold"))

        # centre placeholders
        self._val_text = self.create_text(self.CX, self.CY - 30,
                                          text="--", fill=TEXT_PRI,
                                          font=("Segoe UI", 32, "bold"))
        self.create_text(self.CX, self.CY - 10,
                         text="BMI", fill=TEXT_SEC,
                         font=("Segoe UI", 9))
        self._cat_text = self.create_text(self.CX, self.CY + 10,
                                          text="Enter values to calculate",
                                          fill=TEXT_SEC,
                                          font=("Segoe UI", 9, "italic"),
                                          width=160, justify="center")

    def _draw_needle(self, angle_deg, color):
        if self._needle:
            self.delete(self._needle)
        angle_rad = math.radians(angle_deg)
        x2 = self.CX + self.NEEDLE_R * math.cos(angle_rad)
        y2 = self.CY - self.NEEDLE_R * math.sin(angle_rad)
        self._needle = self.create_line(self.CX, self.CY, x2, y2,
                                        fill=color, width=3, capstyle=tk.ROUND)
        self.create_oval(self.CX - 6, self.CY - 6,
                         self.CX + 6, self.CY + 6,
                         fill=color, outline=BG, width=2)

    def _animate_needle(self, start_a, end_a, steps, color, step=0):
        if step > steps:
            return
        current = start_a + (end_a - start_a) * (step / steps)
        self._draw_needle(current, color)
        self.after(16, self._animate_needle, start_a, end_a, steps, color, step + 1)

    def update_bmi(self, bmi, category, color):
        target_angle = self._bmi_to_angle(bmi)
        start_angle  = self._bmi_to_angle(self._bmi) if self._bmi else 180
        self._bmi    = bmi
        self.itemconfig(self._val_text, text=f"{bmi:.1f}", fill=color)
        self.itemconfig(self._cat_text, text=category, fill=color)
        self._animate_needle(start_angle, target_angle, 30, color)

    def reset(self):
        self._bmi = None
        if self._needle:
            self.delete(self._needle)
            self._needle = None
        self.itemconfig(self._val_text, text="--",   fill=TEXT_PRI)
        self.itemconfig(self._cat_text, text="Enter values to calculate", fill=TEXT_SEC)


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class BMIApp(tk.Tk):
    HEIGHT_UNITS = ["Meter (m)", "Centimeter (cm)", "Millimeter (mm)",
                    "Feet (ft)", "Inches (in)"]
    WEIGHT_UNITS = ["Kilogram (kg)", "Pound (lbs/lb)", "Gram (g)"]

    def __init__(self):
        super().__init__()
        self.title("BMI Calculator")
        self.resizable(False, False)
        self.configure(bg=BG)
        self._center_window(820, 660)
        self._build_ui()

    def _center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(28, 0))
        tk.Label(hdr, text="BMI Calculator",
                 bg=BG, fg=TEXT_PRI,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(hdr, text="Body Mass Index",
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 11)).pack(side="left", padx=(12, 0), pady=(6, 0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(14, 0))

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=20)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        self._build_left(body)
        self._build_right(body)

        # Footer
        tk.Label(self, text="BMI is a general screening tool and not a diagnostic measure.",
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8)).pack(pady=(0, 12))

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Height section
        self._section(left, "HEIGHT")
        hcard = self._card(left)
        self.h_unit = tk.StringVar(value=self.HEIGHT_UNITS[1])
        self._dropdown(hcard, "Unit", self.h_unit, self.HEIGHT_UNITS)
        self.h_entry_var = tk.StringVar()
        self.h_entry = self._entry(hcard, "Value", self.h_entry_var, "e.g. 170")

        # Weight section
        self._section(left, "WEIGHT")
        wcard = self._card(left)
        self.w_unit = tk.StringVar(value=self.WEIGHT_UNITS[0])
        self._dropdown(wcard, "Unit", self.w_unit, self.WEIGHT_UNITS)
        self.w_entry_var = tk.StringVar()
        self.w_entry = self._entry(wcard, "Value", self.w_entry_var, "e.g. 65")

        # Buttons
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill="x", pady=(18, 0))
        self._btn(btn_row, "  Calculate BMI  ", self._calculate,
                  bg=ACCENT, fg="white").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn(btn_row, "  Reset  ", self._reset,
                  bg=CARD, fg=TEXT_SEC).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.info_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.info_var,
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8, "italic"),
                 justify="left", anchor="w").pack(fill="x", pady=(10, 0))

        self.err_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.err_var,
                 bg=BG, fg=DANGER,
                 font=("Segoe UI", 9),
                 justify="left", anchor="w").pack(fill="x")

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        # Gauge frame
        gauge_frame = tk.Frame(right, bg=CARD,
                               highlightbackground=BORDER,
                               highlightthickness=1)
        gauge_frame.pack(fill="x")
        self.gauge = GaugeWidget(gauge_frame)
        self.gauge.pack(pady=(10, 5))

        # BMI Range table
        self._section(right, "BMI RANGES")
        rcard = self._card(right, pady=0)
        self.range_rows = []

        for lo, hi, label, tip, color in BMI_RANGES:
            row_frame = tk.Frame(rcard, bg=CARD)
            row_frame.pack(fill="x", pady=1)

            indicator = tk.Frame(row_frame, bg=color, width=4)
            indicator.pack(side="left", fill="y")

            info = tk.Frame(row_frame, bg=CARD)
            info.pack(side="left", fill="x", expand=True, padx=10, pady=5)

            range_str = f"{lo}  \u2013  {hi}" if hi < 100 else f"{lo}+"
            lbl_title = tk.Label(info, text=label, bg=CARD, fg=TEXT_PRI,
                                 font=("Segoe UI", 9, "bold"), anchor="w")
            lbl_title.pack(fill="x")
            lbl_sub = tk.Label(info, text=f"BMI {range_str}   \u2022   {tip}",
                               bg=CARD, fg=TEXT_SEC,
                               font=("Segoe UI", 8), anchor="w")
            lbl_sub.pack(fill="x")

            self.range_rows.append((lo, hi, row_frame, indicator, lbl_title, lbl_sub, color))

    # ── widget helpers ────────────────────────────────────────────────────────
    def _section(self, parent, text):
        tk.Label(parent, text=text,
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8, "bold"),
                 anchor="w").pack(fill="x", pady=(14, 4))

    def _card(self, parent, pady=8):
        f = tk.Frame(parent, bg=CARD,
                     highlightbackground=BORDER,
                     highlightthickness=1)
        f.pack(fill="x", pady=pady)
        return f

    def _dropdown(self, parent, label, var, options):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=14, pady=(10, 4))
        tk.Label(row, text=label, bg=CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 9), width=6, anchor="w").pack(side="left")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.TCombobox",
                        fieldbackground=INPUT_BG, background=INPUT_BG,
                        foreground=TEXT_PRI, selectbackground=ACCENT,
                        selectforeground="white", arrowcolor=TEXT_SEC, borderwidth=0)
        style.map("Custom.TCombobox",
                  fieldbackground=[("readonly", INPUT_BG)],
                  foreground=[("readonly", TEXT_PRI)])

        cb = ttk.Combobox(row, textvariable=var, values=options,
                          state="readonly", style="Custom.TCombobox",
                          font=("Segoe UI", 9))
        cb.pack(side="left", fill="x", expand=True, padx=(8, 0))

    def _entry(self, parent, label, var, placeholder=""):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=14, pady=(4, 10))
        tk.Label(row, text=label, bg=CARD, fg=TEXT_SEC,
                 font=("Segoe UI", 9), width=6, anchor="w").pack(side="left")

        e = tk.Entry(row, textvariable=var,
                     bg=INPUT_BG, fg=TEXT_PRI,
                     insertbackground=ACCENT, relief="flat",
                     font=("Segoe UI", 10),
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=5)
        e.bind("<Return>", lambda _: self._calculate())

        e.insert(0, placeholder)
        e.config(fg=TEXT_SEC)
        e._placeholder = placeholder

        def on_focus_in(event, entry=e):
            if entry.get() == entry._placeholder:
                entry.delete(0, "end")
                entry.config(fg=TEXT_PRI)

        def on_focus_out(event, entry=e):
            if not entry.get():
                entry.insert(0, entry._placeholder)
                entry.config(fg=TEXT_SEC)

        e.bind("<FocusIn>",  on_focus_in)
        e.bind("<FocusOut>", on_focus_out)
        return e

    @staticmethod
    def _btn(parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, relief="flat", bd=0,
                         font=("Segoe UI", 10, "bold"),
                         cursor="hand2",
                         activebackground=ACCENT, activeforeground="white",
                         padx=16, pady=10)

    # ── logic ─────────────────────────────────────────────────────────────────
    def _calculate(self):
        self.err_var.set("")
        self.info_var.set("")

        # height
        h_raw = self.h_entry.get().strip()
        if not h_raw or h_raw == self.h_entry._placeholder:
            self.err_var.set("  Please enter a height value.")
            return
        try:
            h_num = float(h_raw)
            if h_num <= 0:
                raise ValueError
        except ValueError:
            self.err_var.set("  Height must be a positive number.")
            return

        # weight
        w_raw = self.w_entry.get().strip()
        if not w_raw or w_raw == self.w_entry._placeholder:
            self.err_var.set("  Please enter a weight value.")
            return
        try:
            w_num = float(w_raw)
            if w_num <= 0:
                raise ValueError
        except ValueError:
            self.err_var.set("  Weight must be a positive number.")
            return

        # convert
        h_m  = height_to_meters(h_num, self.h_unit.get())
        w_kg = weight_to_kg(w_num, self.w_unit.get())

        if h_m < 0.5 or h_m > 3.0:
            self.err_var.set("  Height value seems unrealistic. Check unit selection.")
            return
        if w_kg < 2 or w_kg > 700:
            self.err_var.set("  Weight value seems unrealistic. Check unit selection.")
            return

        bmi = w_kg / (h_m ** 2)
        label, tip, color = get_bmi_category(bmi)

        self.info_var.set(
            f"Converted  ->  Height: {h_m:.4f} m  |  Weight: {w_kg:.2f} kg"
        )
        self.gauge.update_bmi(bmi, label, color)
        self._highlight_range(bmi)

    def _highlight_range(self, bmi):
        for lo, hi, row_f, indicator, lbl_t, lbl_s, color in self.range_rows:
            if lo <= bmi < hi:
                row_f.config(bg="#1f2235")
                indicator.config(width=6)
                lbl_t.config(bg="#1f2235", fg=color)
                lbl_s.config(bg="#1f2235", fg=TEXT_PRI)
            else:
                row_f.config(bg=CARD)
                indicator.config(width=4)
                lbl_t.config(bg=CARD, fg=TEXT_PRI)
                lbl_s.config(bg=CARD, fg=TEXT_SEC)

    def _reset(self):
        self.h_entry.delete(0, "end")
        self.h_entry.insert(0, self.h_entry._placeholder)
        self.h_entry.config(fg=TEXT_SEC)

        self.w_entry.delete(0, "end")
        self.w_entry.insert(0, self.w_entry._placeholder)
        self.w_entry.config(fg=TEXT_SEC)

        self.h_unit.set(self.HEIGHT_UNITS[1])
        self.w_unit.set(self.WEIGHT_UNITS[0])
        self.err_var.set("")
        self.info_var.set("")
        self.gauge.reset()

        for _, _, row_f, indicator, lbl_t, lbl_s, color in self.range_rows:
            row_f.config(bg=CARD)
            indicator.config(width=4)
            lbl_t.config(bg=CARD, fg=TEXT_PRI)
            lbl_s.config(bg=CARD, fg=TEXT_SEC)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
