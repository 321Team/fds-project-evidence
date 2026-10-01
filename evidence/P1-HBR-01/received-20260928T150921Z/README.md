# P1-HBR-01 — hbr01-test.sh 사전 입력값 자동 수집 원본 (2026-09-28)

Record ID: **P1-HBR-01** ([baseline #13](https://github.com/321Team/fds-project-baseline/issues/13)). [infra-ansible PR#59](https://github.com/321Team/infra-ansible/pull/59)의 `playbooks/p1-hbr-01-discover.yml` 실행 원본을 편입합니다.

| 항목 | 값 |
|---|---|
| 원본 | `p1-hbr01-discover-20260928T150921Z.tar.gz` |
| SHA-256 | 같은 폴더 `.sha256` sidecar와 일치 |
| 수집 도구 | [infra-ansible `playbooks/p1-hbr-01-discover.yml`](https://github.com/321Team/infra-ansible/blob/feat/p1-hbr-01-discover/playbooks/p1-hbr-01-discover.yml) ([infra-ansible PR#59](https://github.com/321Team/infra-ansible/pull/59)) |
| 수집 | ansible01(`server01_ansible`) → cicd-runner01(10.250.10.20)/k8s-control01/harbor01(10.1.93.54) 대상 read-only 접속 시험, 2026-09-28 KST. **`변경 없음`은 `p1-hbr-01-discover.yml` 실행 단계 자체에 한정된다** — 그 직전 prerequisite provisioning(아래 참고)은 별도 운영 변경이다 |
| 선행 운영 변경 | `MUTATING / REVIEW NOT VERIFIED`. cicd-runner01·harbor01에 `svc_ansible` 계정 신규 생성 및 SSH key 등록, cicd-runner01 `linux-admins` 그룹 추가, 두 호스트에 `svc_ansible ALL=(ALL) NOPASSWD: ALL` sudoers 등록. 상세는 immutable commit [infra-ansible `f76e09f`의 runbook](https://github.com/321Team/infra-ansible/blob/f76e09fafbb50563eeee1872ac5e9556b47b2f89/docs/runbooks/P1-HBR-01-runner-harbor-svc_ansible-provisioning.md) 참고. baseline #13/[infra-ansible PR#59](https://github.com/321Team/infra-ansible/pull/59)는 discovery playbook만 승인 대상이며, 이 provisioning 자체를 승인하거나 P1-HBR-01 AC PASS 근거로 삼지 않는다 |
| 전달 경로 | ansible01 → 사용자가 zip으로 압축해 세션에 업로드 → 세션에서 압축 해제 후 SHA-256 재확인 |
| 수집·제공 | 이하영(P1-HBR-01 Lead). 수집 자동화 playbook·대상 서버(cicd-runner01/harbor01) `svc_ansible` 계정 프로비저닝 보조는 Claude Code(CLAUDE_ASSISTED). 실제 서버 실행은 이하영이 ansible01에서 직접 수행 |

## 수신 검증

- tar.gz 내부 `SHA256SUMS`(2개 파일 대상) 재계산 일치
- 비밀정보 검색: 해당 없음(인증서 SAN, 방화벽 zone/포트, 설치 경로, Worker IP만 포함 — 키/비밀번호 없음)

## 내용물 요약 (원본 보존 — 판정 아님)

| 파일 | 내용 |
|---|---|
| `hbr01-discover-run.log` | `ansible-playbook ... playbooks/p1-hbr-01-discover.yml` 전체 실행 stdout(`tee`로 저장). Runner(SAN/CA/로컬 이미지), Control Plane(Worker IP), harbor01(방화벽/설치 경로) 조회 및 최종 "수집 결과" 요약 포함 |
| `hbr01-values.env` | 위 실행이 생성한 결과 파일 원본. `IP=10.1.93.54`, `IP_SAN_MATCH=True`, `HARBOR_DIR=/home/server08/harbor`, `ALLOW_IPS`(Worker 3대), `RUNNER_SOURCE_CANDIDATE=10.250.10.20` 등 |

## 배경과 한계

- 이 playbook은 **읽기 전용 사전 수집 도구**다. `hbr01-test.sh`(baseline #13 AC 검증 스크립트) 실행 전 필요한 설정값(SAN, CA, 로컬 이미지, Runner/Worker IP, 방화벽, harbor 설치 경로)을 모아 `hbr01-values.env`로 저장하는 것이 전부이며, **어떤 서버 설정도 변경하지 않는다**.
- `IP_SAN_MATCH=True`는 harbor01 인증서의 IP SAN에 `10.1.93.54`가 포함돼 있다는 **조회 결과**이지, baseline #13의 AC-01(또는 다른 Runtime AC)이 PASS로 판정됐다는 뜻이 아니다. baseline #13은 현재 "Runtime AC는 PASS 0 / FAIL 0 / NOT VERIFIED 6" 상태이며, 실제 AC 판정은 `hbr01-test.sh` 실행 결과와 Lead 판단으로 별도 진행한다.
- `source_image`를 지정하지 않고 실행해 `SRC_IMG=CHECK_ME_REQUIRE_DIGEST_PINNED_SOURCE_IMAGE`로 남아 있고, `RUNNER_SOURCE_CANDIDATE`도 승인된 관측값이 아닌 자동 수집 후보값이다. 두 값 모두 `hbr01-test.sh` 실행 전 사람이 직접 검증·확정해야 한다(playbook 자체의 명시적 주석).
- 이 실행을 위해 cicd-runner01·harbor01에 `svc_ansible` 자동화 계정을 신규 프로비저닝했다. 상세 절차는 immutable commit [infra-ansible `f76e09f`의 runbook](https://github.com/321Team/infra-ansible/blob/f76e09fafbb50563eeee1872ac5e9556b47b2f89/docs/runbooks/P1-HBR-01-runner-harbor-svc_ansible-provisioning.md) 참고(이전 링크는 이동 가능한 `feat/p1-hbr-01-discover` branch를 가리켰음 — immutable commit으로 교체).

### 잔여 보안 상태 — 후속 하드닝 필요 (미해소)

prerequisite provisioning으로 cicd-runner01·harbor01에 아래 상태가 남아 있으며, 이 evidence 편입 시점 기준 **미해소**다. read-only discovery 실행 자체의 결과가 아니라 그 실행을 가능하게 하기 위한 선행 운영 변경의 잔여 상태이므로 별도로 명시한다.

- **키 제한 미적용**: 등록된 `svc_ansible` SSH key가 k8s_nodes 대상 `harden_svc_ansible_key.yml`(`from="10.250.10.10",restrict`) 적용 범위 밖 — 현재 제한 옵션 없이 등록된 상태
- **`NOPASSWD: ALL`**: 두 호스트 모두 `svc_ansible`에 범위 제한 없는 sudo 권한 부여
- **`linux-admins` 그룹 편입**: cicd-runner01의 `AllowGroups linux-admins` sshd 제한을 우회하기 위해 automation 계정을 관리자 그룹에 추가 — harbor01에는 동일 제한이 없어 두 호스트 간 sshd 정책이 일관되지 않음(runbook 자체가 "의도된 것인지 확인 필요"로 남김)

이 세 항목의 하드닝/rollback은 runbook의 "후속 조치 필요(미완료)" 절에 기록돼 있으나 **담당자·완료 조건은 이 편입 시점 기준 미지정**이다. Lead/Support가 별도로 owner와 완료 조건을 정하기 전까지 이 evidence 편입만으로 하드닝이 완료됐거나 승인됐다고 간주하지 않는다.

이 편입은 원본 보존이다. P1-HBR-01의 AC 체크, Gate, 티켓 상태는 바꾸지 않는다.
