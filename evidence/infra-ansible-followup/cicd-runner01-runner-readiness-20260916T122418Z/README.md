# cicd-runner01 Runner 수집 원본 검토 — 2026-09-16

**판정: 원본 무결성 PASS / 호스트 시스템 서비스 관측 완료 / GitHub Runner 목록 UNKNOWN / 실행 준비 NOT_ASSESSED.** INFO_INCOMPLETE를 시험 FAIL이나 Runner 등록0대로 해석하지 않는다.

## 확인된 사실

사용자가 제출한 실행은 2026-09-16 12:24:18 UTC (21:24:18 KST), cicd-runner01의 `server01_cicd-runner` UID1000에서 수행됐다. 기존 로그인 홈은 `/home/server01_cicd-runner`다. 수집기가 기록한 configuration_changed=false, github_actions=NOT_RUN을 유지한다. 수신 검토자가 서버에서 직접 실행한 결과가 아니다.

| 항목 | 원본 관측 |
|---|---|
| 시스템 Runner 서비스 | actions.runner.321Team-infra-cicd.cicd-runner01.service |
| 서비스 상태 | loaded / active / running |
| 서비스 계정 | server01_cicd-runner, UID/GID1000:1000 |
| 작업 디렉터리 | /home/server01_cicd-runner/actions-runner |
| 로컬 등록 URL | https://github.com/321Team/infra-cicd |
| 로컬 agentId / agentName | 2 / cicd-runner01 |
| 로컬 poolId / poolName | 1 / Default |
| 로컬 workFolder | _work |
| GitHub 목록 조회 | UNKNOWN / GH_NOT_INSTALLED |

수집기는 시스템 서비스 목록2개 조회와 해당 unit show에서 모두 rc0을 기록했다. 이 범위에서 infra-cicd 서비스1개가 관측됐고 infra-ansible 시스템 서비스는 목록에 없었다. **다른 호스트의 Runner, 사용자 범위 서비스, 수동 실행 프로세스, GitHub 저장소/조직 전체 등록 부재를 입증하지 않는다.**

`GH_NOT_INSTALLED`는 구현상 `shutil.which('gh')`가 실패했다는 뜻이다. 정확하게는 해당 프로세스 PATH에서 gh 실행 파일을 찾지 못했으며 시스템 어느 위치에도 설치되지 않았다고 단정하지 않는다. GitHub 인증 조회 자체가 수행되지 않았으므로 권한 부족·등록0대·offline 판정을 내리지 않는다.

`.runner`는 로컬 설정이다. agentId/poolName/URL만으로 현재 GitHub online 상태·repository 접근·조직 Runner group 정책을 확정하지 않는다. active/running도 실제 Job 수신 증거가 아니다.

앞선 rootless Podman 시험의 전용 계정 `ansible-verify` UID1001과 이번 실제 서비스 계정 UID1000은 다르다. 전용 계정의 sudo 거절·격리 시험 결과를 이 서비스 계정에 전용하지 않는다. 이번 sudo_policy·credential_isolation·cleanup은 모두 NOT_ASSESSED다.

## 무결성 검토

- [사용자 원본](input/ansible-runner-evidence.tar.gz): 1,293바이트, SHA256 `7fd5edd3426aebcdaa512fe7b51a1a9a9375b900cf5164099826e9e6a76d9752`.
- 원문 sidecar와 일치. 안전한 상대 경로·중복 없는 파일집합·일반 파일3개와 내부 SHA256SUMS의2개 데이터 파일 해시를 대조했다. 링크·특수파일은 없다.
- [RESULT.json](original/RESULT.json)과 [COLLECTOR.sha256](original/COLLECTOR.sha256)은 압축에서 꺼낸 바이트 동일 사본이다.
- 기록된 collector SHA256 `bdeb35849d453aa9fc2463b93012e9775fd7701c2a89f479be0b7bf470016bb3`는 배포한 v1 코드 해시와 일치한다. 압축에 실행 코드 자체는 없으므로 이를 별도의 원격 실행 attestation으로 해석하지 않는다.
- 기존 v1 ZIP SHA256 `80a2216b3db6380a9b9ac751259bfb495fcc863b6657f12de8b13b7f99c0db61`. 이번 수신에 따른 코드 수정·새 키트 발행은 하지 않는다.

## 바로 이어갈 단계

이미 gh를 사용한 관리용 호스트(ansible01 등)에서 기존 v1 키트를 그대로 사용해 다음 조회만 실행한다. 관리자 gh 인증을 시험 전용 계정으로 옮기거나 cicd-runner01의 Runner를 재등록하지 않는다.

```bash
python3 -I -B collect.py --scope github
```

HOME_EVIDENCE와 HOME_SHA256 두 파일을 인수한다. INFO_INCOMPLETE여도 원문을 제출한다. Repository Runner 목록의 인증 조회 실패는 등록 부재와 다르다. [GitHub 공식 조회 권한](https://docs.github.com/en/rest/actions/self-hosted-runners#list-self-hosted-runners-for-a-repository).

이 조회는 host/systemd 수집을 반복하지 않는다. 조회한 등록 정보와 이번 서비스 계정을 연결한 뒤 실제 사용할 Runner의 repository/group/labels, 계정·운영 자격증명 분리, sudo, 일회성 또는 동등 격리, 성공/실패/취소 시 정리의 근거를 확정한다. 활성화 변경 독립 리뷰 → 정상/고의 결함 실제 Actions → 인수 순서를 유지한다.

수신 시 PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c` 유지. 두 PR의 정식 review0건, PR13은 이전 HEAD의 COMMENTED1건이다. infra-ansible Actions Run은0건이다. 앞선 [두 엔진 PASS_LOCAL_REVALIDATION](https://github.com/321Team/fds-project-evidence/blob/f3b5ea69f5119fc89e15f128c086f1c8eba97fea/evidence/infra-ansible-followup/cicd-runner01-podman-20260916T110635Z/README.md)은 유효하며 동일 소스 재시험은 요청하지 않는다. 운영 적용·엔진 전환·Runner 변경·Workflow 활성화·병합·독립 승인은 수행하지 않았다.
