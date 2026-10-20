# D-11d (infra-rosa main d2f2b2b README d11d-ps block, placeholders only replaced). Owner: jaehwan.
$env:PATH = "C:\Users\soldesk\AppData\Local\Temp\claude\C-----------09------\107b808e-9cec-4a78-bc25-61e52f7a12cc\scratchpad\oc-4.22.17\bin;" + $env:PATH   # this process only
"oc: " + (Get-Command oc).Source
$d11HadConfig = Test-Path Env:KUBECONFIG
$d11PreviousConfig = $env:KUBECONFIG
$d11Directory = Join-Path ([IO.Path]::GetTempPath()) ("rosa-d11d-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $d11Directory -ErrorAction Stop | Out-Null
$d11Config = Join-Path $d11Directory "kubeconfig"
$d11Ok = $false
try {
  $env:KUBECONFIG = $d11Config
  $API_URL = "https://api.fds-rosa-hcp.khht.p3.openshiftapps.com:443"
  $EXPECTED_USER = "jaehwan"
  oc login $API_URL -u $EXPECTED_USER
  if ($LASTEXITCODE -ne 0) { throw "STOP: 로그인 실패" }
  $actualUser = oc whoami
  if ($LASTEXITCODE -ne 0) { throw "STOP: whoami 실패" }
  $actualServer = oc whoami --show-server
  if ($LASTEXITCODE -ne 0) { throw "STOP: server 조회 실패" }
  "USER=$actualUser"; "SERVER=$actualServer"
  if ($actualUser -ne $EXPECTED_USER -or $actualServer -ne $API_URL) { throw "STOP: 사용자 또는 server 불일치" }
  # monitoring-edit 은 jaehwan 에게만 fds-app 에서 부여(baseline#25). 본인 로그인으로 J-1·J-2 와 같은 질문을 확인
  $mon = if ($EXPECTED_USER -eq 'jaehwan') { 'yes' } else { 'no' }
  foreach ($c in @(@('yes','get','pods','-n','fds-app'), @('no','create','deployments','-n','fds-app'),
                   @('no','list','nodes'), @('no','get','secrets','-n','fds-app'),
                   @($mon,'create','servicemonitors.monitoring.coreos.com','-n','fds-app'),
                   @($mon,'create','prometheusrules.monitoring.coreos.com','-n','fds-app'))) {
    $want = $c[0]; $args2 = $c[1..($c.Count - 1)]
    $got = oc auth can-i @args2; $rc = $LASTEXITCODE
    "can-i $($args2 -join ' ') => $got (rc=$rc)"
    if (-not (($want -eq 'yes' -and $rc -eq 0 -and $got -eq 'yes') -or ($want -eq 'no' -and $rc -eq 1 -and $got -eq 'no'))) {
      throw "STOP: can-i 기대값 불일치($($args2 -join ' '))"
    }
  }
  $d11Ok = $true
} finally {
  if ($d11HadConfig) { $env:KUBECONFIG = $d11PreviousConfig } else { Remove-Item Env:KUBECONFIG -ErrorAction SilentlyContinue }
  if (Test-Path -LiteralPath $d11Config) { oc --kubeconfig $d11Config logout | Out-Null; Remove-Item -LiteralPath $d11Config }
  Remove-Item -LiteralPath $d11Directory -ErrorAction SilentlyContinue
  if ($d11Ok) { "D-11d RESULT: PASS" } else { "D-11d RESULT: FAIL" }
}
