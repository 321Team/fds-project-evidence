# cicd-runner01 Runner v1.2 — 실제 PASS_PREPARE

## 판정과 범위

2026-09-16 16:15:30–16:18:12 UTC (2026-09-17 01:15:30–01:18:12 KST) 실제 prepare가 PASS다. 외부 원본 SHA256 `31941e2758c6060815319ab542e854f491f655da254b3e1848a23b3932d52b0f`, 21977 bytes. 외부17파일/중첩49파일 manifest·정확한 집합, 외부/중첩 checksum, 복제 HOST 결과 바이트가 일치한다. 원본 archive/sidecar를 그대로 보존했다. JSON은 원본에서 바이트 그대로 복사한 조회용 사본이다.

- 배포 v1.2 bundle manifest `5c0e851db396689ca6549562f2a442cd5a6e6b58d2d30dd0f99d5f3338dc3bfe`와 일치. 코드 PR19 HEAD `9cb8d6c702f750b9276daec859b1c237109daed1`은 변경하지 않았다.
- 새 이미지 `sha256:02d097ce453f4011218a081286e02be2c4d64599d1b329d6d98e049b9c34fd85`. 원본 image inspect의 bundle label, container inspect의 이미지 ID/exit0/OOM=false를 대조했다. Podman 원본 ID의 선택적 `sha256:` 접두어는 실행 코드와 같은 정규화로 비교했다.
- 전용 계정 UID1001/비sudo, rootless Podman/cgroupv2/systemd/SELinux Enforcing 확인.
- 컨테이너 격리14/14, 네트워크 허용4/거부4, 총8/8 PASS. files.pythonhosted.org의 HTTP404는 TLS 통신 도달 판정 범위로 허용하며 인증/API 성공을 의미하지 않는다.
- 공식 Runner2.337.0 다운로드 226430031bytes 및 SHA256 `70920811a4f8ad4328818682bca5c6469c1c942fab52448868071d0063816613` 일치. 검증된 r3 base 이미지 ID 유지.
- 명령12건의 기대 rc/timeout=false 일치. runner/proxy/workspace 모두 REMOVED.
- proxy 종료 시 SIGTERM 15초 후 SIGKILL 전환 경고가 원문에 있다. 제거 rc0 및 exists rc1로 실제 제거를 확인했다. 정리 실패나 명령 timeout으로 해석하지 않는다.
- `runner_registration_attempted=false`, `github_actions_verdict=NOT_RUN`, 운영 apply/엔진 전환=false.

**이 결과는 수정된 이미지의 prepare 성공이다.** BOM 호환성 수정 후 실제 등록 식별정보 파싱 성공은 아직 시험하지 않았다. 이전 v1.1 실패를 PASS로 바꾸거나 실제 예외를 소급 확정하지 않는다.

## 고정된 다음 입력

새 PREPARED 경로:

`/home/ansible-verify/ansible-actions-6ca2111d63f740438342fd7da89e25da/evidence/PREPARED.json`

실제 실행한 v1.2 원본 키트 경로:

`/home/server01_cicd-runner/ansible-runner-v1_2.RxNbHB6V/FDS_Ansible_Actions_Runner_v1_2`

현재 남은 선행 확인은 이전 실패에서 만든 정확한 Runner 이름의 관리 API 목록 부재다. 아직 제출 증적이 없고 현재 연결은 Runner 관리 API endpoint를 지원하지 않는다. 기존 infra-cicd Runner ID2는 이 작업의 대상이 아니다. 아래 조회는 등록/삭제/Workflow 변경을 하지 않는다.

## 지금 실행할 명령 — ansible01 기존 관리 로그인

```bash
(
set -euo pipefail
umask 077
TASK_ABSENCE_FILE=$(mktemp "$HOME/ansible-runner-absence.XXXXXXXX.txt")
printf 'repository=321Team/infra-ansible\nrunner_name=ansible-ci-e64364fe3bab45fabcc43aea675c9693\nqueried_at_utc=%s\n' "$(date -u +%FT%TZ)" > "$TASK_ABSENCE_FILE"
TASK_QUERY_RC=0
if gh api --paginate 'repos/321Team/infra-ansible/actions/runners?per_page=100' \
  --jq '.runners[] | select(.name == "ansible-ci-e64364fe3bab45fabcc43aea675c9693") | {id,name,status}' \
  >> "$TASK_ABSENCE_FILE"; then
  :
else
  TASK_QUERY_RC=$?
fi
printf '\nquery_rc=%s\n' "$TASK_QUERY_RC" >> "$TASK_ABSENCE_FILE"
sha256sum "$TASK_ABSENCE_FILE" > "$TASK_ABSENCE_FILE.sha256"
cat "$TASK_ABSENCE_FILE"
printf 'HOME_EVIDENCE=%s\n' "$TASK_ABSENCE_FILE"
exit "$TASK_QUERY_RC"
)
```

출력 `HOME_EVIDENCE=` txt와 `.sha256`를 제출한다. `query_rc=0`이고 일치하는 객체가 없으면 조회 시점에 해당 이름이 없다는 근거다. 객체가 나오면 자동 삭제하지 말고 ID/name을 대조한다. 조회 실패는 부재로 판정하지 않는다.

## 부재 확인 후 등록 재검사

기존 관리 도구 `FDS_Ansible_Admin_Token_v1_1_1`로 새 단기 토큰을 발급하고 packet만 비공개 경로로 cicd-runner01 기존 로그인 홈에 전달한다. 양쪽 토큰 모두 최소10분이 남아 있어야 한다. 아래 명령은 부재 확인과 새 token packet 발급/전송을 완료한 뒤 사용한다.

```bash
(
set -euo pipefail
cd /home/server01_cicd-runner/ansible-runner-v1_2.RxNbHB6V/FDS_Ansible_Actions_Runner_v1_2
sha256sum -c SHA256SUMS
read -r -p '전송한 새 TOKEN_PACKET 절대 경로: ' TASK_TOKEN_PATH
chmod 600 -- "$TASK_TOKEN_PATH"
sudo bash run.sh registration-check \
  --prepared /home/ansible-verify/ansible-actions-6ca2111d63f740438342fd7da89e25da/evidence/PREPARED.json \
  --token-file "$TASK_TOKEN_PATH"
)
```

새 `PASS_REGISTRATION_CHECK`, identity/BOM 선별 증적, 실제 ID/name의 관리 API 부재까지 검증한다. 증적은 기존 로그인 홈에 생성하며 token JSON은 첨부하지 않는다. 현재는 새 등록/Actions 활성화·정상/고의 결함 CI·최신 HEAD 독립 승인·merge·운영 적용·Issue5 AC 완료를 주장하지 않는다. 코드/증적 PR은 Draft를 유지한다.
