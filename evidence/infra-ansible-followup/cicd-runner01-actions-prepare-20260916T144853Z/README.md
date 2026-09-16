# cicd-runner01 Runner v1.1 — 실제 prepare PASS

제출된 실행 증적을 원본 checksum, 두 archive manifest의 전체 일반 파일 coverage, 명령·실제 inspect·결과 JSON·정리 기록으로 대조했다. 포함된 바이트의 무결성과 내부 일관성을 확인한 것이며 독립적인 원격 attestation으로 표현하지 않는다.

| 항목 | 확인 결과 |
|---|---|
| 원본 | `ansible-actions-runner-evidence.tar(1).gz`를 보관 시 표준 이름으로 복사, 원본 bytes 동일 |
| SHA256 / 크기 | `879789b3d542e23703990c2cd71475c5d217281c12fa77f619452e5e0b091bc5` / 21,915bytes |
| 실행 기록 시간 | 2026-09-16 14:48:53–14:50:38 UTC / 23:48:53–23:50:38 KST |
| 코드 HEAD | `5fd76293da7bbcdb238cc8edeb8206e47283e395` (infra-ansible PR19) |
| Bundle manifest | `ecff16d871d7b08cd9aa72e580e54830b61d438ec9dcbbf3847bbac2f690ff46` — 고정 GitHub HEAD와 대조 일치 |
| 이미지 | `sha256:104b262f24146c8cb5068f8e577bff0ed438bd7941ff1a43ab74a04dc735573f` |
| 계정·호스트 | UID1001/GID1002 비sudo, rootless Podman6.1.0, SELinux Enforcing, cgroupv2/systemd |
| Runner/이미지 | 공식 archive checksum, 고정 base ID, network=none build, Listener2.337.0 실행 확인 |
| 격리 | 14항목 PASS. UID/GID1000, cap0, NNP, seccomp, container_t, network=lo, readonly root/socket, CPU2/RAM4GiB/PIDs512 및 직접 공인/사설 연결 거절 |
| 네트워크 | HTTPS 허용4건, 사설/metadata/미허용 도메인 차단4건 PASS |
| 종료/정리 | Runner exit0/OOM false. 두 정확한 CID rm0/exists1, workspace REMOVED |
| 최종 판정 | `PASS_PREPARE_EVIDENCE_RECONCILED` |
| 미실행 | Runner 등록/해제, 실제 Actions, 운영 적용 |

files.pythonhosted.org 루트는 HTTP404를 반환했다. 이 항목은 TLS/HTTP 도달 시험이므로 설계된 통과 범위200–499에 해당한다. 패키지 다운로드나 인증·CI 성공을 뜻하지 않는다.

프록시는 SIGTERM으로 15초 내 종료되지 않아 Podman이 SIGKILL을 사용했다. rm rc0 및 동일 CID exists rc1로 제거를 확인했으므로 이번 prepare 정리 조건은 충족한다. 비차단 개선 사항은 프록시의 명시적인 SIGTERM 처리다. 이미 통과한 bundle/image binding을 유지하기 위해 이번에는 실행 코드를 바꾸지 않는다. 개선을 적용하면 새 manifest로 prepare가 필요하다.

이전 v1의 podman-info 차단은 v1.1 재실행에서 나타나지 않았고 실제 준비가 완료됐다. v1 당시의 직접 원인은 누락된 stderr 때문에 여전히 확정할 수 없다. 여러 수정 중 어느 하나만을 원인으로 단정하지 않는다.

다음 단계는 같은 v1.1 키트의 등록·즉시해제 검사다. [NEXT_STEPS.md](NEXT_STEPS.md)에 실제 PREPARED 경로를 넣었다. 정상/고의 결함 Actions를 포함한 Issue5 AC, 독립 리뷰, workflow 활성화, merge는 이 PASS로 대체하지 않는다.
