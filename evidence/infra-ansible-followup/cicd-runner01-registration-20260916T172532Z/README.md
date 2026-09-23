# cicd-runner01 v1.2 registration-check PASS

제출 원본 SHA256: `7b8906a94ad5a4b23ae8a1d32cc307160311ea90cf17cad70623898384d1a0b7` (6206 bytes).
원본 tar.gz와 sidecar를 그대로 보존했으며 외부 해시·중첩 archive 해시·양쪽 내부 manifest 및 파일 집합을 검증했다.
외부 17파일, 내부 10파일. 외부 복제 HOST_RUN_RESULT와 내부 원문이 동일하다.

## 실제 서버 실행 결과

- 실행 UTC: 2026-09-16 17:25:32.986067–17:25:58.310814.
- HOME / HOST / CONTAINER 모두 PASS_REGISTRATION_CHECK. configure_rc=0, remove_rc=0.
- 저장소: 321Team/infra-ansible.
- Runner ID: 3 / 이름: ansible-ci-f9e3ef4d85e44573891eaebcaffd5b1d.
- UTF-8 BOM=true, JSON 파싱 및 URL/name/id 검사 모두 통과. v1.2 수정의 실제 실행 확인이다.
- 격리 14/14, rootless Podman / SELinux Enforcing / cgroupv2, 컨테이너 exit0 / OOM=false.
- runner/proxy/workspace 모두 REMOVED. host diagnostic_errors 없음.
- bundle: `5c0e851db396689ca6549562f2a442cd5a6e6b58d2d30dd0f99d5f3338dc3bfe`.
- image: `sha256:02d097ce453f4011218a081286e02be2c4d64599d1b329d6d98e049b9c34fd85`.

원본의 PASS는 등록/제거 검사 범위다. 실제 Actions는 NOT_RUN이며 운영 apply/엔진 전환은 false다.
관리 API에서 **이번 ID 3 또는 이름**의 목록 부재를 확인하는 증적은 아직 없다.
이전 이름의 부재 증적을 이번 항목에 전용하지 않는다.
최신 토큰 발급 증적은 이 업로드에 포함되지 않았으므로 새 API POST 상태를 주장하지 않는다.

## 홈 경로 사고와 방어코드

사용자가 홈 접근 복구 후 재수행했다고 보고했다. 사고 당시 실제 홈 mode나 데이터 삭제는 독립 관측하지 않았다.
앞선 입력 경로 무조건 chmod 안내는 철회한다. 디렉터리 search 권한을 잃을 수 있는 안내 결함으로 검토했다.

[방어 도구 소스 및 운영 절차](https://github.com/321Team/infra-ansible/tree/2fae52a9e09e33b8c8bff6c653b8533d8b52dc47/tools/ansible-runner-input).
코드 작성 전에 별도 DEEP_REVIEW 커밋을 기록했다.
홈/디렉터리/링크/특수 파일·소유자·경로·packet 검사 뒤 동일 FD에만 fchmod한다.
증적은 기존 로그인 홈에 생성하며 토큰과 원시 예외를 보존하지 않는다.

- 신규 방어 도구 로컬 회귀: **20/20 PASS**, 실제 로그/rc를 input-guard-local에 보존.
- 초기 일시적인 작업 환경 오프라인은 복구됐으며 최종 파일에 대한 시험을 실행했다.
- 기존 Runner 24파일과 admin-token 11파일의 Git blob 일치 확인. 기존 전체 93파일 보존.
- 신규 보호 도구의 실제 서버 실행은 NOT_RUN이다. 위 실제 Runner PASS는 보호 도구 추가 전 실행이다.
- 배포 ZIP: 16465 bytes, SHA256 `19c916f826a3ff0178f07f3b1a2b0b62f9359902f73196cadf330a08b070f34d`.
- 독립 승인·merge·Workflow 활성화·실제 Actions 정상/고의 결함 실행은 별도 미완료다.

지금은 보호 도구를 위해 재등록을 반복하지 않는다.
위 운영 절차 README의 읽기 전용 관리 API 목록 확인을 ansible01에서 실행하고 홈의 결과/sidecar를 제출한다.

