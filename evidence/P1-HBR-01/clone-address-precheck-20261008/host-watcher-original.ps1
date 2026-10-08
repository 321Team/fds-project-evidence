$ErrorActionPreference = 'Stop'
$prep = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'a1-preparation.json') -Raw | ConvertFrom-Json
$vmrunPath = 'C:\Program Files\VMware\VMware Workstation\vmrun.exe'
$record = [ordered]@{ started = (Get-Date).ToString('o'); status = 'WAITING' }
try {
    while ([DateTimeOffset]::UtcNow.ToUnixTimeSeconds() -lt $prep.manifest.expires_epoch) {
        $resultPath = Join-Path $prep.transfer 'A1_RESULT.json'
        $sidecarPath = Join-Path $prep.transfer 'A1_RESULT.sha256'
        if ((Test-Path -LiteralPath $resultPath) -and (Test-Path -LiteralPath $sidecarPath)) {
            $actual = (Get-FileHash -LiteralPath $resultPath -Algorithm SHA256).Hash.ToLowerInvariant()
            $expected = (Get-Content -LiteralPath $sidecarPath -Raw).Trim()
            if ($expected -ne ($actual + '  A1_RESULT.json')) { throw 'Result hash mismatch' }
            Copy-Item -LiteralPath $resultPath -Destination (Join-Path $PSScriptRoot 'a1-received.json')
            Copy-Item -LiteralPath $sidecarPath -Destination (Join-Path $PSScriptRoot 'a1-received.sha256')
            $record.status = 'RECEIVED_HASH_MATCH'
            $record.sha256 = $actual
            Start-Sleep -Seconds 5
            break
        }
        Start-Sleep -Seconds 2
    }
    if ($record.status -eq 'WAITING') { $record.status = 'EXPIRED_NO_RESULT' }
} catch {
    $record.status = 'ERROR'
    $record.error = $_.Exception.Message
} finally {
    $record.removeOutput = (& $vmrunPath -T ws removeSharedFolder $prep.vmx HBR_NEXT 2>&1 | Out-String)
    $record.removeRC = $LASTEXITCODE
    $record.disableOutput = (& $vmrunPath -T ws disableSharedFolders $prep.vmx runtime 2>&1 | Out-String)
    $record.disableRC = $LASTEXITCODE
    $record.finished = (Get-Date).ToString('o')
    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'a1-transfer-result.json') -Encoding utf8
}
