$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$log = Join-Path $here ("d11d-jaehwan-" + (Get-Date -Format "yyyyMMddTHHmmss") + ".log")
Start-Transcript -LiteralPath $log | Out-Null
"START_KST=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
& (Join-Path $here "d11d-jaehwan.ps1")
"END_KST=" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Stop-Transcript | Out-Null
Read-Host "Done. Press Enter to close"
