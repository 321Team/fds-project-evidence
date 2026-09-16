# GitHub Runner 조회 수신 검토 — 2026-09-16

**판정: 수집 COLLECTED / 원본 무결성 PASS / infra-ansible에 조회되는 Runner0대.** 서버 로컬 Ansible 두 엔진 PASS와 GitHub Actions 실행 준비를 구분한다. 이번 조회로 앞선 GH_NOT_INSTALLED에 따른 목록 미확인 상태는 해소됐다.

## 현재 확인

사용자가 ansible01의 `server01_ansible` UID1000에서 기존 v1 키트의 `--scope github`를 실행했다. 2026-09-16 12:34:28~12:34:29 UTC (21:34:28~21:34:29 KST), 홈 `/home/server01_ansible`. 두 저장소 조회는 모두 rc0·OBSERVED다.

| 저장소 | 조회 결과 | 상태 |
|---|---:|---|
| 321Team/infra-ansible | Runner0대 | 빈 목록 |
| 321Team/infra-cicd | Runner1대, ID2 / cicd-runner01 | online, busy=false |

infra-cicd의 labels는 `self-hosted`, `Linux`, `X64`, `p1-cicd`, `onprem`, `podman`이다. 이는 조회 시점의 값이며 현재까지 영구 유지된다고 주장하지 않는다. busy=false는 당시 작업을 수행 중이지 않았다는 뜻이며 미래 자원 가용성 보장은 아니다.

앞선 cicd-runner01의 시스템 서비스·로컬 .runner 관측(12:24:18 UTC)은 URL infra-cicd / ID2 / 이름 cicd-runner01 / 서비스 계정 UID1000이었다. 이번 GitHub 응답의 ID·이름·repository와 일치한다. 따라서 기존 앱 Runner가 Ansible 저장소에도 등록·허용된 것으로 가정할 근거가 없다. 이번 빈 목록은 두 저장소에 대한 조회 범위의 사실이며 조직 전체의 Runner 부재나 조직 정책·권한 설정을 확정하지 않는다.

**실행 차단:** 현재 확인된 infra-ansible Runner가 없고 Workflow도 아직 docs/ci의 비활성 초안이다. Runner 구성·등록·격리/정리 확인, 활성화 변경 리뷰, 실제 정상/고의 결함 Actions 실행이 남았다. 수집 완료는 실행 승인 또는 CI PASS가 아니다.

## 원본 무결성

- [수신 원본](input/ansible-runner-evidence.tar.gz): 970바이트, SHA256 `35fc458552d3530a7ad14cb23eefd33f7d741bff63ee3e1057eb9c7025fadfcf`.
- 첨부명 `(1)`은 내려받기 접미사이며 sidecar의 정식 파일명은 `ansible-runner-evidence.tar.gz`다. 원본 바이트는 변경하지 않았다.
- 외부 sidecar, 안전한 경로·중복 없는 파일집합, 일반 파일3개와 내부 manifest의 데이터 파일2개 해시를 검증했다. [RESULT.json](original/RESULT.json)은 원본 바이트 사본이다.
- 보고된 collector SHA256 `bdeb35849d453aa9fc2463b93012e9775fd7701c2a89f479be0b7bf470016bb3`는 배포 v1과 일치한다. 실행 코드 및 gh 원응답은 이 증적에 포함되지 않고 검증·선별한 결과가 저장돼 있다. 이를 별도 원격 attestation으로 주장하지 않는다.
- 기존 collector는 GET의 모든 페이지를 수신해 총수·중복·타입을 확인한 뒤 OBSERVED를 기록한다. 이번 수신에서 확인한 것은 해당 collector 결과와 무결성이다. 수신 검토자가 관리 API를 별도로 실시간 재조회한 것은 아니다.

## 후속

추가 동일 수집이나 두 엔진 재시험은 요청하지 않는다. [Runner 구성 검토안](RUNNER_PLAN.md)을 다음 작업 범위로 준비했다. 기존 앱 Runner의 등록 URL을 바꾸거나 조직 공유로 전환하지 않는 방향이다. 구성안은 아직 설치·등록·승인된 상태가 아니다.

현재 PR17 `169571801d1b0cee0ba75137380149a48d6b56dd`, PR18 `d5147ebff0febbb8ab2afca28fe64d68301e033c`는 Draft/open/unmerged이며 정식 review0건이다. 증적 PR13의 기존 COMMENTED는 이전 HEAD 대상이다. infra-ansible Actions Run0건을 재조회했다. main 병합·Runner 등록/서비스 변경·변수 설정·Workflow 활성화·운영 apply·엔진 전환·인수 완료 처리는 수행하지 않았다.

관련: [이전 호스트 관측](https://github.com/321Team/fds-project-evidence/blob/4dbdca2bc1bf0ee222204bfd0987e198cb65f698/evidence/infra-ansible-followup/cicd-runner01-runner-readiness-20260916T122418Z/README.md), [두 엔진 PASS](https://github.com/321Team/fds-project-evidence/blob/f3b5ea69f5119fc89e15f128c086f1c8eba97fea/evidence/infra-ansible-followup/cicd-runner01-podman-20260916T110635Z/README.md), [Issue5](https://github.com/321Team/infra-ansible/issues/5).
