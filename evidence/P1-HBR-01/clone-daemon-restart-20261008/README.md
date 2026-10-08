# P1-HBR-01 — 격리 복제본 Docker 재시작 실패 및 수동 복구

기준일: 2026-10-08 KST. 실행: 이권욱의 복제본 콘솔 수동 명령. 수집·편입 보조: CODEX_ASSISTED.

**13:25 후속 수신:** [지정 로그 14개 원본 수신·검증](../clone-original-logs-20261008/README.md)을 별도 회차에 추가했다.
아래 “미수신”은 최초 캡처 편입 시점의 이력이다. 원본 failure.sha256 2/2·archive·내부 manifest 대조가 후속에서 완료됐으며,
복구 후 healthy/listener 화면의 원본 텍스트 및 정확한 복구 완료 시각은 계속 미수신이다. 당시 RECEIPT.json/PNG는 수정하지 않는다.

## 판정

**Docker 재시작 후 Harbor 자동 복구 실패를 격리 복제본에서 관측했고, 기존 컨테이너를 수동 시작하여 10개 모두 healthy로 복구했다. 자동기동 결함 해결 또는 운영 AC 인수로 판정하지 않는다.**

| 단계 | 확인된 결과 | 근거 |
|---|---|---|
| 복제본 수신 | 전달 5개 파일 SHA-256 일치, 독립 단일 디스크 체인 검사 rc=0 | `host/hash-verification.json`, `host/disk-chain-check.json`, `host/disk-descriptor.json` |
| 작업 사본 준비·첫 부팅 | 별도 작업 사본, 가상 NIC 제거, 새 UUID. 첫 부팅 후 컨테이너 0개 | `host/preparation.json`, `host/boot-selected.json`, `console/console-receipt-1156/` |
| 정지 방식 정정 | 공급자가 복제 전 compose down 후 정상 종료했다고 정정. 컨테이너 0개는 그 상태와 부합하며 자동기동 실패 증거가 아님 | `console/preclone-shutdown-correction/RECEIPT.json` |
| T0 재생성 | 기존 Compose/로컬 이미지로 up, 표시 rc=0, 10개 healthy, 443/1514 LISTEN | `console/reconstruction-result/` |
| T1 Docker 재시작 | 재시작 명령 표시 rc=0. 약 1분 후 앱 9개 Exited(128), harbor-log만 healthy. 443/80 소실, 1514는 관측 시점 LISTEN | `console/daemon-restart-failure/` |
| T1 직접 오류 | 9개 모두 logging driver 초기화 중 [::1]:1514 연결 거절. journal 표시 12:27:17 KST | `console/daemon-restart-cause/` |
| T2 수동 복구 | compose start 표시 rc=0. 같은 짧은 ID의 10개 컨테이너 healthy, 443/80/1514 LISTEN 복구 | `console/manual-recovery-result/` |

RUNTIME는 **격리 복제본 한 회차의 사용자 콘솔 제출 관측**이다. REVIEW/PUBLICATION은 이 편입 PR에서 별도 처리하며, 운영 적용·VM 재부팅 시험·후보 수정 적용은 수행하지 않았다.

## 출처와 환경

