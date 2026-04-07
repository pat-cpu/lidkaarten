# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True, convert=True)

BASE = Path(__file__).resolve().parent

from config import EXCEL_PATH

# ----------------------------------------------------
#  MAP-CHECKER
# ----------------------------------------------------
def ensure_folders():
    required = [
        BASE / "gegenereerde_barcodes",
        BASE / "qr_png",
    ]

    print("\n🔍 Mappen controleren...")
    for folder in required:
        if not folder.exists():
            print(f"⚠️  Map ontbreekt, wordt aangemaakt: {folder}")
            folder.mkdir(parents=True, exist_ok=True)
            print("   ✔ Aangemaakt.")
        else:
            print(f"✔ Map ok: {folder}")
    print("----------------------------------------------------\n")


# ----------------------------------------------------
#  EXCEL LOCK DETECTIE
# ----------------------------------------------------
def excel_is_open():
    try:
        with EXCEL_PATH.open("r+b"):
            return False
    except PermissionError:
        return True


def wait_for_excel():
    print("\n❌ leden.xlsx staat OPEN in Excel.")
    print("👉 Sluit Excel volledig en druk ENTER om opnieuw te proberen.\n")
    input()


def safe_run(script):
    while True:
        if excel_is_open():
            wait_for_excel()
        else:
            break

    subprocess.run([sys.executable, str(BASE / script)])


# ----------------------------------------------------
#  MENU
# ----------------------------------------------------
def main():

 
    ensure_folders()

    while True:
        print(Fore.LIGHTYELLOW_EX + Style.BRIGHT + """
========================================================
             THE WHISKIES – BARCODE MENU
========================================================
""" + Style.RESET_ALL)

        print("""
1) Nieuw lid toevoegen
2) Barcodekaartjes printen
3) QR codes genereren (1–2–3)
4) Map barcodes openen
5) Map QR openen
0) Terug naar hoofdmenu

--------------------------------------------------------
Maak uw keuze: """)

        keuze = input(Fore.CYAN + "> " + Style.RESET_ALL).strip()

        if keuze == "1":
            safe_run("nieuw_lid.py")
        elif keuze == "2":
            safe_run("print_barcodes.py")
        elif keuze == "3":
            safe_run("QR_Code123.py")
        elif keuze == "4":
            os.startfile(BASE / "gegenereerde_barcodes")
        elif keuze == "5":
            os.startfile(BASE / "qr_png")
        elif keuze == "0":
            break
        else:
            print(Fore.RED + "❌ Ongeldige keuze.\n")


if __name__ == "__main__":
    main()
