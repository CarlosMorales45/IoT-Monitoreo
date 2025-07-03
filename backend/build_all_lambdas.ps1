$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$lambdaSrc = Join-Path $scriptPath "lambdas"
$lambdaBuild = Join-Path $scriptPath "lambda_build"

if (!(Test-Path $lambdaBuild)) {
    New-Item -Path $lambdaBuild -ItemType Directory | Out-Null
}

Get-ChildItem -Path "$lambdaBuild\*.zip" -ErrorAction SilentlyContinue | Remove-Item -Force

Get-ChildItem $lambdaSrc -Directory | ForEach-Object {
    $lambdaName = $_.Name
    $lambdaPath = Join-Path $lambdaSrc $lambdaName
    Write-Host "Empaquetando $lambdaName..."

    # Carpeta temporal para empaquetar TODO en la raíz del ZIP
    $tempPath = Join-Path $lambdaPath "temp_package"
    if (Test-Path $tempPath) { Remove-Item $tempPath -Recurse -Force }
    New-Item -Path $tempPath -ItemType Directory | Out-Null

    $reqFile = Join-Path $lambdaPath "requirements.txt"
    if (Test-Path $reqFile) {
        python -m pip install -r $reqFile -t $tempPath
    }
    Copy-Item -Path (Join-Path $lambdaPath "main.py") -Destination $tempPath

    # Puedes copiar otros archivos si tu lambda los necesita (ej: utils.py, config.json, etc.)
    # Copy-Item -Path (Join-Path $lambdaPath "*.py") -Destination $tempPath

    # Aquí aseguramos que el nombre final sea exactamente igual al nombre de la carpeta
    $zipPath = Join-Path $lambdaBuild ("{0}.zip" -f $lambdaName)
    if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
    Add-Type -AssemblyName 'System.IO.Compression.FileSystem'
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempPath, $zipPath)

    Remove-Item $tempPath -Recurse -Force
}
Write-Host "¡Listo! Zips guardados en $lambdaBuild\"
