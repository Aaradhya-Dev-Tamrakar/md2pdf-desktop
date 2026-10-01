<#
.SYNOPSIS
    Registers or unregisters md2pdf Studio context menu actions in Windows Explorer.
.DESCRIPTION
    Adds "Convert to PDF (md2pdf)" and the "md2pdf Studio ▾" submenu directly
    into Windows Explorer's right-click context menu for .md and .markdown files.
    Writes strictly to HKCU:\Software\Classes, requiring no administrator elevation.
.PARAMETER Unregister
    Removes the context menu entries.
.PARAMETER Register
    Installs the context menu entries (default).
#>

[CmdletBinding(DefaultParameterSetName = "Register")]
param(
    [Parameter(ParameterSetName = "Register")]
    [switch]$Register = $true,

    [Parameter(ParameterSetName = "Unregister")]
    [switch]$Unregister,

    [Parameter()]
    [string]$PythonPath
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }

$directConvert = Join-Path $scriptDir "direct_convert.py"
$studioApp = Join-Path $scriptDir "md2pdf_app.py"

if (-not $PythonPath) {
    $cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if (-not $cmd) {
        $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    }
    if ($cmd) {
        $PythonPath = $cmd.Source
    } else {
        $PythonPath = "$env:LOCALAPPDATA\Programs\Python\Python314\pythonw.exe"
    }
}

$extensions = @(".md", ".markdown")

if ($Unregister) {
    Write-Host "[md2pdf] Removing context menu entries..." -ForegroundColor Cyan
    foreach ($ext in $extensions) {
        $keys = @(
            "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\md2pdf.direct",
            "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell\md2pdf.menu",
            "HKCU:\Software\Classes\$ext\shell\md2pdf.direct",
            "HKCU:\Software\Classes\$ext\shell\md2pdf.menu"
        )
        foreach ($key in $keys) {
            if (Test-Path $key) {
                Remove-Item -Path $key -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  Removed: $key" -ForegroundColor DarkGray
            }
        }
    }
    Write-Host "[md2pdf] Context menu entries successfully removed." -ForegroundColor Green
    return
}

# Ensure files exist
if (-not (Test-Path $directConvert)) {
    throw "direct_convert.py not found at: $directConvert"
}
if (-not (Test-Path $studioApp)) {
    throw "md2pdf_app.py not found at: $studioApp"
}
if (-not (Test-Path $PythonPath)) {
    throw "Python executable not found at: $PythonPath"
}

Write-Host "[md2pdf] Registering context menu for Markdown files..." -ForegroundColor Cyan
Write-Host "  Python:  $PythonPath" -ForegroundColor DarkGray
Write-Host "  Runner:  $directConvert" -ForegroundColor DarkGray
Write-Host "  Studio:  $studioApp" -ForegroundColor DarkGray

foreach ($ext in $extensions) {
    $targetBases = @(
        "HKCU:\Software\Classes\SystemFileAssociations\$ext\shell",
        "HKCU:\Software\Classes\$ext\shell"
    )

    foreach ($base in $targetBases) {
        # 1. Direct 1-Click Convert
        $directKey = Join-Path $base "md2pdf.direct"
        $directCmd = Join-Path $directKey "command"
        New-Item -Path $directCmd -Force | Out-Null
        Set-ItemProperty -Path $directKey -Name "(Default)" -Value "Convert to PDF (md2pdf)"
        Set-ItemProperty -Path $directKey -Name "Icon" -Value "shell32.dll,242"
        Set-ItemProperty -Path $directCmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`""

        # 2. Cascading Menu with Options
        $menuKey = Join-Path $base "md2pdf.menu"
        $menuShell = Join-Path $menuKey "shell"
        New-Item -Path $menuShell -Force | Out-Null
        Set-ItemProperty -Path $menuKey -Name "(Default)" -Value "md2pdf Options"
        Set-ItemProperty -Path $menuKey -Name "MUIVerb" -Value "md2pdf Studio ▾"
        Set-ItemProperty -Path $menuKey -Name "SubCommands" -Value ""
        Set-ItemProperty -Path $menuKey -Name "Icon" -Value "shell32.dll,71"

        # Submenu 1: Auto Detect
        $sub1 = Join-Path $menuShell "1_auto"
        $sub1Cmd = Join-Path $sub1 "command"
        New-Item -Path $sub1Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub1 -Name "(Default)" -Value "Convert with Smart Detect"
        Set-ItemProperty -Path $sub1Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`""

        # Submenu 2: Sidebar Light
        $sub2 = Join-Path $menuShell "2_sidebar_light"
        $sub2Cmd = Join-Path $sub2 "command"
        New-Item -Path $sub2Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub2 -Name "(Default)" -Value "Convert with Sidebar Light"
        Set-ItemProperty -Path $sub2Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`" --mode sidebar_light"

        # Submenu 3: Sidebar Dark
        $sub3 = Join-Path $menuShell "3_sidebar_dark"
        $sub3Cmd = Join-Path $sub3 "command"
        New-Item -Path $sub3Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub3 -Name "(Default)" -Value "Convert with Sidebar Dark"
        Set-ItemProperty -Path $sub3Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`" --mode sidebar_dark"

        # Submenu 4: LaTeX Formal
        $sub4 = Join-Path $menuShell "4_latex"
        $sub4Cmd = Join-Path $sub4 "command"
        New-Item -Path $sub4Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub4 -Name "(Default)" -Value "Convert with LaTeX Formal"
        Set-ItemProperty -Path $sub4Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`" --mode latex"

        # Submenu 5: Auto & Open
        $sub5 = Join-Path $menuShell "5_open"
        $sub5Cmd = Join-Path $sub5 "command"
        New-Item -Path $sub5Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub5 -Name "(Default)" -Value "Convert and Open PDF"
        Set-ItemProperty -Path $sub5Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$directConvert`" `"%1`" --open"

        # Submenu 6: Edit in Studio
        $sub6 = Join-Path $menuShell "6_edit"
        $sub6Cmd = Join-Path $sub6 "command"
        New-Item -Path $sub6Cmd -Force | Out-Null
        Set-ItemProperty -Path $sub6 -Name "(Default)" -Value "Edit in md2pdf Studio"
        Set-ItemProperty -Path $sub6Cmd -Name "(Default)" -Value "`"$PythonPath`" `"$studioApp`" `"%1`""
    }
}

Write-Host "[md2pdf] Context menu registered successfully!" -ForegroundColor Green
Write-Host "  Right-click any .md or .markdown file in File Explorer to use:" -ForegroundColor White
Write-Host "   - 'Convert to PDF (md2pdf)' -> Direct 1-click conversion with toast notice" -ForegroundColor Gray
Write-Host "   - 'md2pdf Studio ▾'         -> Choose specific engine (Light, Dark, LaTeX) or Edit" -ForegroundColor Gray