- 수신 원본: `C:\Project321team\harbor-clone\harbor01-test`. 시험 작업 사본: `D:\FDS-Isolated-Lab\harbor01-20261008\harbor01-test.vmx`.
- 공급자는 server08의 VMware Workstation에서 원본을 Powered Off 후 Full Clone했다고 전달했다. 공급자 VMware 원본 로그와 원본 Harbor health 응답은 미수신이다. 공급자 진술과 로컬 수신 파일 검사 결과를 구분한다.
- 원본 VMDK SHA-256: `ef83d9512d25e8859675a8dabc438f95aa6cb651c35c335e3df656bc4bc5ca87`. 250 GiB 가상 용량, monolithicSparse, parentCID=ffffffff. 해시는 수신 시 파일 무결성 확인이며 Harbor 데이터 무결성 시험이 아니다.
- 수신 파일과 작업 사본의 준비 시 해시를 대조했다. 부팅 후 원본 보존 확인은 작은 4개 파일 해시 및 전체 5개 파일 크기/mtime 대조다. 부팅 후 20.9GB 원본 디스크를 다시 전량 해시한 것으로 표시하지 않는다.
- 작업 VM은 가상 NIC 자체가 없고 shared folders/USB/ISO를 비활성화했다. 게스트 출력에는 lo와 docker0만 보인다. 운영망과 동일한 네트워크 조건의 인수 시험이 아니다.
- 게스트 표시: `server08@harbor01`, Harbor 이미지 `v2.13.1`, Docker context `unix:///var/run/docker.sock`, root dir `/var/lib/docker`.
- Compose: `/home/server08/harbor/docker-compose.yml`; 게스트 화면 SHA-256 `0a84f57692268335eeedf45411e025d784e520bf749fa3501a3800cdfcb14ef0`. 시험 후 재해시는 미수신이며, 제공 명령에는 Compose 변경이 없다.
- `/data/database`, `/data/registry`, `/data/redis` 및 bind 경로 존재를 확인했다. DB 67M, registry 1.2G, redis 108K는 표시 크기이고 DB 내용·이미지 Pull의 정합성 검증이 아니다.
- 증적 생성 경로: 게스트 `/home/server08/harbor-clone-t0-01/`. 게스트 원본 텍스트와 해시 값은 아직 받지 못했다.

## 실행 순서와 해석

공급자는 복제 전 다음 두 명령을 실행했다고 정정했다.

```sh
cd /home/server08/harbor && sudo docker compose down
sudo shutdown -h now
```

따라서 공급자의 최초 “부팅 후 443 지연이 기존 자동기동 실패와 같은 양상”이라는 설명은 철회된 진술이다. 원본은 이후 compose up으로 복구했다고 전달받았으며, 이 문서는 원본 서버를 다시 조작하지 않았다.

아래는 **이미 사용자 콘솔에서 실행한 명령의 기록**이며 추가 실행 지시가 아니다. root 권한 명령은 정상 계정의 sudo 인증으로 실행했다.

```sh
# T0: 기존 설정/데이터/이미지에서 컨테이너 재생성
sudo docker compose -f /home/server08/harbor/docker-compose.yml up -d --pull never --no-build
# T1: 컨테이너를 지우지 않은 상태에서 Docker 데몬 재시작
sudo timeout 120s systemctl restart docker
# 실패 시점의 상태/daemon journal 수집 후 T2: 기존 객체 수동 시작
sudo docker compose -f /home/server08/harbor/docker-compose.yml start
```

원래 실행은 각 단계 로그와 rc 파일로 리다이렉션했고, 해당 명령 화면을 함께 보존했다. T1에서는 Docker 재시작 명령의 rc=0과 Harbor 자동 복구 결과가 달랐다. inspect와 journal의 공통 직접 오류는 다음과 같다.

```text
failed to create task for container: failed to initialize logging driver: dial tcp [::1]:1514: connect: connection refused
```

이 오류는 앱 task 생성 전 syslog 연결 실패를 가리킨다. 실패 후 화면에서는 logger가 `127.0.0.1:1514`를 듣고 있었지만, **각 실패 순간 IPv4 listener가 이미 준비됐는지는 입증되지 않았다.** IPv4 fallback 시도·순서도 이 화면으로 확인할 수 없다.

T2는 설정을 변경하는 명령 없이 logger가 준비된 뒤 기존 객체의 start에 성공했다. 이는 logger 준비 시점/순서의 개입 가능성을 뒷받침하지만 IPv6 단독 원인 또는 IPv4 주소 고정만으로 해결된다는 증거는 아니다. 마지막 화면의 앱 Up 2 minutes / logger Up 14 minutes는 상대 표시이며 정확한 복구 시각이나 지속 관측 구간으로 환산하지 않는다.

## 증적 무결성과 정정

