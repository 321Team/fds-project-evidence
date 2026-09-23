# ansible01 관리 토큰 발급 재검증 — PASS_TOKEN_PACKET

## 판정

사용자 제출 실서버 증적에서 등록·제거 토큰 발급이 모두 HTTP 201로 성공했다. 사용자 보고의 repository-level self-hosted runners 허용 변경 후, 이전 실행의 등록 토큰 POST 403 차단이 이번 재실행에서는 해소됐음을 확인한다. 원본 압축/sidecar, 내부 manifest와 정확한 파일 집합, 배포 도구 v1.1.1의 코드 해시가 일치한다.

- 실행: 2026-09-16 15:44:40.712811–15:44:44.926583 UTC (2026-09-17 00:44:40–00:44:44 KST).
- 저장소: `321Team/infra-ansible`; 도구: `admin-token-v1.1.1`.
- UID1000/예상 호스트 확인, memory protection, gh 발견, 저장소 조회, 두 토큰 발급, packet 검증/쓰기: 8단계 모두 PASS.
- 저장소 GET: HTTP200, admin=true. registration token POST: HTTP201. removal token POST: HTTP201.
- packet 검증 당시 남은 시간: 등록 3599.449초, 제거 3599.889초.
- `packet_written=true`, `token_post_attempted=true`, `runner_registration_attempted=false`, `actions_executed=false`.
- 원본 SHA256: `b3bf12ea75e60a3292a76913e614c54e00a4af39282c024bfede38de63837e00` (799 bytes).
- 관리 도구 `admin-token.py`: `0c4ee7d9ad3e3d21998ffcbf25f61e08e9482ae6af159762713ad7895719670c`.
- `common.py`: `1cf7cbc14b3a861a74d7eb014ad13495dd4781ef186a9c7e00c9e43a62af0811`.

토큰 원문/packet은 제출받지 않았고 이 증적에 포함되지 않는다. `RESULT.json`은 압축 내 `evidence/RESULT.json`의 원본 바이트다. 다운로드 중 추가된 `(1)` 이름만 정규화했고 압축 원본은 변경하지 않았다.

## 다음 실행: cicd-runner01 등록 후 제거 검사

검토 결과 기존 Runner v1.1과 검증된 PREPARED 영수증을 그대로 사용할 수 있다. 실행 코드 변경은 필요하지 않다. 관리 도구 v1.1.2 진단 후보는 배포하지 않는다.

ansible01의 `TOKEN_PACKET=` 파일만 승인된 비공개 파일 전송 경로로 cicd-runner01 기존 로그인 홈에 전달한다. 패킷 내용을 출력하거나 증적에 첨부하지 않는다. 아래 명령은 이번 화면의 파일명을 기준으로 한다. 재발급했다면 새 출력 파일명을 사용한다. 양쪽 토큰에 최소 10분이 남아 있어야 하므로 전송 후 바로 실행한다. 시간이 지난 경우 기존 v1.1.1 관리 도구로 새 packet을 발급한다.

```bash
(
set -euo pipefail
cd "$HOME/FDS_Ansible_Actions_Runner_v1_1"
sha256sum -c SHA256SUMS
TASK_TOKEN_PATH="$HOME/ansible-runner-token-m0b3cyfd.json"
chmod 600 -- "$TASK_TOKEN_PATH"
sudo bash run.sh registration-check \
  --prepared /home/ansible-verify/ansible-actions-a1a17a5e782944ab924a6af14fae7a52/evidence/PREPARED.json \
  --token-file "$TASK_TOKEN_PATH"
)
```

기존 준비 이미지 ID는 `sha256:104b262f24146c8cb5068f8e577bff0ed438bd7941ff1a43ab74a04dc735573f`, bundle manifest는 `ecff16d871d7b08cd9aa72e580e54830b61d438ec9dcbbf3847bbac2f690ff46`이다. 실행기는 이 결합과 현재 계정·격리를 다시 검사한다. 영수증을 복제하거나 수정하지 않는다.

예상 상태는 `PASS_REGISTRATION_CHECK`다. 이 모드는 새 고유 이름으로 등록한 뒤 즉시 제거하며 Listener/job을 시작하지 않는다. 성공/실패 모두 기존 로그인 홈의 `HOME_EVIDENCE=` 압축과 같은 경로의 `.sha256`를 제출한다. 실제 생성된 Runner ID/name을 결과로 식별한 후 관리 호스트에서도 API 목록에서 사라졌는지 대조해야 한다. 기존 infra-cicd Runner ID2는 이 검사의 정리 대상이 아니다.

## 완료 범위

이번 입력은 실제 관리 API의 단기 토큰 발급 성공 증거다. Runner 등록/제거 검사는 아직 실행 증적이 없고, Actions 활성화·정상/고의 결함 CI·최신 HEAD 독립 승인·병합·운영 적용·Issue5 Acceptance 완료도 아직 아니다. 코드 PR19 HEAD `52271b7fafd5f442cf5540978b8c5df74bf352de`와 Draft 상태를 유지한다.

앞선 HTTP403과 정책 선택 증적은 각 시점의 이력으로 보존한다. 이번 성공은 이전 응답에서 누락된 상세 오류 메시지를 복원하거나 원인을 소급 확정하는 자료는 아니다.
