<<<<<<< HEAD
from pathlib import Path

# =========================================================
# BASISPAD
# =========================================================

# Map waar dit config.py bestand staat (= LidkaartenPython)
BASE_DIR = Path(__file__).resolve().parent

# Excel-bestand staat standaard in dezelfde map
EXCEL_PATH = BASE_DIR / "data" / "leden.xlsx"

# =========================================================
# EXCEL INSTELLINGEN
# =========================================================

SHEET = "Leden"

# Kolomnamen zoals jij ze gebruikt in Excel
CODE_COL = "Code"
NAME_COL = "Naam"
QR_COL   = "QR"      # optioneel, mag leeg blijven in Excel

# =========================================================
# PRINT LAYOUT (ENIGE BRON VAN WAARHEID)
# =========================================================

# Raster
PRINT_COLS = 2
PRINT_ROWS = 5

# Marges (mm)
PAGE_MARGIN_MM = 6.0   # boven & onder

# Tussenruimtes (mm)
GAP_X_MM = 0.0         # tussen kolommen
GAP_Y_MM = 0.0         # tussen rijen

# Nooit groter schalen dan origineel kaartformaat
SCALE_MAX_1 = True

# Debug kaders rond kaartvakken (handig bij testen)
=======
from pathlib import Path

# =========================================================
# BASISPAD
# =========================================================

# Map waar dit config.py bestand staat (= LidkaartenPython)
BASE_DIR = Path(__file__).resolve().parent

# Excel-bestand staat standaard in dezelfde map
EXCEL_PATH = BASE_DIR / "data" / "leden.xlsx"

# =========================================================
# EXCEL INSTELLINGEN
# =========================================================

SHEET = "Leden"

# Kolomnamen zoals jij ze gebruikt in Excel
CODE_COL = "Code"
NAME_COL = "Naam"
QR_COL   = "QR"      # optioneel, mag leeg blijven in Excel

# =========================================================
# PRINT LAYOUT (ENIGE BRON VAN WAARHEID)
# =========================================================

# Raster
PRINT_COLS = 2
PRINT_ROWS = 5

# Marges (mm)
PAGE_MARGIN_MM = 6.0   # boven & onder

# Tussenruimtes (mm)
GAP_X_MM = 0.0         # tussen kolommen
GAP_Y_MM = 0.0         # tussen rijen

# Nooit groter schalen dan origineel kaartformaat
SCALE_MAX_1 = True

# Debug kaders rond kaartvakken (handig bij testen)
>>>>>>> 14b142486c61fce67c54e7dc87a5c29fdb29e6d5
DEBUG_FRAMES = False