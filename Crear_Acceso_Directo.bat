@echo off
chcp 65001 >nul
echo Creando acceso directo de DisplaySwitch en tu Escritorio...

set "SCRIPT_DIR=%~dp0"
set "ICON_FILE=%SCRIPT_DIR%app_icon.ico"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "NEW_SHORTCUT=%DESKTOP_DIR%\DisplaySwitch.lnk"
set "LEGACY_SHORTCUT=%DESKTOP_DIR%\Los Monitores pingueros del Fede.lnk"

if exist "%SCRIPT_DIR%MonitorSwitch.exe" (
    set "EXE_TARGET=%SCRIPT_DIR%MonitorSwitch.exe"
) else (
    set "EXE_TARGET=%SCRIPT_DIR%DisplaySwitch.vbs"
)

powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%NEW_SHORTCUT%'); $s.TargetPath = '%EXE_TARGET%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'DisplaySwitch - Control Inteligente de Pantallas'; if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; $s.Save(); $s2 = $ws.CreateShortcut('%LEGACY_SHORTCUT%'); $s2.TargetPath = '%EXE_TARGET%'; $s2.WorkingDirectory = '%SCRIPT_DIR%'; $s2.Description = 'Los Monitores pingueros del Fede'; if (Test-Path '%ICON_FILE%') { $s2.IconLocation = '%ICON_FILE%' }; $s2.Save(); $sm = [Environment]::GetFolderPath('Programs'); $s3 = $ws.CreateShortcut((Join-Path $sm 'DisplaySwitch.lnk')); $s3.TargetPath = '%EXE_TARGET%'; $s3.WorkingDirectory = '%SCRIPT_DIR%'; $s3.Description = 'DisplaySwitch'; if (Test-Path '%ICON_FILE%') { $s3.IconLocation = '%ICON_FILE%' }; $s3.Save()"

if exist "%NEW_SHORTCUT%" (
    echo [OK] Acceso directo creado exitosamente en tu Escritorio y Menú Inicio:
    echo "%NEW_SHORTCUT%"
) else (
    echo [ERROR] No se pudo crear el acceso directo.
)
pause
