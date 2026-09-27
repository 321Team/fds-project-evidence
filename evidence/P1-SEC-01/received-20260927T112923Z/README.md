# P1-SEC-01 — B3 CP 3대 kubelet serverTLSBootstrap 확인 (2026-09-27)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). GWONUK Review Owner 판정의 B3(kubelet serverTLSBootstrap 6-node 영구 형상화) 대응 — 6개 노드 중 CP 3대의 live 확인. Worker 3대는 기존 9/26 evidence에 이미 있음. 관련: [infra-ansible PR#55](https://github.com/321Team/infra-ansible/pull/55)(병합 완료, source), [이슈 코멘트](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-5854007820).

| 항목 | 값 |
|---|---|
| 원본 | `p1-sec01-b3-cp-tls-20260927T112923Z.tar.gz` |
| SHA-256 | `53d55cce8f5f15c62c6266d7e1dda7cf8e439817345ecd7a005fb37c267ef247` (같은 폴더 `.sha256` sidecar와 일치) |
| 수집 | ansible01(`server01_ansible`)에서 CP 3대에 개별 SSH(`server02`/`server03`/`server04`)로 접속해 `sudo grep` 실행, 결과를 ansible01에서 파일로 취합 |
| 수집 시각 | 2026-09-27T11:30:00Z (세션 대화 중 개별 확인한 시각을 취합 시점에 기록) |
| 전달 경로 | ansible01 → 사용자가 `scp -r`로 로컬 수신 → zip 압축 → 세션 업로드 → 세션에서 압축 해제 후 SHA-256 재확인 |
| 수집·제공 | 이하영(P1-SEC-01 Lead). 수집·편입 정리는 Claude Code 보조 |

## 수신 검증

- tar.gz 바이트 SHA-256이 ansible01에서 계산한 값과 일치(`53d55cce...`)
- 비밀정보 검색: 해당 없음(설정값 확인 텍스트만 포함)

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 내용 |
|---|---|
| `b3-cp-serverTLSBootstrap.txt` | CP 3대(`10.1.93.102/103/104`, `k8s-control01/02/03`) 각각의 `/var/lib/kubelet/config.yaml`에서 `serverTLSBootstrap` 값 확인. 3대 전부 `true` |

## 배경 및 한계

- 이 확인은 개별 SSH 세션마다 대화 중 순차로 실행됐으며, 각 명령의 원시 stdout은 세션 텍스트로만 존재했다가 이후 ansible01에서 하나의 파일로 재작성(retype)됐다. **명령 자체의 실행 결과값(値)은 서버에서 나온 그대로이나, 파일 자체는 사후 작성본**이다 — SSH 세션의 raw pty 출력을 그대로 캡처한 것이 아님을 명시한다.
- Worker 3대(`k8s-worker01/02/03`)의 동일 확인은 이 편입 범위 밖이며, 9/26 evidence([received-20260926T152344Z](../received-20260926T152344Z/README.md))의 `99-csr-final.txt`(6개 노드 CSR 전체 승인)로 이미 뒷받침됨.
- AC 최종 충족 판정은 이 편입만으로 하지 않는다. 판정은 Review Owner/Lead가 baseline #19에서 별도로 함.

이 편입은 원본 보존이다. P1-SEC-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
