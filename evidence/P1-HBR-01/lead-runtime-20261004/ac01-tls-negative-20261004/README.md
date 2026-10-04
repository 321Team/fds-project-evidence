# AC-01 TLS Negative — 복구 이후 재실행 (2026-10-04 18:54:45 KST)

- 수행: 이하영 / cicd-runner01 / 계정 `server01_cicd-runner`. 병합·리뷰된 `infra-harbor-trivy scripts/verify/tls-negative-test.sh`(sha256 `81b0c2c83ebf01267bfe15bec0114481aa4d72346a59e80dae52791e4092592d`)를 해시 확인 후 그대로 실행. 수정 없음.
- 입력: 올바른 CA = Runner Podman trust `~/.config/containers/certs.d/10.1.93.54/ca.crt`(sha256 `20ddfa5e…053f`), 잘못된 CA = OS 기본 `/etc/pki/tls/certs/ca-bundle.crt`(Harbor Root CA 미포함).
- 결과: 올바른 CA로 `/api/v2.0/health` 성공(구성요소 8개 healthy), 잘못된 CA는 curl Exit Code 60으로 거부, `SCRIPT_RC=0`.
- 서버 원본 `~/ac01-tls-negative-20261004T185445.txt`: 1004 bytes, sha256 `0fcf5fb23f67c12f79726f4f9cc7dda4486a1fe1f45dda3e97e266096374e306`. curl 진행 표시의 CR(`\r`)이 포함돼 있어 서버에서 `tr '\r' '\n'`으로 만든 정리본 `….txt.lf`(sha256 `1a2a100b72fbcb7ff3fb561821a2e5de8f1d7678b089edab0fe0a34e72702e05`)를 PC로 옮겼다. 이 폴더의 `.lf`가 그 정리본이며 해시는 서버 값과 일치한다. 원본(CR 포함) 파일은 PC에 없다.
- 한계: 이 시험은 Runner 한 곳에서 `/api/v2.0/health`에 대해 수행했다. Worker 등 다른 consumer의 trust와 AC-04 Source 제한은 별도다. 복구 전(2026-09-30) 시험은 별도 회차(`received-20260930T040033Z`)이며 이 결과로 대체하지 않는다.