- `console/`의 PNG 19개는 사용자가 제출한 원본 이미지 바이트를 복사한 것이다. RECEIPT.json은 각 시점의 로컬 해석·수신 메타데이터이며 서버 원본 JSON이 아니다. 과거 PENDING/NOT_YET_CONFIRMED 필드는 작성 당시 이력이다. 현재 판정은 이 README와 마지막 수신 기록을 함께 읽는다.
- `SOURCE_INDEX.json`에 복사 출처·바이트 수·SHA-256을 기록했다. `host/boot-selected.json`은 무관한 다른 VM 목록을 제외한 **선택 필드 파생본**이며, 원본 로컬 기록의 해시와 파생 범위를 표시한다.
- 최초 T0 RECEIPT의 짧은 ID 2개 수기 전사 오류를 보존하고 T1 RECEIPT에 정정했다: core `436e086cb531` → 화면의 `543e086cb531`; trivy-adapter `07757cdb9924` → 화면의 `07757cdb93e4`. 원본 PNG는 변경하지 않았다. 전후 동일성 판정은 정정된 화면 값 기준이다. 전체 ID 파일은 미수신이다.
- 게스트에서 state-errors.txt와 docker-journal.txt에 대한 failure.sha256 생성 명령이 보인다. **그 해시 값 및 원본 파일을 수신·검증한 것은 아니다.** 이 폴더 SHA256SUMS는 로컬 수신 이미지/메타데이터 무결성만 검증한다.
- VM 디스크·DB·자격증명·전체 Compose/VMX는 이 저장소에 포함하지 않았다. 이미지는 암호 입력 내용 없이 sudo prompt만 포함한다.

## 추적성과 잔여 작업

- 책임 티켓: [baseline #13 — P1-HBR-01](https://github.com/321Team/fds-project-baseline/issues/13). 현행 정본 v3.1.21 (`979facb98de8ca1f1e2ce22f38b27ac3366f3fc3`)의 Service/Health·재기동 복구 검토에 연결한다. AC-01 전체, TLS·IF-09/10·AC-04 Source allowlist 등을 PASS로 상향하지 않는다.
- IPv4 주소 후보: [infra-harbor-trivy #12](https://github.com/321Team/infra-harbor-trivy/pull/12), 조회 HEAD `2b3b3b17417c9e1c4d6c8a0fdd9cb95cad5a03f7`, 리뷰 대기. **본 복제본/운영에 미적용**이다. 이번 관측을 후보 수정 검증 결과로 해석하지 않는다.
- [readonly observer #13](https://github.com/321Team/infra-harbor-trivy/pull/13), [격리 syslog CI #14](https://github.com/321Team/infra-harbor-trivy/pull/14)는 별도 코드·시험이다. 여기의 guest trial은 해당 스크립트 실행 결과가 아니다. 과거 “복제 VM 미확보”였던 준비 상황은 이번 수신으로 해소됐으나, 후보 수정 및 VM reboot 검증은 남았다.

우선순위:

1. 현재 복구 상태를 유지하고 guest 원본 start/end, up, before-restart, restart, state-errors, docker-journal, failure.sha256, recovery-start, recovery 자료를 비밀정보 노출 없이 별도 수집회차로 전달·대조한다. 현재 이미지 기반 판정을 원본 완비로 상향하지 않는다.
2. IPv4 주소 설정과 logger readiness를 분리한 후보 시험 절차·복구안을 검토한다. 주소만 바꾼 성공을 가정하지 않는다.
3. 격리 복제본에서 후보 적용 후 Docker 재시작, 이어 별도 VM 재부팅을 검증한다. 실행 전 설정·ID·시각·logger 준비 신호를 확보하고 실패 시 추가 재시작 대신 로그 보존 후 알려진 수동 복구 경로를 사용한다. 이 문서 자체가 운영 적용 승인은 아니다.
4. 독립 리뷰 후 증적 편입. 운영 Runtime 적용·정본/티켓 종결은 해당 Gate로 별도 처리한다.

공식 동작 참고: [Compose down](https://docs.docker.com/reference/cli/docker/compose/down/), [Compose start](https://docs.docker.com/reference/cli/docker/compose/start/). 제공된 재현 결과의 근거는 위 원본 화면과 수신 기록이다.
