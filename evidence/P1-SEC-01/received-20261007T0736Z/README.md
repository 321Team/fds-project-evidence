# P1-SEC-01 — LimitRange 3개 Namespace 적용 상태 콘솔 출력 (2026-10-07)

Record ID: **P1-SEC-01** ([baseline #19](https://github.com/321Team/fds-project-baseline/issues/19)). v3.2 인계 §4 "LimitRange 근거"(적용 증적이 `monitoring-api` 1개뿐이었음)를 보완하는 읽기 전용 조회 결과다. **이 폴더는 AC 판정이나 LimitRange 요구 충족을 주장하지 않는다.** 판정은 Review Owner 몫이다.

## 출처와 수신
| 항목 | 값 |
|---|---|
| 파일 | `limitrange-20261007.txt` (1453 B), SHA-256 `57699e14605421fe5c88fc8084d26dd6e62d08b27bf52147f1e7ca31bb757d42` |
| 성격 | **콘솔 출력을 `tee`로 저장한 파일**이다. 서버가 생성한 증적 파일이 아니며, 첫 줄에 `[sudo] server02 암호:` 프롬프트가 섞여 있다(암호 값은 없음). |
| 실행 | ansible01에서 `get limitrange -A`, `describe limitrange -A` (이하영, 읽기 전용, 변경 없음) |
| 전달 | zip(`limitrange-20261007.zip`)으로 공유 폴더에 올림 → 세션에서 압축 해제 → 해시 계산 |
| 수신 | 2026-10-07 16:3x KST |

## 관측값 (판정 아님)
세 LimitRange의 생성 시각은 모두 `2026-09-22T00:17:38Z`이고 type은 `Container`, Min/Max/ratio는 설정 없음(`-`)이다.

| Namespace | 이름 | Default Request (cpu/mem) | Default Limit (cpu/mem) | 정의 파일 값 | 일치 |
|---|---|---|---|---|---|
| fds-app | fds-app-default-limits | 250m / 256Mi | 500m / 512Mi | 250m·256Mi / 500m·512Mi | 예 |
| monitoring-api | monitoring-api-default-limits | 200m / 256Mi | 500m / 512Mi | 200m·256Mi / 500m·512Mi | 예 |
| monitoring-node | monitoring-node-default-limits | 50m / 64Mi | 100m / 128Mi | 50m·64Mi / 100m·128Mi | 예 |

정의 파일: `infra-kubernetes` `manifests/05-limitrange.yaml`(origin/main `9785627` 기준으로 대조).

## 검증
- 파일의 비밀정보 패턴(`password|secret=|token=|BEGIN … KEY|bearer|authorization:`) 일치 0건. 프롬프트 줄의 `암호:`는 문구일 뿐 값이 없다.
- 업로드된 zip을 풀어 얻은 txt의 SHA-256을 위 값과 대조했다.

## 한계 (은닉 아님)
1. 콘솔 출력 저장본이라 서버 측 해시·봉인·수집 시각 기록이 없다. 조회 시각은 파일에 없고, 생성 시각(09-22)만 있다.
2. 현재 시점 한 번의 조회이며 이 값이 09-22 이후 계속 같았다는 증명이 아니다.
3. LimitRange는 **기본값(default) 안전망**이며 명시적 resources의 대체가 아니다(정의 파일 주석). 기본값이 실제 Pod에 적용된 관측은 이 폴더에 없다.
4. 정의 파일 대조는 사람이 값을 눈으로 비교한 것이다.

## AC와의 대응 (판정이 아니라 연결)
| #19 항목 | 관련 파일 |
|---|---|
| D-SEC-01 §5(Resource) LimitRange 적용 상태 | `limitrange-20261007.txt` |

AI usage: CLAUDE_ASSISTED (수신 검증·대조·정리 보조). 판단은 이하영.
