<#
.SYNOPSIS
    Install ATLAS-8 native PDP-8 MicroPython emulator onto an RP2040 Pico.
.DESCRIPTION
    Defaults to Dashboard mode for the dedicated PC and Chrome front panel.
    Files remain on PC: dashboard/, pc_dashboard_server.py, tests/, docs/, PDFs.
    Uses official mpremote utility over Pico USB CDC; backs up existing Pico
    files, verifies transfers byte-for-byte, and installs main.py LAST.
.EXAMPLE
    .\INSTALL_PICO.ps1 -Port COM7
.EXAMPLE
    .\INSTALL_PICO.ps1 -Mode Monitor -Port COM7
.EXAMPLE
    .\INSTALL_PICO.ps1 -Mode Dashboard -WhatIf
.NOTES
    Requires an RP2040 with MicroPython already flashed and Python 3 with
    mpremote installed. Not yet verified on an actual Pico; exercise caution.
#>
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Low')]
param(
    [ValidateSet('Dashboard','Monitor')][string]$Mode = 'Dashboard',
    [ValidateNotNullOrEmpty()][string]$Port = 'auto',
    [string]$BackupDirectory = '',
    [switch]$SkipBackup,
    [switch]$NoReset
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Get-PythonInvocation {
    if (Get-Command py -ErrorAction SilentlyContinue) { return @{ exe='py'; prefix=@('-3') } }
    if (Get-Command python -ErrorAction SilentlyContinue) { return @{ exe='python'; prefix=@() } }
    throw 'Python 3 was not found. Install Python 3 and run this installer again.'
}

$pythonInfo = Get-PythonInvocation
$pythonExe = $pythonInfo.exe
$pythonPrefix = @($pythonInfo.prefix)

function Invoke-Python([string[]]$Arguments, [switch]$AllowFailure) {
    $allArgs = @($pythonPrefix) + @($Arguments)
    # Explicitly capture stdout/stderr without converting native stderr to a
    # terminating PowerShell error (works on Windows PowerShell 5.1 and PS7).
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $pythonExe @allArgs 2>&1 | Out-String
        $exitCode = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $oldPreference }
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw ("Python command failed (exit $exitCode): python $($Arguments -join ' ')`n$output")
    }
    return @{ Code=$exitCode; Text=[string]$output }
}

function Invoke-Mpremote([string[]]$Arguments, [switch]$AllowFailure) {
    $mpArgs = @('-m','mpremote','connect',$Port) + $Arguments
    return Invoke-Python -Arguments $mpArgs -AllowFailure:$AllowFailure
}

function File-SHA256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

$runtimeFiles = @('pdp8.py','programs.py','tape.py','monitor.py','bootstrap.py','dashboard_bridge.py')
$entrySource = if ($Mode -eq 'Dashboard') { 'main_dashboard.py' } else { 'main.py' }
$remoteFiles = @($runtimeFiles) + @('main.py')
foreach ($name in @($runtimeFiles) + @($entrySource)) {
    $local = Join-Path $root $name
    if (-not (Test-Path -LiteralPath $local -PathType Leaf)) {
        throw "Missing '$name'. Run this script from an extracted full ATLAS-8 checkout."
    }
}

Write-Host ''
Write-Host 'ATLAS-8 / PDP-8 Pico installer' -ForegroundColor Cyan
Write-Host "Mode: $Mode | Pico connection: $Port"
Write-Host "Repository source: $root"
Write-Host 'IMPORTANT: Close Thonny, mpremote REPL and the PC dashboard LIVE PICO connection.'
Write-Host ''
Write-Host 'MicroPython startup selection:'
if ($Mode -eq 'Dashboard') {
    Write-Host '  main_dashboard.py  -->  Pico:/main.py  (JSON/USB bridge for Chrome)' -ForegroundColor Green
    Write-Host '  Do NOT install repository main.py in this mode.'
} else {
    Write-Host '  repository main.py --> Pico:/main.py (standalone text monitor)' -ForegroundColor Yellow
    Write-Host '  Chrome LIVE PICO mode will NOT work with this entry point.'
}

