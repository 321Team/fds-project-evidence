# 새 Deploy 실제 결과 — Run38412128227/Attempt1

이권욱 / CODEX_ASSISTED. GitHub actual Job **2026-10-13T23:17:52+09:00 ~ 2026-10-13T23:19:25+09:00**, conclusion **success**. 원본을 보존한 판정은 **DEPLOY_AND_POD_DIGEST_READY_VERIFIED**이다.

- [사전검증 Run38411968657](https://github.com/321Team/infra-cicd/actions/runs/38411968657) → [실제 Deploy Run38412128227](https://github.com/321Team/infra-cicd/actions/runs/38412128227). 사용자 승인 false1회/true1회는 이 회차로 소진했고 자동 재실행은 하지 않았다.
- 대상 source `147f760298dd4a683ea58f2a887483769352b97d`, plan `ed7787673f5b8f8f1f97e49e78a9359ec1c09f8835acda19cc93d7e130ee2ad4`, record `fb8b603e6e9ee4449767d74a5d22fb864c1ef7a0a11d75e1eef0c3144d1c58db`. 새 Push38404449622/TBS38395350748/APP affbc69에 연결한다.
- [사용자 정확 승인 원문](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6147190360), [독립 입력 리뷰](https://github.com/321Team/fds-project-evidence/pull/219#pullrequestreview-5504707659). 승인된23:15~23:25 KST 실제 시작/00:15 종료 조건을 실제 Job 시각과 대조했다.
- Session `EXECUTION_RETURNED`, ROLLOUT `READY`, ROLLBACK `NOT_EXECUTED`, error `NONE`. broker 완료와 rollout 판정을 분리했다.
- 원본 Runner 위치 `/home/server01_cicd-runner/FDS_CICD_Deploy.id4l3iwm`, result SHA256 `c700fd0ba6d8d865a1a77d0979d93c0ba8ff79368a478091670d3ba8302b4719`. false/true actual Run/Job 원본·로그, Runner receipt/claim/checkpoint, 전후 metadata, 공급·broker 명령/rc/hash를 함께 보존했다. 로그는 ANSI/CRLF 원래 bytes를 파일로 수신했으며 터미널 보호 예외를 원격 통제 완화로 해석하지 않는다.
- 지속 claim/checkpoint 파일 9개 보존, checkpoint `CLOSED`, socket 부재 `True`, Runner Worker 0. 토큰 원문/환경/개인키/Secret을 수집하지 않았다. credential의 실제 발급·status 만료·정리 범위는 `final/VERIFIED_RESULT.json`에 있으며 server 강제 revoke는 수행하지 않았다.
- 공급 시 두 전송은 rc0/hash 일치였지만 로컬 확인기가 `stat`의 영문 형식명을 기대해 한국어 출력에서 멈췄다. 기존 파일을 재전송·덮어쓰지 않고 archive+13파일 및 record의 숫자 stat/권한/해시를 순수 읽기로 재확인해 통과했다. 그 중단·readback 원본도 보존하며 Workflow 재실행이나 새 Token 회차로 소비하지 않았다.

## 실제 사후 대상

```json
{
  "transaction-api": {
    "image": "10.1.93.54/fds/transaction-api@sha256:338b8a2871507ce8b42deedc916b26e350577ee6efd18df23d7ff2dd4b17dff0",
    "uid": "8a2af808-ec33-41f2-80b5-addde4e28910",
    "generation": 12,
    "ready": 3,
    "pod_uids": [
      "4d0b362b-5081-4745-b68a-85636e08dc10",
      "da814b7b-1a35-4ce9-8719-eedee3d7936d",
      "9d34d371-5839-429b-b255-a9a4a6ebdd31"
    ],
    "nodes": [
      "k8s-worker03",
      "k8s-worker02",
      "k8s-worker01"
    ],
    "restart_counts": [
      0,
      0,
      0
    ],
    "endpoint_count": 3
  },
  "fds-engine": {
    "image": "10.1.93.54/fds/fds-engine@sha256:8b257adb08b6d381f72b66d3386efea6112a8f072ecfafcbcd463bcd1c3be89d",
    "uid": "bf825dec-465b-4603-8b71-f768d195531c",
    "generation": 6,
    "ready": 3,
    "pod_uids": [
      "533caef6-e244-451a-96d1-8d4de9f40983",
      "1b2f1c14-a04f-438c-b051-4d65a0a8a8e7",
      "4ab7c0a7-c7aa-4f0c-9a63-642a752dbe51"
    ],
    "nodes": [
      "k8s-worker02",
      "k8s-worker03",
      "k8s-worker01"
    ],
    "restart_counts": [
      0,
      0,
      0
    ],
    "endpoint_count": 3
  }
}
```

## 판정 경계와 다음 순서

사후 Deployment/Pod imageID·Ready·Endpoint 확인 범위만 판정한다. 전체 HTTP·업무 E2E, 새로운 HA/Probe 장애, 최종 앱 회귀·DB 인수는 이 회차에서 수행하지 않았다. 기존 DB#11의 “최종 앱 회귀 후 판단”, W4 전체 HTTP5xx NOT_MEASURED를 유지한다. 기존 실패·복귀 이력과 이전 claim도 보존한다.

기존 정확 입력 승인을 이 새 Runtime 증적 편입 승인으로 확대하지 않는다. 새 HEAD의 독립 증적 검토와 병합은 별도다. 성공 판정이면 최종 형상을 기반으로 최소 HA/복귀 → 최종 APP 회귀 → DB 판단을 준비한다. 실패/불명 판정이면 추가 변경을 중단하고 actual 결과와 현재 상태를 먼저 대조한다. 같은 plan·token·claim으로 자동 재실행하지 않는다.
