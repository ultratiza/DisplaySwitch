' Script para ejecutar DisplaySwitch de forma 100% silenciosa sin ventana de consola negra
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = ScriptDir
MainPy = ScriptDir & "\main.py"

' Buscar pythonw.exe o pyw.exe
Dim pywPath
pywPath = "C:\Program Files\Python314\pythonw.exe"

If Not fso.FileExists(pywPath) Then
    pywPath = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Launcher\pyw.exe")
End If
If Not fso.FileExists(pywPath) Then
    pywPath = "pythonw.exe"
End If

WshShell.Run """" & pywPath & """ """ & MainPy & """", 0, False