if ($WhatIfPreference) {
    Write-Host ''
    Write-Host 'DRY RUN: No Pico was accessed and no files were changed.'
    foreach ($name in $runtimeFiles) { Write-Host "  Would copy $name -> :$name" }
    Write-Host "  Would copy $entrySource -> :main.py LAST"
    return
}

$test = Invoke-Python -Arguments @('-m','mpremote','--help') -AllowFailure
if ($test.Code -ne 0) {
    throw "mpremote is not installed for this Python. Run: $pythonExe $($pythonPrefix -join ' ') -m pip install mpremote"
}

# Back up each existing destination, including main.py, before writing anything.
# A missing destination is normal on a clean Pico; any other error is fatal.
if (-not $SkipBackup) {
    if ([string]::IsNullOrWhiteSpace($BackupDirectory)) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $BackupDirectory = Join-Path $root ('pico-backups\' + $stamp)
    }
    New-Item -ItemType Directory -Force -Path $BackupDirectory | Out-Null
    Write-Host "Backing up existing Pico files to $BackupDirectory" -ForegroundColor Cyan
    foreach ($name in $remoteFiles) {
        $destination = Join-Path $BackupDirectory $name
        $result = Invoke-Mpremote -Arguments @('fs','cp',(':'+$name),$destination) -AllowFailure
        if ($result.Code -eq 0) {
            Write-Host "  Backup: $name"
        } elseif ($result.Text -match '(?i)ENOENT|Errno\s*2|No such file|not found|does not exist') {
            Write-Host "  New file: $name"
        } else {
            throw "Could not safely back up Pico:$name. Nothing has been uploaded yet.`n$($result.Text)"
        }
    }
} else {
    Write-Warning 'Backups disabled by -SkipBackup. Existing Pico files may be overwritten.'
}

# Preserve startup behavior until all dependencies are fully installed.
$copySequence = @()
foreach ($name in $runtimeFiles) {
    $copySequence += @{ source=$name; target=$name }
}
$copySequence += @{ source=$entrySource; target='main.py' }

$verified = 0
foreach ($entry in $copySequence) {
    $src = Join-Path $root $entry.source
    $remote = ':' + $entry.target
    Write-Host "Copying $($entry.source) -> Pico:$($entry.target)" -ForegroundColor Cyan
    Invoke-Mpremote -Arguments @('fs','cp',$src,$remote) | Out-Null
    $tmp = [System.IO.Path]::GetTempFileName()
    try {
        Invoke-Mpremote -Arguments @('fs','cp',$remote,$tmp) | Out-Null
        if ((File-SHA256 $src) -ne (File-SHA256 $tmp)) {
            throw "VERIFY FAILED for Pico:$($entry.target). The transferred bytes differ."
        }
    } finally {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
    }
    $verified++
    Write-Host "  Verified SHA-256: $($entry.target)" -ForegroundColor Green
}

Write-Host ''
Write-Host "SUCCESS: $verified files copied and verified, including the correct main.py." -ForegroundColor Green
if (-not $NoReset) {
    Write-Host 'Rebooting the Pico...'
    $result = Invoke-Mpremote -Arguments @('reset') -AllowFailure
    if ($result.Code -ne 0) {
        Write-Warning "Files verified, but automated reset failed. Press the Pico RESET button or reconnect USB. $($result.Text)"
    }
}
if ($Mode -eq 'Dashboard') {
    Write-Host 'Next: Release the USB port, start START_DASHBOARD_WINDOWS.bat on the PC,'
    Write-Host 'select LIVE PICO in Chrome, and enter the Pico COM port.'
} else {
    Write-Host 'Next: Open mpremote REPL for the text-based PDP-8 monitor.'
}
Write-Host 'Recovery: Close the dashboard, interrupt the Pico with Ctrl-C, then use'
Write-Host 'mpremote to remove or replace Pico:/main.py. Saved backups remain on your PC.'
