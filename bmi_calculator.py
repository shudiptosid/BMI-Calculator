import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import math
import json
import os
import datetime


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

# Added the unique category key as the 6th element in each range tuple
BMI_RANGES = [
    (0,    16.0,  "Severely Underweight",  "Consult a doctor immediately",          BMI_COLORS["severe_under"], "severe_under"),
    (16.0, 18.5,  "Underweight",           "You need to gain weight",               BMI_COLORS["underweight"],  "underweight"),
    (18.5, 25.0,  "Normal / Perfect",      "Great! Keep it up",                     BMI_COLORS["normal"],       "normal"),
    (25.0, 30.0,  "Overweight",            "Needs improvement – diet & exercise",   BMI_COLORS["overweight"],   "overweight"),
    (30.0, 35.0,  "Obesity – Class I",     "Moderate obesity, seek guidance",       BMI_COLORS["obese_1"],      "obese_1"),
    (35.0, 40.0,  "Obesity – Class II",    "Severe obesity, consult a specialist",  BMI_COLORS["obese_2"],      "obese_2"),
    (40.0, 100.0, "Obesity – Class III",   "Morbid obesity, medical care needed",   BMI_COLORS["obese_3"],      "obese_3"),
]

# Detailed health & wellness tips matching each category key
HEALTH_TIPS = {
    "severe_under": (
        "✔ Consult a doctor or registered dietitian immediately.\n"
        "✔ Focus on regular, small, nutrient-dense, high-calorie meals.\n"
        "✔ Avoid filling up on beverages before eating."
    ),
    "underweight": (
        "✔ Gradually increase calorie intake with wholesome food groups.\n"
        "✔ Incorporate healthy fats (nuts, seeds, avocados, olive oil).\n"
        "✔ Perform resistance training to build healthy muscle mass."
    ),
    "normal": (
        "✔ Maintain your current healthy lifestyle.\n"
        "✔ Eat a colorful, balanced diet with fiber, protein, and grains.\n"
        "✔ Keep up daily physical activity and prioritize quality sleep."
    ),
    "overweight": (
        "Try:\n"
        "✔ Walking daily, cycling, or doing recreational sports.\n"
        "✔ Portions management and limiting high-sugar processed foods.\n"
        "✔ Increasing fresh vegetables, lean proteins, and water intake."
    ),
    "obese_1": (
        "Try:\n"
        "✔ Starting light aerobic exercise (walking, swimming) 30 mins a day.\n"
        "✔ Structured meal planning and logging meals to monitor calories.\n"
        "✔ Partnering with a nutritionist or coach for supportive check-ins."
    ),
    "obese_2": (
        "Try:\n"
        "✔ Low-impact joint-friendly physical exercises.\n"
        "✔ Structured, dietitian-approved calorie-controlled meal plans.\n"
        "✔ Routine wellness checkups and tracking step count."
    ),
    "obese_3": (
        "Try:\n"
        "✔ Supervising physical activities under medical advice.\n"
        "✔ Setting up a medical evaluation for weight management plan.\n"
        "✔ Gaining routine behavioral and mental health counseling support."
    )
}

