# P1-SEC-01 — Edge Cutover RUN 20261008T1800 원본 (edge01 upstream E-K3S → Worker 3대)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). 2026-10-08 17:35~19:35 KST 창에서 실행한 Edge Cutover 회차의 원본이다. **이 폴더는 #19 AC 충족이나 종결을 주장하지 않는다.** 판정은 Review Owner 몫이다. 같은 날 실패·복구한 앞 회차는 [`../edge-cutover-20261008T1730/`](../edge-cutover-20261008T1730/README.md)에 있다.

## 출처
| 항목 | 값 |
|---|---|
| 승인 | [6055806493](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6055806493)(새 RUN·코드·창 조건부 GO, 역할·검증·복구 조건은 [6054208925](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6054208925) 계승) |
| 코드 | [infra-kubernetes#77](https://github.com/321Team/infra-kubernetes/pull/77) 승인 HEAD `cdd2883d9e9473db3b9307fe6cbe94d2a26bd58d` → 병합 `81ad791d5a6a611d3c7f0068bd638e60ec8e28f8` |
| 실행 파일 SHA-256 | `edge01-cutover.sh` `7e9182533a6ba766eebd728944b1f3922071e3922470819921ba8594a38a8af9`, `cutover-capture.sh` `e4caceafc4cfa72fa5b9bf369257141b67c7b1c5679a02de6350c428a81aeb88`, `cutover-capture-judge.py` `fef5bc372b0ed34a6033a104e0ca961d53df5536152c14198b8ccaa4c9c21dfe`, `control01-cutover-check.sh` `7fa38c7a93f1d8b6c7607142420fb3c065b2ed75647561230c120a84043b45a2` |
| P4 수집기 | infra-ansible `c0d784fa9a1d9dfc57f504ed969c036d0860acef` `playbooks/p1-sec-01-b2-collect-58.yml` `42fc3ed486b9b16f6be156b2770ada6cf9fa725c9b0a5882473afa0bd7eb9024` |
| 실행 | 이재환(edge01 `server08`, control01 `server02`, PC `10.1.93.29`, db01), 이권욱(ansible01 `server01_ansible` → Worker 3대 `svc_ansible` become, 최종 judge·P4). 명령 안내·수신 검증·편입 정리는 Claude Code 보조 |
| 전달 경로 | edge01 → PC `scp`. control01·ansible01 → 콘솔 `base64` 출력 → PC 복원(관리망·control01은 PC에서 scp 불가). Worker 캡처는 ansible `fetch`로 ansible01에 모은 뒤 ansible01 묶음에 포함 |

## 파일
| 파일 | 내용 | SHA-256 |
|---|---|---|
| `edge01-edge-cutover-20261008T1800.tgz` | edge01 `~/edge-cutover-20261008T1800/`(check·apply 로그, `upstream-file.before/after/path`, sent·smoke·capture·judge 출력, E-K3S Pod 목록) + `/var/tmp/edge-cutover-capture-20261008T1800/{check,apply}/` | `6b9e223c36aa655f132a7e847266bcc74b986d484d0909731daef3d2782b77c8` |
| `control01-edge-cutover-20261008T1800.tgz` | control01 `/root/edge-cutover-20261008T1800/` pre `173540`, post `174937` | `b763c7f3672647ec1700608c93c7f76cc9a2636b24910531cd74ca7721084b23` |
| `ansible01-edge-rx-20261008T1800.tgz` | ansible01 `~/edge-rx-20261008T1800/`: Worker report check/apply, 인계 수신본(edge01 check·apply, control01 pre), 최종 judge 출력 2개, P4 출력·`evidence-58` 결과, Worker 3대 캡처 원본 tgz | `b61fca5a975eedd31f821af13f9dc1d3e666d345e8b82af77365f6d879826168` |
| `control01-post-c3/control01-post-182210.log` | C3 종료 뒤 post(18:22:10). 서버 `sha256sum` 값과 같음 | `c0b9dfc12de73de6bd1fe6d7dc1c6b80f624c5c9a1eaf9cdbb1282648c190683` |
| `pc/edge-cutover-20261008T1800-{n1,e2e,c3}.txt` | PC PowerShell 출력(P1·P2·N1, #20 D-04 E2E, C3). `Tee-Object` 기본값이라 **UTF-16LE·CRLF**이며 그대로 보존 | `SHA256SUMS` 참고 |

- `.sha256`·`.contents.txt`: edge01 것은 서버에서 만든 sidecar 그대로다. control01·ansible01 것은 서버 콘솔에 출력된 SHA와 일치함을 확인한 묶음으로 PC에서 다시 만든 것이다(내용은 서버 출력과 같다).
- Worker 캡처 tgz 3개(묶음 안) SHA는 Worker에서 만든 값과 같다: worker01 `b4d1f3d9…b647`, worker02 `2c2f88a3…b701`, worker03 `4b139960…cfef2`.
- 비밀정보 패턴 검색(`password|secret=|token=|BEGIN … KEY|bearer|authorization:|DB 접속 문자열`) 일치 0건(묶음 6개·Worker 캡처 tgz·PC 출력 모두). 캡처는 pcap·요청 원문을 남기지 않는다(표식 요청의 식별 필드만).

## 진행·관측 (원본 보존 — 판정 아님)
| 단계 | KST | 관측 |
|---|---|---|
| 진입 전 | 17:26~17:35 | 4개 파일 SHA 승인값 일치, 도구·sudo·`NTPSynchronized=yes`, 새 인계 루트 710 `svc_ansible:--x`. DNS 검증 종료 기록 [6055811930](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6055811930), 비중첩 확인, 단톡 공지 |
| C0-a pre | 17:35:40 | NodePort `etp=Local 80->8000:30080`, endpoint 1·1·1 ready, GNP `.50/32`, 32085 0, MON 23/23/EMPTY, 조회 실패 0 |
| C0-b~e | 17:36~17:39 | 캡처 4곳 READY, edge check rc0 `EDGE_CAPTURE_READY tag=check173816`(반영 판정 rc0), Worker report err=0 |
| C0-f | 17:40 | judge `scope=all captured=edge01,k8s-worker01,k8s-worker02,k8s-worker03 verdict=METHOD_READY` rc0 |
| C1 | 17:41:42~ | edge `apply` rc0 `EDGE_OK`(4줄 전환, reload 17:41:43, 반영 rc0, 표식 9/9 200·smoke 201, `/metrics` 404, E-K3S 쪽 apply 표식 0) → judge apply `PATH_OK` rc0 |
| C2 | 17:44~17:52 | P1 200 / P2 404 / N1 Worker `:30080` 3건 False(출발 `.29`) / P3 `SIM_cut_202610081800_apply` 1행 false/false / D-04 POST 201·`SIM_e2e_202610081800` 1행 false/false·`sum(transaction_save_success_total)` 1→2 / P4 3대 source `10.1.93.50` PASS / post 17:49:37 C0와 같음 |
| C3 | 17:51:19~18:21:19 | PC `/readyz` 5분 간격 7회 모두 200. post 18:22:10: endpoint·GNP·32085·MON 23/23/EMPTY·조회 실패 0·재시작 0 |

인계(`/var/tmp/edge-cutover-handoff-20261008T1800/`) 사본은 원본·사본·원본 재확인·ansible01 수신 SHA가 모두 일치했다. 인계 트리의 `svc_ansible` ACL 회수·삭제는 이 PR 병합 뒤 해당 경로에만 한다.

AI 사용: CLAUDE_ASSISTED
