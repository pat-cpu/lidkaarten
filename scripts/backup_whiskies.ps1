$datum = Get-Date -Format "yyyy-MM-dd_HH-mm"

$project = "C:\Users\patri\Documenten\THE WHISKIES TEST\Test_lidkaartenPython"
$temp = Join-Path $env:TEMP "Test_lidkaartenPython_backup_temp"
$doel1 ="C:\Users\patri\Documenten\THE WHISKIES TEST\Test_lidkaartenPython\_backup\Test_lidkaartenPython_backup_$datum.zip"
$doel2 = "\\192.168.0.122\archief_ssd\THE WHISKIES\Test_lidkaartenPython_backup_$datum.zip"

Write-Host ""
Write-Host "Backup maken van belangrijke programmabestanden..."
Write-Host ""

# tijdelijke map leegmaken
if (Test-Path $temp) {
    Remove-Item $temp -Recurse -Force
}
New-Item -ItemType Directory -Path $temp | Out-Null

# hoofdmap: alleen belangrijke bestandstypes
Get-ChildItem $project -File | Where-Object {
    $_.Extension -in ".py", ".bat", ".txt", ".md"
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $temp -Force
}

# belangrijke mappen kopiëren
$belangrijkeMappen = @("data", "assets", "scripts")

foreach ($map in $belangrijkeMappen) {
    $bronMap = Join-Path $project $map
    if (Test-Path $bronMap) {
        Copy-Item $bronMap -Destination $temp -Recurse -Force
    }
}

# oude zip met dezelfde naam verwijderen indien nodig
if (Test-Path $doel1) { Remove-Item $doel1 -Force }
if (Test-Path $doel2) { Remove-Item $doel2 -Force }

# lokale zip maken
try {
    Compress-Archive -Path "$temp\*" -DestinationPath $doel1 -Force -ErrorAction Stop
    Write-Host "Lokale backup OK:" $doel1
} catch {
    Write-Host "FOUT bij lokale backup:" $_.Exception.Message
}

# netwerk zip maken
if (Test-Path "\\192.168.0.122\archief_ssd\THE WHISKIES") {
    try {
        Compress-Archive -Path "$temp\*" -DestinationPath $doel2 -Force -ErrorAction Stop
        Write-Host "Netwerk backup OK:" $doel2
    } catch {
        Write-Host "FOUT bij netwerk backup:" $_.Exception.Message
    }
} else {
    Write-Host "NAS niet bereikbaar, netwerkbackup overgeslagen."
}

# tijdelijke map opruimen
if (Test-Path $temp) {
    Remove-Item $temp -Recurse -Force
}

Write-Host ""
Write-Host "Backup klaar."