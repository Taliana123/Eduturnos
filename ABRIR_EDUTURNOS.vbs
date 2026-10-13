Set sh = CreateObject("WScript.Shell")
base = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run Chr(34) & base & "\tools\iniciar_eduturnos.bat" & Chr(34), 1, False