HISTORY_FILE = "bmi_history.json"


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
    for lo, hi, label, tip, color, key in BMI_RANGES:
        if lo <= bmi < hi:
            return label, tip, color, key
    last = BMI_RANGES[-1]
    return last[2], last[3], last[4], last[5]


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
        
        # Enable Resizing and set Constraints
        self.resizable(True, True)
        self.minsize(820, 720)
        self.configure(bg=BG)
        self._center_window(850, 740)

        # Store calculated results for clipboard & report export
        self.last_bmi = None
        self.last_category = None
        self.last_height_str = ""
        self.last_weight_str = ""
        self.last_tips_key = ""

        self._build_ui()
        self._refresh_history_table()

    def _center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Configure global window resizing grid weights
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Styled notebook tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD, foreground=TEXT_SEC, 
                        bordercolor=BORDER, padding=[18, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        # Treeview history log styles
        style.configure("Treeview",
                        background=CARD,
                        foreground=TEXT_PRI,
                        fieldbackground=CARD,
                        rowheight=30,
                        bordercolor=BORDER,
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])
        style.configure("Treeview.Heading",
                        background=INPUT_BG,
                        foreground=TEXT_SEC,
                        relief="flat",
                        font=("Segoe UI", 9, "bold"))

        notebook = ttk.Notebook(self, style="TNotebook")
        notebook.grid(row=0, column=0, sticky="nsew")

        # ── TAB 1: CALCULATOR ──
        calc_tab = tk.Frame(notebook, bg=BG)
        notebook.add(calc_tab, text="  Calculator  ")

        hdr = tk.Frame(calc_tab, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(20, 0))
        tk.Label(hdr, text="BMI Calculator",
                 bg=BG, fg=TEXT_PRI,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(hdr, text="Body Mass Index",
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 11)).pack(side="left", padx=(12, 0), pady=(6, 0))

        tk.Frame(calc_tab, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(12, 0))

        body = tk.Frame(calc_tab, bg=BG)
        body.pack(fill="both", expand=True, padx=30, pady=15)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

        tk.Label(calc_tab, text="BMI is a general screening tool and not a diagnostic measure.",
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8)).pack(pady=(0, 10))

        # ── TAB 2: HISTORY LOG ──
        hist_tab = tk.Frame(notebook, bg=BG)
        notebook.add(hist_tab, text="  Calculation History  ")

        hdr_h = tk.Frame(hist_tab, bg=BG)
        hdr_h.pack(fill="x", padx=30, pady=(20, 0))
        tk.Label(hdr_h, text="BMI History Log",
                 bg=BG, fg=TEXT_PRI,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Frame(hist_tab, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(12, 0))

        # Table frame inside history log
        tbl_frame = tk.Frame(hist_tab, bg=BG)
        tbl_frame.pack(fill="both", expand=True, padx=30, pady=15)
        tbl_frame.rowconfigure(0, weight=1)
        tbl_frame.columnconfigure(0, weight=1)

        columns = ("date", "height", "weight", "bmi", "category")
        self.history_table = ttk.Treeview(tbl_frame, columns=columns, show="headings", style="Treeview")
        
        self.history_table.heading("date", text="Date & Time")
        self.history_table.heading("height", text="Height Input")
        self.history_table.heading("weight", text="Weight Input")
        self.history_table.heading("bmi", text="BMI")
        self.history_table.heading("category", text="Classification")

        self.history_table.column("date", width=150, anchor="center")
        self.history_table.column("height", width=120, anchor="center")
        self.history_table.column("weight", width=120, anchor="center")
        self.history_table.column("bmi", width=90, anchor="center")
        self.history_table.column("category", width=220, anchor="w")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.history_table.yview)
        self.history_table.configure(yscrollcommand=vsb.set)
        
        self.history_table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        hist_btn_row = tk.Frame(hist_tab, bg=BG)
        hist_btn_row.pack(fill="x", padx=30, pady=(0, 25))
        self._btn(hist_btn_row, "  Clear History  ", self._clear_history,
                  bg=DANGER, fg="white").pack(side="left")

        # Global keyboard Return key binding to calculate BMI instantly
        self.bind("<Return>", lambda _: self._calculate())

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

        # Calculator Action Buttons (Row 1)
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill="x", pady=(18, 0))
        self._btn(btn_row, "  Calculate BMI  ", self._calculate,
                  bg=ACCENT, fg="white").pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn(btn_row, "  Reset  ", self._reset,
                  bg=CARD, fg=TEXT_SEC).pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Utility Action Buttons (Row 2)
        btn_row2 = tk.Frame(left, bg=BG)
        btn_row2.pack(fill="x", pady=(8, 0))
        
        self.copy_btn = self._btn(btn_row2, "  Copy Result  ", self._copy_result, bg=CARD, fg=TEXT_PRI)
        self.copy_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.copy_btn.config(state="disabled")

        self.pdf_btn = self._btn(btn_row2, "  Export PDF  ", self._export_pdf, bg=CARD, fg=TEXT_PRI)
        self.pdf_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.pdf_btn.config(state="disabled")

        # Info & Error Indicators
        self.info_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.info_var,
                 bg=BG, fg=TEXT_SEC,
                 font=("Segoe UI", 8, "italic"),
                 justify="left", anchor="w").pack(fill="x", pady=(8, 0))

        self.err_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self.err_var,
                 bg=BG, fg=DANGER,
                 font=("Segoe UI", 9),
                 justify="left", anchor="w").pack(fill="x")

        # Health Advice Display Card
        self._section(left, "HEALTH RECOMMENDATIONS")
        self.tips_card = self._card(left, pady=0)
        self.tips_text = tk.StringVar(value="Enter details and calculate to see health advice.")
        self.tips_label = tk.Label(self.tips_card, textvariable=self.tips_text,
                                   bg=CARD, fg=TEXT_PRI,
                                   font=("Segoe UI", 9),
                                   justify="left", anchor="w")
        self.tips_label.pack(fill="x", padx=14, pady=12)

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

        for lo, hi, label, tip, color, key in BMI_RANGES:
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
            self.err_var.set("Please enter a valid height.")
            return
        try:
            h_num = float(h_raw)
            if h_num <= 0:
                raise ValueError
        except ValueError:
            self.err_var.set("Please enter a valid height.")
            return

        # weight
        w_raw = self.w_entry.get().strip()
        if not w_raw or w_raw == self.w_entry._placeholder:
            self.err_var.set("Please enter a valid weight.")
            return
        try:
            w_num = float(w_raw)
            if w_num <= 0:
                raise ValueError
        except ValueError:
            self.err_var.set("Please enter a valid weight.")
            return

        # convert
        h_m  = height_to_meters(h_num, self.h_unit.get())
        w_kg = weight_to_kg(w_num, self.w_unit.get())

        if h_m < 0.5 or h_m > 3.0:
            self.err_var.set("Height value seems unrealistic. Check unit selection.")
            return
        if w_kg < 2 or w_kg > 700:
            self.err_var.set("Weight value seems unrealistic. Check unit selection.")
            return

        bmi = w_kg / (h_m ** 2)
        label, tip, color, key = get_bmi_category(bmi)

        # Store calculations for clipboard and pdf utilities
        self.last_bmi = bmi
        self.last_category = label
        self.last_height_str = f"{h_num} {self.h_unit.get()}"
        self.last_weight_str = f"{w_num} {self.w_unit.get()}"
        self.last_tips_key = key

        # Enable action buttons
        self.copy_btn.config(state="normal")
        self.pdf_btn.config(state="normal")

        # Update dynamic widgets
        self.info_var.set(
            f"Converted  ->  Height: {h_m:.4f} m  |  Weight: {w_kg:.2f} kg"
        )
        self.gauge.update_bmi(bmi, label, color)
        self._highlight_range(bmi)
        
        # Display dynamic tips list
        self.tips_text.set(HEALTH_TIPS.get(key, ""))

        # Save to local history log
        self._save_to_history(h_num, w_num, bmi, label)

    def _copy_result(self):
        if self.last_bmi is not None:
            formatted_text = f"BMI: {self.last_bmi:.1f}\nCategory: {self.last_category}"
            self.clipboard_clear()
            self.clipboard_append(formatted_text)
            self.update()
            
            # Temporary label swap for quick UX copy confirmation
            orig = self.copy_btn.cget("text")
            self.copy_btn.config(text="  Copied Result! ✓  ", fg=BMI_COLORS["normal"])
            self.after(1500, lambda: self.copy_btn.config(text=orig, fg=TEXT_PRI))

    def _export_pdf(self):
        if self.last_bmi is None:
            return

        name = simpledialog.askstring("Report Owner", "Enter name for the BMI Report:", parent=self)
        if name is None: # user cancelled
            return
        name = name.strip()
        if not name:
            name = "Valued User"

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"BMI_Report_{name.replace(' ', '_')}.pdf",
            title="Save BMI Assessment Report",
            parent=self
        )
        if not filename:
            return

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            doc = SimpleDocTemplate(filename, pagesize=letter,
                                    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()
            
            # Styles configuration
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=24,
                textColor=colors.HexColor("#6c63ff"),
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'DocSub',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.HexColor("#8b8fa8"),
                spaceAfter=25
            )
            section_heading = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=colors.HexColor("#1a1d27"),
                spaceBefore=15,
                spaceAfter=8,
                borderColor=colors.HexColor("#6c63ff"),
                borderPadding=4
            )
            body_style = ParagraphStyle(
                'DocBody',
                parent=styles['BodyText'],
                fontName='Helvetica',
                fontSize=10,
                textColor=colors.HexColor("#2a2d3a"),
                leading=15,
                spaceAfter=8
            )
            bold_label = ParagraphStyle(
                'BoldLabel',
                parent=body_style,
                fontName='Helvetica-Bold'
            )
            
            # PDF Header
            story.append(Paragraph("BMI ASSESSMENT REPORT", title_style))
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            story.append(Paragraph(f"Generated on {now_str} for {name}", subtitle_style))
            
            # Details Summary
            story.append(Paragraph("Assessment Summary", section_heading))
            summary_data = [
                [Paragraph("Patient Name:", bold_label), Paragraph(name, body_style)],
                [Paragraph("Measured Height:", bold_label), Paragraph(self.last_height_str, body_style)],
                [Paragraph("Measured Weight:", bold_label), Paragraph(self.last_weight_str, body_style)],
                [Paragraph("Calculated BMI:", bold_label), Paragraph(f"{self.last_bmi:.1f}", body_style)],
                [Paragraph("Classification:", bold_label), Paragraph(self.last_category, body_style)]
            ]
            t = Table(summary_data, colWidths=[150, 350])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#e2e8f0")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))
            
            # PDF Health Advice
            story.append(Paragraph("Health & Lifestyle Advice", section_heading))
            tips = HEALTH_TIPS.get(self.last_tips_key, "")
            for line in tips.split('\n'):
                if line.strip():
                    story.append(Paragraph(line.strip(), body_style))
            story.append(Spacer(1, 15))
            
            # Reference ranges table
            story.append(Paragraph("BMI Category Reference Ranges", section_heading))
            ref_data = [["BMI Range", "Classification", "General Recommendation"]]
            for lo, hi, label, tip, color_hex, _ in BMI_RANGES:
                range_str = f"{lo} - {hi}" if hi < 100 else f"{lo}+"
                ref_data.append([range_str, label, tip])
                
            ref_table = Table(ref_data, colWidths=[100, 150, 250])
            ref_table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1d27")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ])
            
            for i in range(len(ref_data)):
                for j in range(len(ref_data[i])):
                    is_header = (i == 0)
                    font_name = "Helvetica-Bold" if is_header else "Helvetica"
                    text_color = colors.white if is_header else colors.HexColor("#2a2d3a")
                    
                    if not is_header and ref_data[i][1] == self.last_category:
                        ref_table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f1f5f9"))
                        font_name = "Helvetica-Bold"
                        
                    ref_data[i][j] = Paragraph(
                        ref_data[i][j],
                        ParagraphStyle('Cell', parent=styles['Normal'], fontName=font_name, textColor=text_color, fontSize=9)
                    )
            
            ref_table.setStyle(ref_table_style)
            story.append(ref_table)
            
            # Disclaimer
            story.append(Spacer(1, 30))
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=8,
                textColor=colors.HexColor("#8b8fa8"),
                alignment=1
            )
            story.append(Paragraph("Disclaimer: BMI is a general screening tool and not a diagnostic measure of health.", disclaimer_style))
            story.append(Paragraph("Please consult with a qualified medical professional for personalized health advice.", disclaimer_style))
            
            doc.build(story)
            messagebox.showinfo("Success", f"PDF report successfully exported to:\n{os.path.basename(filename)}", parent=self)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF:\n{str(e)}", parent=self)

    # ── history logger operations ──────────────────────────────────────────────
    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self, history):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error saving history log: {e}")

    def _save_to_history(self, h_val, w_val, bmi, label):
        history = self._load_history()
        
        record = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "height": f"{h_val} {self.h_unit.get()}",
            "weight": f"{w_val} {self.w_unit.get()}",
            "bmi": round(bmi, 1),
            "category": label
        }
        
        history.insert(0, record)
        if len(history) > 100:
            history = history[:100]
            
        self._save_history(history)
        self._refresh_history_table()

    def _refresh_history_table(self):
        for item in self.history_table.get_children():
            self.history_table.delete(item)
            
        history = self._load_history()
        for rec in history:
            self.history_table.insert("", "end", values=(
                rec.get("date", ""),
                rec.get("height", ""),
                rec.get("weight", ""),
                rec.get("bmi", ""),
                rec.get("category", "")
            ))

    def _clear_history(self):
        if not self._load_history():
            messagebox.showinfo("History", "No history records to clear.", parent=self)
            return
            
        if messagebox.askyesno("Clear History", "Are you sure you want to permanently clear all history records?", parent=self):
            self._save_history([])
            self._refresh_history_table()

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

        # Reset selection states
        self.last_bmi = None
        self.last_category = None
        self.last_height_str = ""
        self.last_weight_str = ""
        self.last_tips_key = ""
        
        self.copy_btn.config(state="disabled")
        self.pdf_btn.config(state="disabled")
        self.tips_text.set("Enter details and calculate to see health advice.")

        for _, _, row_f, indicator, lbl_t, lbl_s, color in self.range_rows:
            row_f.config(bg=CARD)
            indicator.config(width=4)
            lbl_t.config(bg=CARD, fg=TEXT_PRI)
            lbl_s.config(bg=CARD, fg=TEXT_SEC)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
