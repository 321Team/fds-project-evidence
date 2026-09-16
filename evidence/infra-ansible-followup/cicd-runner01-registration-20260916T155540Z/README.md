# cicd-runner01 Runner 등록 검사 실패 — v1.2 수정 후보

## 수신 결과

실서버 실행 2026-09-16 15:55:40–15:56:05 UTC (2026-09-17 00:55:40–00:56:05 KST)는 `FAIL`이다. 압축 원본 SHA256 `5cf140fc17fb452c2c681502aa61e2eede0cc6992bdb13c55269c42c06c2351a`, 6093 bytes. 외부17파일/중첩10파일 manifest·정확한 파일 집합·외부/중첩 checksum·복제 HOST 결과 바이트 일치. 원본 압축/sidecar는 변경 없이 보존했다.

| 항목 | 관측 |
|---|---|
| 전용 계정/비sudo | PASS, UID1001 |
| v1.1 bundle/image 결합 | 기존 PASS_PREPARE와 일치 |
| 컨테이너 격리 | 14/14 PASS |
| configure_rc / remove_rc | 0 / 0 |
| container exit/OOM | 1 / false |
| 등록 identity | 선별 결과에 없음 |
| runner/proxy/workspace 정리 | 모두 REMOVED |
| Actions/운영 적용 | NOT_RUN / false |

검사 대상 이름은 `ansible-ci-e64364fe3bab45fabcc43aea675c9693`이다. 제거 rc0는 기록됐지만 GitHub API 목록 부재는 아직 별도 확인되지 않았다. 현재 연결은 Runner 관리 API endpoint 조회를 지원하지 않아 원격 목록을 확인하지 못했다. 기존 infra-cicd Runner ID2는 이 작업의 삭제 대상이 아니다.

## 딥리뷰와 수정

공식 actions/runner v2.337.0의 `ConfigurationStore.SaveSettings` → `IOUtil.SaveObject`는 명시적인 `Encoding.UTF8` 파일 쓰기를 사용한다. 기존 Python `json.loads(Path.read_text())`는 UTF-8 BOM 설정 파일에서 실패하는 결함이 있으며 이를 로컬 파일로 재현했다. `configure_rc=0`, identity 누락, 회복 `remove_rc=0`, 전체FAIL이라는 실서버 패턴과 일치한다. 다만 당시 error_type과 원본 설정 바이트가 수집되지 않아 **실제 예외 종류/직접 원인은 UNKNOWN**으로 유지한다.

코드 수정 전 `REGISTRATION_FAILURE_REVIEW.md`를 작성했다. Runner v1.2는 bounded regular read + 엄격한 `utf-8-sig` 해석을 사용한다. URL/새 이름/양의 ID 검사, 실패 시 회복 제거와 원래 FAIL 유지, 계정·격리·정리를 보존한다. 허용된 실패 단계/예외 분류와 BOM·identity 검사 boolean만 추가하며 원문 값/토큰/private log는 제외한다.

기존37 + 등록 파일·전체 제어흐름 모형12 = 로컬49검사 PASS, Python AST9파일/bash 구문 PASS. 이것은 실제 GitHub 등록/Podman 시험이 아니다. `REGISTRATION_FAILURE_REVIEW.md`와 `LOCAL_RESULTS.json`에서 범위와 코드 해시를 확인할 수 있다.

새 배포 파일 `FDS_Ansible_Actions_Runner_v1_2.zip`: 56402 bytes, SHA256 `72ce31155f8879c6719a880113dfd35999c95bde43c3621e587a54ffaa3ada88`. 24파일, bundle manifest `5c0e851db396689ca6549562f2a442cd5a6e6b58d2d30dd0f99d5f3338dc3bfe`.

## 다음 실행

새 ZIP/sidecar를 cicd-runner01 기존 로그인 홈에 놓고 아래를 실행한다. 새 이미지에 코드가 포함되어야 하므로 이전 PREPARED.json으로 등록을 재시도하지 않는다. 새 prepare에는 토큰이 필요 없다.

```bash
(
set -euo pipefail
cd "$HOME"
sha256sum -c FDS_Ansible_Actions_Runner_v1_2.zip.sha256
TASK_RUNNER_KIT_DIR=$(mktemp -d "$HOME/ansible-runner-v1_2.XXXXXXXX")
unzip -q FDS_Ansible_Actions_Runner_v1_2.zip -d "$TASK_RUNNER_KIT_DIR"
cd "$TASK_RUNNER_KIT_DIR/FDS_Ansible_Actions_Runner_v1_2"
sha256sum -c SHA256SUMS
sudo bash run.sh prepare
)
```

`HOME_EVIDENCE=`의 압축/동일 경로 sha256는 기존 로그인 홈에 생성된다. 새 PASS_PREPARE 검증과 관리 호스트의 이전 Runner 목록 부재 확인 후 새 단기 토큰으로 등록·제거 검사를 진행한다. 토큰 JSON은 증적 제출 대상이 아니다.

아래는 ansible01 기존 관리 로그인에서 실행할 읽기 전용 잔존 조회다. 전체 페이지를 읽고 이번 이름만 표시하며 원본 출력은 홈의 새 파일에 기록한다. gh 실패 시 조회 실패로 취급한다. 일치 행이 있으면 자동 삭제/재등록하지 않고 해당 ID/name을 대조한다.

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

`query_rc=0`이고 일치 객체가 없어야 이번 이름이 조회 시점에 없다는 근거다. 실제 새 Runner 등록/제거, Actions 활성화·정상/결함 CI, 독립 리뷰/승인, merge, 운영 적용 및 Issue5 AC는 아직 완료하지 않는다. 코드/증적 PR은 Draft를 유지한다.

공식 근거: [Runner 설정 저장](https://github.com/actions/runner/blob/v2.337.0/src/Runner.Common/ConfigurationStore.cs), [UTF-8 파일 쓰기](https://github.com/actions/runner/blob/v2.337.0/src/Runner.Sdk/Util/IOUtil.cs), [Python utf-8-sig](https://docs.python.org/3/library/codecs.html#encodings.utf_8_sig).
