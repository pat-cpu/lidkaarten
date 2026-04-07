from pathlib import Path

# Map waar dit config.py bestand staat (= LidkaartenPython)
BASE_DIR = Path(__file__).resolve().parent

# Excel-bestand staat in dezelfde map als de scripts
EXCEL_PATH = BASE_DIR / "leden.xlsx"

SHEET = "Leden"
CODE_COL = "Code"
NAME_COL = "Naam"