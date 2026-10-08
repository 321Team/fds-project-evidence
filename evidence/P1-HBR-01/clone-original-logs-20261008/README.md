# Harbor 복제본 실패·복구 원본 로그 수신 — 2026-10-08

이권욱 / CODEX_ASSISTED. [앞선 캡처 회차](../clone-daemon-restart-20261008/README.md)의 미수신 로그를 보완한다.
**지정 원본 14파일 수신·해시 대조 완료. 자동기동 실패 및 수동 복구 판정은 유지한다.**

## 수신과 무결성

- 게스트 원본: `harbor01:/home/server08/harbor-clone-t0-01`, 정상 server08 콘솔에서 sudo로 수집기 실행.
- 수집 시각: `2026-10-08T13:25:23.724919+09:00`. 새 Runtime 시험이나 서비스/원본 변경 없이 지정 로그만 읽었다.
- HGFS 전용 공유 HBR_LOG_OUT으로 Windows 비공개 폴더에 전달. 가상 NIC는 계속 없었다.
- 수신 archive: `harbor-originals-20261008T132523-31f1dd4f.tar.gz`, 4416바이트.
- SHA-256: `b35b12d381994518b244049abb942e934282c7ccc49dcee9ac1445663834282e`. 원 archive·sidecar 바이트를 재압축 없이 보존했다.
- 원본 로그 14개 및 수집기 생성 receipt/manifest 2개, 총 16개 archive member를 확인했다. 개별 파일 SHA/크기 및 내부 manifest 15항목과 수신 archive SHA를 호스트에서 재대조했다.
- 기존 게스트 `failure.sha256`의 state-errors/docker-journal **2/2 일치**. SHA 생성 후 수신까지 두 파일이 해당 해시와 일치함을 뜻하며, 과거 원본의 외부 서명·시각 인증을 대신하지 않는다.
- 수집기는 SHA `cb259bd4a56ded1efa5b63f8bf146c727ab34a5e0c4e2bb3dc9522fffea04337`. 소스와 모의 검사 결과를 `verification/`에 보존했다. 사전 독립 리뷰된 Runtime driver로 표시하지 않는다.
- 새 파일 내용 검토와 비밀키/GitHub token/명시적 credential 패턴 점검에서 노출 항목을 발견하지 않았다. 전체 Compose·환경변수·DB·인증키는 수집 대상이 아니다.

## 원본에서 확인한 실행 시각

| 기록 | KST | 해석 |
|---|---|---|
| start.txt / end.txt | 12:18:06 / 12:19:50 | T0 재생성 전후 사용자가 남긴 시각. 명령의 정밀 실행 시간으로 환산하지 않음 |
| restart-start.txt | 12:26:19 | 사용자 사전 시각 기록 |
| journal: Stopping docker.service | 12:27:06 | 실제 daemon 종료 시작 기록. 위 사전 시각과 구분 |
| journal: logger 종료 대기 상한 | 12:27:16.715 | logger가 SIGTERM 후 10초 안에 종료되지 않아 강제 종료한 기록 |
| journal: 새 daemon 시작 | 12:27:16.936 | dockerd PID10761 |
| journal: 앱 9개 시작 실패 | 12:27:17.969~17.977 | 각 전체 container ID가 before-restart 원본과 일치 |
| journal: harbor-log sbJoin | 12:27:18.048 | logger 네트워크 연결 관련 기록. TCP/syslog 준비 완료의 직접 증거는 아님 |
| journal: daemon 초기화 완료 | 12:27:18.162 | Docker 서비스 시작 완료 |
| recovery-start.txt | 12:38:56 | 수동 복구 사전 시각. 복구 완료 시각 파일은 없음 |

up.rc, restart.rc, recovery.rc는 모두 0이며 restart.log는 0바이트다. Docker 재시작 rc0을 Harbor 자동 복구 성공으로 해석하지 않는다.

`before-restart.txt`는 전체 ID의 10개 healthy를 기록하고, `state-errors.txt`는 앱 9개 모두 아래 오류와 ExitCode128을 기록한다.

```text
failed to create task for container: failed to initialize logging driver: dial tcp [::1]:1514: connect: connection refused
```

수동 recovery.log에는 기존 앱 9개의 Started가 있다. 복구 후 10개 healthy·443/1514 LISTEN과 전후 짧은 ID 대조는 앞선 원본 캡처 근거다. 복구 후 전체-ID ps/inspect 또는 listener 텍스트 원본을 이번 14파일에 포함한 것으로 주장하지 않는다.

## 추가 해석과 한계

- 실패가 logger sbJoin 기록보다 먼저였다는 원본 순서를 확보했다. 준비 순서 개입 가능성은 더 뒷받침되지만, 각 시점의 IPv4 listener 준비 여부·fallback 시도는 계속 미확인이다.
- journal의 daemon 버전은 **29.8.0**이다. 이전 GitHub-hosted 격리 syslog CI의 Docker28.0.4와 다르므로 CI 결과를 이 clone의 동작 보증으로 전용하지 않는다.
- nftables 테이블 삭제 관련 info 메시지와 fsverity warning은 원문 그대로 보존한다. 이번 9개 기동 실패의 직접 State.Error는 syslog 연결 거부다. 부수 로그만으로 방화벽 변경을 정당화하지 않는다.
- 후보 #12 주소 override 미적용, 새 Docker 재시작·VM reboot 미실행, 자동기동 결함 미해결. TLS·데이터 정합성·운영 AC 전체 인수는 별도다.

## 수집 경로 수정 및 정리

첫 수집기는 `/mnt/hbr-out`만 허용해 자동 경로에서 STOP했다. 자동 HGFS 경로 `/mnt/hgfs/HBR_LOG_OUT`도 허용하되 실제 HGFS filesystem을 검사하도록 수정한 v2로 수신했다. 모의 원본 검사 5건, 경로 검사 7건은 실제 파일 수신과 구분한다.

`verification/export-host-result.json`에서 수신 archive/sidecar hash 일치, **13:25:34.766 KST removeSharedFolder rc0 / disableSharedFolders(runtime) rc0**를 확인했다. 후속 VMX에서 `sharedFolder.maxNum=0`, `isolation.tools.hgfs.disable=TRUE`, `ethernet0.present=FALSE`를 확인했다. 과거 sharedFolder0 문자열 일부는 남아 있어도 활성 목록 수는 0이며, 게스트 내부 mount point의 unmount 완료는 별도 사용자 확인 대상이다. 원본 로그와 수신본은 삭제하지 않았다.

관련: [baseline #13](https://github.com/321Team/fds-project-baseline/issues/13), [주소 후보 #12](https://github.com/321Team/infra-harbor-trivy/pull/12), [관측기 #13](https://github.com/321Team/infra-harbor-trivy/pull/13). 다음은 source 검토와 고정 실행안에 따른 주소/준비 순서 분리 시험이다. 이 수신 완료가 운영 적용·재시험 GO를 대신하지 않는다.

후속 사용자 확인: 두 umount 명령의 정리 요청에 사용자가 완료 취지로 회신했다. `verification/guest-unmount-attestation.json`에 원문과 해석을 보존한다. 게스트 정리는 **USER_REPORTED_COMPLETE**이며 도구로 mount 표를 직접 재조회한 것은 아니다.
