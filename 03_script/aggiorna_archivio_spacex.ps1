# Importazione autonoma e in sola lettura. Nessuna modifica ai gestori Python.
param([string]$NodeExe = '', [string]$DataImportazione = (Get-Date -Format 'yyyy-MM-dd'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$taskRoot = Split-Path $PSScriptRoot -Parent
function Read-ArchiveEntry($zip, $name) {
    $entry = $zip.GetEntry($name)
    if ($null -eq $entry) { return $null }
    $reader = [IO.StreamReader]::new($entry.Open())
    try { return $reader.ReadToEnd() } finally { $reader.Dispose() }
}
function Read-Sheet($relativePath, $sheetName, $headerRow, $dateColumns) {
    $fullPath = Join-Path $taskRoot $relativePath
    $zip = [IO.Compression.ZipFile]::OpenRead($fullPath)
    try {
        [xml]$workbook = Read-ArchiveEntry $zip 'xl/workbook.xml'
        if ($workbook.workbook.workbookPr.date1904 -eq '1') { throw 'Date Excel 1904 non supportate: importazione fermata.' }
        [xml]$rels = Read-ArchiveEntry $zip 'xl/_rels/workbook.xml.rels'
        $sheet = @($workbook.workbook.sheets.sheet) | Where-Object { $_.name -eq $sheetName }
        if ($null -eq $sheet) { throw "Foglio mancante: $sheetName" }
        $relId = $sheet.GetAttribute('id', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')
        $rel = @($rels.Relationships.Relationship) | Where-Object { $_.Id -eq $relId }
        $target = [string]$rel.Target
        $sheetPath = if ($target.StartsWith('/')) { $target.TrimStart('/') } else { 'xl/' + $target }
        [xml]$xml = Read-ArchiveEntry $zip $sheetPath
        $strings = @()
        $shared = Read-ArchiveEntry $zip 'xl/sharedStrings.xml'
        if ($shared) {
            [xml]$ss = $shared
            $strings = @($ss.sst.si | ForEach-Object { ($_.SelectNodes('.//*[local-name()="t"]') | ForEach-Object { $_.InnerText }) -join '' })
        }
        $headers = @{}
        $result = [Collections.Generic.List[object]]::new()
        foreach ($row in $xml.worksheet.sheetData.row) {
            if ([int]$row.r -lt $headerRow) { continue }
            $record = [ordered]@{ source_row = [int]$row.r }
            foreach ($cell in $row.c) {
                $col = ([string]$cell.r) -replace '\d', ''
                $val = $null
                if ($cell.t -eq 's') { $val = $strings[[int]$cell.v] }
                elseif ($cell.t -eq 'inlineStr') { $val = ($cell.SelectNodes('.//*[local-name()="t"]') | ForEach-Object { $_.InnerText }) -join '' }
                elseif ($cell.t -eq 'str') { $val = [string]$cell.v }
                elseif ($cell.t -eq 'e') { throw "Errore Excel $relativePath/$sheetName/$($cell.r): $($cell.v)" }
                elseif ($null -ne $cell.v -and [string]$cell.v -ne '') {
                    $val = [double]::Parse([string]$cell.v, [Globalization.CultureInfo]::InvariantCulture)
                }
                if ([int]$row.r -eq $headerRow) { if ($val) { $headers[$col] = [string]$val }; continue }
                if ($headers.ContainsKey($col)) {
                    $key = $headers[$col]
                    if ($null -ne $val -and $dateColumns -contains $key -and $val -is [double]) { $val = [DateTime]::FromOADate($val).ToString('yyyy-MM-dd') }
                    if ($null -ne $val -and $key -eq 'ora_utc' -and $val -is [double]) { $val = [DateTime]::FromOADate($val).ToString('HH:mm:ss') }
                    $record[$key] = $val
                }
            }
            if ([int]$row.r -gt $headerRow -and ($record['id_lancio'] -or $record['Flight'] -or $record['id_sito'])) { $result.Add($record) }
        }
        return ,$result.ToArray()
    } finally { $zip.Dispose() }
}
$sources = @(
    '01_workbook/lanci_spacex.xlsx', '01_workbook/sviluppo_starship.xlsx',
    'monografie/starship/voli.json', 'sezioni/storico-lanci.html'
)
$hashes = [ordered]@{}
foreach ($source in $sources) { $hashes[$source] = (Get-FileHash -LiteralPath (Join-Path $taskRoot $source) -Algorithm SHA256).Hash.ToLowerInvariant() }
$payload = [ordered]@{
    imported = $DataImportazione
    hashes = $hashes
    launches = Read-Sheet '01_workbook/lanci_spacex.xlsx' 'elenco' 1 @('data','data_evento','anno_mese')
    recoveries = Read-Sheet '01_workbook/lanci_spacex.xlsx' 'recuperi_veicoli' 1 @('data_recupero')
    sites = Read-Sheet '01_workbook/lanci_spacex.xlsx' 'siti' 1 @()
    tests = Read-Sheet '01_workbook/sviluppo_starship.xlsx' 'Voli integrati' 4 @()
    monograph = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $taskRoot 'monografie/starship/voli.json') | ConvertFrom-Json
    legacy_html = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $taskRoot 'sezioni/storico-lanci.html')
}
foreach ($source in $sources) {
    if ((Get-FileHash -LiteralPath (Join-Path $taskRoot $source) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $hashes[$source]) { throw "Fonte cambiata durante la lettura: $source" }
}
if (-not $NodeExe) {
    $command = Get-Command node -ErrorAction SilentlyContinue
    if ($command) { $NodeExe = $command.Source }
    else { $NodeExe = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' }
}
if (-not (Test-Path -LiteralPath $NodeExe)) { throw 'Node non disponibile. Specificare -NodeExe con il percorso di Node.' }
$scratch = Join-Path $taskRoot '99_temporanei/archivio110'
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
$jsonPath = Join-Path $scratch 'fonti.json'
[IO.File]::WriteAllText($jsonPath, ($payload | ConvertTo-Json -Depth 30), [Text.UTF8Encoding]::new($false))
& $NodeExe (Join-Path $PSScriptRoot 'costruisci_archivio_spacex.mjs') $jsonPath
if ($LASTEXITCODE -ne 0) { throw 'Costruzione archivio interrotta: leggere gli errori.' }
