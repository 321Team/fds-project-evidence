# AC09 이전 Digest 복구·현행 복원 — 2026-10-15

**Runtime·HTTP/계측·DB 사후 대조·SEC 조건 판정 및 Lead의 AC09 한정 결과 수용 완료. 이 증적 편입 후보 자체의 독립 리뷰·CI·병합과 AC10/전체 Delivery 종결은 별개로 남아 있다.** CODEX_ASSISTED.

- 실제 [Runtime 결과](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186586952), [DB 보완](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6186849803), 이하영 [SEC 사후 판정](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6187360015), 이권욱 [17:11:50 AC09 결과 수용](https://github.com/321Team/infra-cicd/issues/11#issuecomment-6187579176).
- Runtime 소스 `fddc76e1c261cd938f06211b7ed035fdcb32e606`, 기존 Runner #2. false Run `38693789875`·`38693851363`, true R1 `38693979785`·R2 `38694721511`, 모두 Attempt1·Job1개·success. TokenRequest2·입금POST2·추가edgeGET4, 새Runner·재dispatch·재POST·수동복구0.
- R1은 승인된 이전 두 digest로 명시적 복구, R2는 현행 두 digest로 복원했다. 각 단계 Ready3×2·HTTP201·FDS 정상·동일 Pod 저장/평가 +1·오류0. 동일 거래 ID DB 각1행과 공통10필드 일치. 최종 현행Pod6·이전Pod0·재시작0, 임시 공급 회수 및16:06:17 작업창 반환.

## 원본 구성과 재현

| 위치 | 내용 |
|---|---|
| [runtime/EVIDENCE_MANIFEST.json](runtime/EVIDENCE_MANIFEST.json) | 봉인된446파일과 외부61개 기준/추가원본의 기존 인덱스. SHA `e5b950818d03ca73adc0bc56d98dc1a083e69853183a2c908fcd7bab516d185a` 불변 |
| `runtime/` | 그446파일+기존 manifest/seal 2개를 원 bytes로 복사. claim/checkpoint 원mtime·Run/Jobs/로그·HTTP body·계수·전후시계·정리/반환 포함 |
| [EXTERNAL_ORIGINAL_INDEX.json](EXTERNAL_ORIGINAL_INDEX.json), `external/` | 원 인덱스의 외부61개를 원 SHA대로 복사. 긴 로컬 출처 경로는 매핑에서 보존 |
| `app-runtime/`, `app-db/`, `db-central/` | APP 별도 HTTP/계수 대조와 사용자 db01 READ ONLY 콘솔 원문·고정SQL·재구성파일·중앙/APP 검증. 재구성은 콘솔 전달 LF bytes에 대한 대조이며 새 원격 조회가 아님 |
| `references/sec-post.json`, `references/lead-acceptance.json` | 실제 GitHub SEC·Lead 판정 원문. 작성자·게시 시각·링크 포함 |
| [COPY_PROVENANCE.json](COPY_PROVENANCE.json) | 복사한 각 파일의 출처·대상·bytes·SHA. 원본을 정규화하거나 이전 내용에 사후 승인을 삽입하지 않음 |
| [STATE_LAYERS.json](STATE_LAYERS.json) | 원본 기술판정과 후속 업무/위험 수용, 이 PR 편입 상태 구분 |
| [verify.py](verify.py), [LOCAL_VALIDATION.json](LOCAL_VALIDATION.json) | 네트워크 없이 봉인/복사 SHA, 승인/Run/journal, 두 실제 API→DB 행, 수량·복원·SEC 출처, JSON/base64/압축 내부 민감정보 패턴 확인 |

로컬 실행: 이 폴더에서 `python -B verify.py`. 저장소에서는 `python tools/check-evidence-layout.py --base origin/main`, `python -m unittest discover -s tests -q`를 수행한다. 원본 소스 사본은 증적으로 읽는 것이며 이 패키지에서 배포/수집 스크립트를 실행하지 않는다. 폴더 `SHA256SUMS`와 루트 `REGISTRY_SHA256SUMS`를 함께 확인한다. 압축6개는 각각1MiB 이하의 원 bytes·sidecar 및 `registry/ARCHIVE_CONTENTS.json` 내부파일 목록으로 연결했다.

## 판정 경계와 알려진 제한

- 원본의 정확 PATCH 시각 `NOT_MEASURED`, 엄격한 회차 전체 E_host 상한 `UNPROVEN`은 그대로다. 원시 구간 차이371.114초/500.490초와 관측 시점 오차0.0027~0.0721초 등에 대해 **SEC가15/30분 및 위험조건 충족·사고 아님·단회수용 종료로 판단했다.** 수학적 입증 결과를 고친 것이 아니다.
- `runtime/`·APP의 과거 파일에 DB 미수집/SEC 대기/인수 미완료가 남아 있는 것은 당시 사실이다. 위 후속 원문과 STATE_LAYERS가 현재 판단을 보완한다. 원 봉인 내용을 최신 표현으로 덮지 않는다.
- DB 사전0행은 미수집·소급 미입증이다. 채택된 최종 승인 카드는 동일 ID 사후 대조를 요구하며 그 범위는 충족했다. 정상 deposit 각1건을 모든 Rule·이력조회·외부 Client 경로로 확대하지 않는다.
- 일부 공통 transport 원본 receipt의 `PURE_READ_PRECHECK` 및 `NOT PERFORMED (Pre-check)`는 arbitrary payload 의미를 판정하지 못한 고정 오표기다. 실제 POST body/method/201에 따라 거래 쓰기2건으로 계상한다. 코드의 실제 리뷰·승인은 별도 source/PR/카드/Run으로 확인하며 이 receipt 문자열을 근거로 축소하지 않는다. 다음 회차용 최소 수정안은 별도 로컬 후보이며 본 원본에 적용하지 않았다.
- 이번 명시적 이전 복구를 실패 후 자동보상·별도 수동복구 또는 모든 경쟁 상황의 신규 Runtime 음성시험으로 확대하지 않는다. 단회 plan claim·배타 mutex·Workflow concurrency는 검토된 코드와 실제 claim/순차 회차로 연결한다.
- 토큰 값·개인키·암호·kubeconfig 실제 자격증명은 편입 대상이 아니다. 토큰 명시 만료·논리 참조 종료는 확인했지만 강제 revocation·만료 후 인증시험·전 디스크/물리메모리 무잔존은 이번 결과가 아니다.
- 내부주소/호스트/합성 거래 데이터는 승인된 팀 증적 저장소 안의 검토 정보다. “공개 가능한 증적”은 자격증명을 제외했다는 뜻이며 저장소를 인터넷 공개로 전환하는 권한이 아니다. 패턴 검사는 발견 가능한 형태에 한정되고 독립 민감정보 검토를 대신하지 않는다.

## 편입 상태

Lead의 AC09 자체 수용은 [현행 정책 §4](https://github.com/321Team/fds-project-baseline/blob/a47ac7543b18b557707453fe708e8e225d916db6/governance/REVIEW_AUTHORITY_POLICY.md)에 따른다. 이 후보의 증적 저장소 편입은 §3.1의 정확 HEAD 독립 리뷰·필수 검사·Lead 수동 병합을 별도로 거쳐야 한다. 여기서는 새 PR 생성·리뷰 요청·서버 작업·추가 Run/Token/POST를 하지 않았다. AC10·복합 Delivery 및 전체 티켓 종결은 이 편입만으로 완료되지 않는다.
