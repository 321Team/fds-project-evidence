# Harbor AC04 사전 읽기 원본의 오프라인 체인 대조

CODEX_ASSISTED. 2026-10-07 21:22:18~21:22:24 KST 관측. infra-ansible#62 지원.

## 판정과 범위

`analysis.rc=2`, `FIXED_TAIL_SWAP_REVIEW_REQUIRED`입니다. 실제 harbor01 원본 및 관측 입력을 분석했으며 MOCK이 아닙니다. FORWARD, DOCKER-USER, NAT DOCKER는 일치하고 DOCKER-FORWARD 마지막 ACCEPT 2줄 및 filter DOCKER 마지막 DROP 2줄 각각의 지정 자리 교환만 검출됐습니다. 앞4줄/행 수는 유지됐고 분석 대상5체인의 다른 drift는 검출되지 않았습니다.

전체 verifier는 이 회차 실행하지 않았으며 기존 FAIL을 PASS로 바꾸지 않습니다. TLS/객체/guard/counter/복구/동시 작업 전체 Gate를 검사하지 않았고 Docker restart 및 서버 설정 변경은 없습니다. `runtime_go=false`, `full_verifier_pass=false`, `ac04_accepted=false`를 유지합니다.

이 관측은 21:22의 사전 지원 자료이며, [23:00 조건부 GO](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-6037611737)가 요구하는 22:35 이후 현장 START Gate를 대신하지 않습니다. 현장 실행자는 이하영이며 이 편입으로 실행 소유권이나 변경창을 확대하지 않습니다.

## 원본·재현·무결성

- host `harbor01/10.1.93.54`, 기존 ansible01 경유 `svc_ansible`, 읽기 전용 `sudo -n`.
- `RECEIPT.json`: 실제 명령/시작·종료 시각/rc/stdout hash. 각 stdout/stderr를 원바이트 보존.
- 원본 `/var/lib/fds-change/P1-HBR-01-AC04/original-state.json` SHA256 `1090de081eb5969f2fc5e1d890f6f022494cf652356a6b8d541be70d6b62d83f` 일치. PRESTATE 5개 항목 서버 검증 rc0. original-state 이외 PRESTATE 4개 파일 자체는 이번에 전송하지 않았으므로 저장소만으로 그4개를 재검산할 수는 없습니다.
- `current-state.json`은 성공한5개 iptables 명령 stdout을 순서 그대로 splitlines한 입력입니다. 추가/정렬/규칙 수정 없음. 각 명령을 두 번째 읽어 동일함을 확인했지만 원자적 snapshot이나 writer 배제를 입증하지 않습니다.
- `analysis-tool.py`는 병합된 infra-ansible `da4e273e7e26a9a0b51211e5146066960df072b5`의 `tools/p1-hbr-ac04-docker-chain-analysis.py` 바이트. SOURCE.json에 blob/SHA256.
- 최초 수집 시 호스트 기대명 오기(`fds-harbor01`)로 hostname 단계에서 STOP했습니다. 이전 관측과 실제 hostname `harbor01`로 수정 후 새 디렉터리에서 재실행했습니다. 최초 시도는 hostname 읽기 외 실행 없으며 여기의 결과는 수정 후 회차입니다.

검토 PC의 Python3 표준 라이브러리 환경에서 다음을 실행합니다. 기존 증적은 덮어쓰지 말고 새 출력 경로에 stdout/stderr/rc를 보존하십시오.

```text
python -I -B analysis-tool.py --original-state original-state.json --original-sha256 1090de081eb5969f2fc5e1d890f6f022494cf652356a6b8d541be70d6b62d83f --current-state current-state.json
```

예상 RC2/지정 pair 교환 후보이며 생성 시각은 재실행마다 다릅니다. INPUT/hash 불일치·INCOMPLETE·UNSUPPORTED_DRIFT이면 중단하고 원본을 확인합니다. 재시작/적용/복구 명령은 이 자료에 포함하지 않습니다. 운영 변경이 없어 서버 원복 대상은 없습니다.

`SHA256SUMS`는 이 디렉터리에서 자신을 제외한 모든 파일을 검증합니다. 원본 규칙·IP는 기존 비공개 프로젝트 저장소 범위의 기술 증적이며 token/password/key/env 수집은 하지 않았습니다. PR 독립 리뷰와 편입 병합은 별도 단계입니다.
