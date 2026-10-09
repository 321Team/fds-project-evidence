# Runner 후속 준비 관측 — 2026-10-09 08:51~52 KST

CODEX_ASSISTED · 이권욱. **READONLY 관측 완료 / 실행 readiness Gate 미판정 / 독립 리뷰 대기.** 정상 `server01_cicd-runner@10.250.10.20`, UID1000, 기존 ansible01 SSH 경유·기존 키·엄격한 host key 검사로 조회했다. sudo·새 권한·원격 파일 생성·이미지/서비스/설정 조작은 없다.

| 관측 항목 | 실제 결과 | 해석 한계 |
|---|---|---|
| 정상 계정·홈 | cicd-runner01 / UID1000 / 홈0700, 소유1000:1000 | Actions Job 계정·현재 등록 상태는 미조회 |
| Runtime 부모·기존 공급 디렉터리 | 모두0700/1000:1000, symlink 아님 | 새 후보 경로 생성·전달은 안 함 |
| 기존 공급 manifest | f4d55db6ecbefe2057cdb7ca6539b6818549744eb8bfc127ba12dcfa4eb6143b, source/tool adc90410 | 기존 공급 전체125파일은 이번에 재검증하지 않음 |
| 버전 출력 | Python3.12.14 / Git2.52.0 / Podman6.1.0, 모두rc0 | Podman info/이미지load/rootless 실행 아님 |
| 홈 filesystem | 여유56,439,685,120bytes(약52.6GiB), readonly flag false | 전체 작업 용량 산정·실제 쓰기·inodes/quotas 미검증 |
| rootless ID 설정 | 본 계정 subuid/subgid 각524288:65536 | 권한 범위 존재 관측, 실제 매핑 실행 아님 |
| SELinux | enforce1 | 실제 컨테이너 label/AVC 무발생 증거 아님 |
| Trivy 파일 | root0:0/0755,168,456,354bytes, SHA d89bcc6510a267f11b773398cbf1be5520ce39f9e8b6633178c4487f05b7d791 | main의binary pin 일치만 확인; 실행·DB 신선도·scan 미실행 |

첫 수집의 Trivy `INCOMPLETE`는 검사기의64MiB 한도보다 실제 파일이 커 hash를 읽지 않은 결과다. 파일 손상으로 판정하지 않으며 원본 결과를 그대로 보존했다. 크기168,456,354bytes를 확인한 후 그 파일만 별도 회차에서192MiB 상한·1MiB 스트리밍·nofollow·읽기 전후 inode/size/mtime/ctime로 읽고 main pin 일치를 확인했다. 다른 항목을 반복 수집하지 않았다.

`repository-input.json`은 조회한 GitHub main04e49811의 config hash·Source adc90410·기존 공급 경로·Trivy pin 및 최신 app-test-build-scan Run37642123031/success를 기록한다. workflow는 회차별 새 checkout을 소비하므로 이를 현재 실행 중인 서버의 단일 활성 config라고 표현하지 않는다. 후보affbc69로 main입력이 전환되지 않은 사실과 기존 공급 manifest가 유지된 사실을 구분한다. 이 snapshot은 장래 dispatch 시 main/승인을 재확인해야 한다는 조건을 대신하지 않는다.

수집기/stdout 해시4/4, SSH2회 rc0·stderr0. 계정·고정호스트·00~09시 gate를 적용했고 Secret/환경변수/credential·프로세스 명령행은 읽거나 반출하지 않았다. 이 조회기는 독립 사전 리뷰를 받지 않은 순수 Pre-check다. stdout·invocation의PC/호스트 시각을 각각 보존했고 동기화 오차는 별도 측정하지 않았다.

잔여: APP Source/Unit 처분·공급tool 승인 연결, 새 Runner 공급 경로/전달 후 bytes 검증, 실제 consumer config 리뷰, 신규 회차의 rootless 동작·Trivy DB/freshness·TLS·등록/Job·비중첩 및 실행GO. 현재 snapshot만으로 READY/PASS Gate를 생성하거나 기존 공급을 새 Source에 재사용하지 않는다. 운영 변경·후속 이미지 실행·Harbor 접근은 없다.
