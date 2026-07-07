# BMI Calculator

A minimal, dark-themed **Body Mass Index Calculator** built with Python and Tkinter — no third-party dependencies required.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

---

## Features

- **Multi-unit height input** — Meter, Centimeter, Millimeter, Feet, Inches
- **Multi-unit weight input** — Kilogram, Pound (lbs), Gram
- **Auto unit conversion** — All values internally converted to SI units (meters / kg)
- **Animated semi-circle gauge** — Colour-coded needle sweeps to your BMI result
- **BMI range reference table** — Active category highlights in real time
- **Input validation** — Catches empty, non-numeric, and unrealistic values
- **Reset button** — Clears all inputs and returns gauge to default state
- **No external libraries** — Uses only Python standard library (tkinter)

---

## BMI Categories

| BMI Range | Category | Advice |
|-----------|----------|--------|
| < 16 | Severely Underweight | Consult a doctor immediately |
| 16 – 18.5 | Underweight | You need to gain weight |
| 18.5 – 25 | Normal / Perfect | Great! Keep it up |
| 25 – 30 | Overweight | Needs improvement – diet & exercise |
| 30 – 35 | Obesity – Class I | Moderate obesity, seek guidance |
| 35 – 40 | Obesity – Class II | Severe obesity, consult a specialist |
| 40 + | Obesity – Class III | Morbid obesity, medical care needed |

---

## Requirements

- Python **3.8** or higher
- `tkinter` (included with standard Python on Windows; see below for Linux/macOS)

### Linux (if tkinter is missing)
```bash
sudo apt-get install python3-tk        # Debian / Ubuntu
sudo dnf install python3-tkinter       # Fedora
```

### macOS
```bash
brew install python-tk                 # via Homebrew
```

---

## Installation & Running

```bash
# 1. Clone the repository
git clone https://github.com/your-username/bmi-calculator.git
cd bmi-calculator

# 2. Run the app (no pip install needed)
python bmi_calculator.py
```

---

## Project Structure

```
BMI Calculator/
├── bmi_calculator.py   # Main application (single file)
├── README.md           # Project documentation
└── .gitignore          # Git ignore rules
```

---

## How to Use

1. **Select a height unit** from the dropdown (e.g. Centimeter)
2. **Enter your height value** in the input field (e.g. `170`)
3. **Select a weight unit** from the dropdown (e.g. Kilogram)
4. **Enter your weight value** in the input field (e.g. `65`)
5. Press **Calculate BMI** or hit `Enter`
6. The gauge needle animates to your result and your BMI category highlights in the range table
7. Converted values are displayed below the buttons for transparency

---

## BMI Formula

```
BMI = weight (kg) / height² (m²)
```

> **Disclaimer:** BMI is a general screening tool and is not a diagnostic measure.
> Consult a qualified healthcare professional for personalised health advice.

---

## License

This project is licensed under the [MIT License](LICENSE).
