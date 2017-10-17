strComputer = "."
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
Set colItems = objWMIService.ExecQuery("Select * from Win32_OperatingSystem")
For Each objItem in colItems
  strOScaption=objitem.Caption
  strOSversion=objitem.Version
Next
osVersion = left(strOSversion,1)
'wscript.echo osVersion
SET Wshell=CreateObject("Wscript.Shell")
if osVersion = "5" then
    Wshell.run "c:\checkpass\checkpass.exe"
else:
    Wshell.run "c:\checkpass\run.js"
end if
