Option Explicit

Dim shell, fileSystem, scriptDirectory, monitorScript, command

Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")

scriptDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
monitorScript = fileSystem.BuildPath(scriptDirectory, "CS549-ResourceMonitor.ps1")
command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Hidden -File """ _
    & monitorScript & """ -AutoStart"

' Window style 0 hides the host console. The PowerShell script explicitly shows its WPF window.
shell.Run command, 0, False
