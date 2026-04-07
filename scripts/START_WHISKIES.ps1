# scripts\START_WHISKIES.ps1
# Veilig startmenu (geen speciale tekens) + kleuren

$ErrorActionPreference = "SilentlyContinue"

# Projectroot = 1 map boven scripts
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

function Get-PythonExe {
    $venvPy = Join-Path $root ".venv\Scripts\python.exe"
    if (Test-Path $venvPy) { return $venvPy }
    return "python"
}

$version = "1.0"

function Show-Header {

    $version = "1.0"

    $season = Get-SeasonText
    $members = Get-MemberCount
    $backup = Get-LatestBackup

    Clear-Host
    Write-Host ""

    Write-Host " __        ___     _     _     _           " -ForegroundColor Yellow
    Write-Host " \ \      / / |__ (_)___| | __(_) ___  ___ " -ForegroundColor Yellow
    Write-Host "  \ \ /\ / /| '_ \| / __| |/ /| |/ _ \/ __|" -ForegroundColor Yellow
    Write-Host "   \ V  V / | | | | \__ \   < | |  __/\__ \" -ForegroundColor Yellow
    Write-Host "    \_/\_/  |_| |_|_|___/_|\_\|_|\___||___/" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "=================================================" -ForegroundColor DarkCyan
    Write-Host "        THE WHISKIES LIDKAARTENSYSTEEM" -ForegroundColor Cyan
    Write-Host "                versie $version" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor DarkCyan
    Write-Host ""
    Write-Host " $season   |   $members" -ForegroundColor Gray
    Write-Host " $backup" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "   Lidkaarten | Barcodes | Preview | Backup" -ForegroundColor Gray
    Write-Host ""
}


function Pause-Back {
    Write-Host ""
    Write-Host "Druk op een toets om terug te keren naar het menu..." -ForegroundColor Yellow
    [void][System.Console]::ReadKey($true)
}

function Run-Py($file) {
    if (-not (Test-Path $file)) {
        Write-Host ("NIET GEVONDEN: " + $file) -ForegroundColor Red
        Start-Sleep -Milliseconds 900
        return
    }
    Write-Host ""
    Write-Host ("START: " + $file) -ForegroundColor Green
    Write-Host "---------------------------------------------" -ForegroundColor DarkGray
    python $file
    Write-Host "---------------------------------------------" -ForegroundColor DarkGray
    Pause-Back
}

function Run-Backup {
    $backup = Join-Path $root "scripts\backup_whiskies.ps1"
    if (-not (Test-Path $backup)) {
        Write-Host "NIET GEVONDEN: scripts\backup_whiskies.ps1" -ForegroundColor Red
        Start-Sleep -Milliseconds 900
        return
    }
    Write-Host ""
    Write-Host "BACKUP STARTEN..." -ForegroundColor Green
    Write-Host "---------------------------------------------" -ForegroundColor DarkGray
    powershell -NoProfile -ExecutionPolicy Bypass -File $backup
    Write-Host "---------------------------------------------" -ForegroundColor DarkGray
    Pause-Back
}

function Get-SeasonText {
    $file = Join-Path $root "Lidkaart_2026_2027.py"
    if (-not (Test-Path $file)) { return "Seizoen: onbekend" }

    try {
        $txt = Get-Content $file -Raw
        if ($txt -match "SEASON_START_YEAR\s*=\s*(\d{4})") {
            $y = [int]$Matches[1]
            return "Seizoen: $y-$($y+1)"
        }
    } catch {}
    return "Seizoen: onbekend"
}

function Get-MemberCount {
    $file = Join-Path $root "leden.xlsx"
    if (-not (Test-Path $file)) { return "Leden: ? (leden.xlsx ontbreekt)" }

    $pyexe = Get-PythonExe

    try {
        $code = @'
import sys
import pandas as pd
df = pd.read_excel(sys.argv[1])
print(len(df.index))
'@
        $count = & $pyexe -c $code $file 2>$null
        if ($count -match "^\d+$") {
            return "Leden: $count"
        }
    } catch {}
    return "Leden: ?"
}f

function Get-LatestBackup {
    # Zoek in projectroot én in de map erboven (waar jouw zips nu staan)
    $parent = (Resolve-Path (Join-Path $root "..")).Path
    $patterns = @("*backup*.zip", "*Backup*.zip", "*.zip")

    $best = $null

    foreach ($p in @($root, $parent)) {
        foreach ($pat in $patterns) {
            $cand = Get-ChildItem -Path $p -Filter $pat -File -ErrorAction SilentlyContinue |
                    Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($cand -and (-not $best -or $cand.LastWriteTime -gt $best.LastWriteTime)) {
                $best = $cand
            }
        }
    }

    # NAS erbij (optioneel)
    $nasPath = "\\192.168.0.122\archief_ssd"
    if (Test-Path $nasPath) {
        foreach ($pat in $patterns) {
            $cand = Get-ChildItem -Path $nasPath -Filter $pat -File -ErrorAction SilentlyContinue |
                    Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($cand -and (-not $best -or $cand.LastWriteTime -gt $best.LastWriteTime)) {
                $best = $cand
            }
        }
    }

    if ($best) {
        return "Laatste backup: " + $best.LastWriteTime.ToString("yyyy-MM-dd HH:mm") + " (" + $best.DirectoryName + ")"
    }
    return "Laatste backup: geen gevonden"
}



while ($true) {
    Show-Header

    Write-Host " [1] Lidkaarten menu" -ForegroundColor White
    # Write-Host " [6] Barcodes menu" -ForegroundColor White
    Write-Host " [2] Live preview kaart" -ForegroundColor White
    Write-Host " [3] Backup maken" -ForegroundColor White

    # Write-Host " [5] Output map openen" -ForegroundColor White
    Write-Host " [4] Afsluiten" -ForegroundColor White
    Write-Host ""

    $k = Read-Host "Maak je keuze (1-6)"

    switch ($k) {
        "1" { Run-Py "menu_lidkaarten.py" }
        # "6" { Run-Py "menu_barcodes.py" }
        "2" { Run-Py "preview_card.py" }
        "3" { Run-Backup }
        # "5" { Start-Process (Join-Path $root "output"); Pause-Back }
        "4" { break }
        default {
            Write-Host "Ongeldige keuze." -ForegroundColor Red
            Start-Sleep -Milliseconds 900
        }
    }
}