# AI 도구 작업 규칙 — fds-project-evidence

이 저장소에서 작업하는 모든 AI 도구가 따르는 규칙이다. 대상은 Claude(Claude Code), GPT(ChatGPT·Codex), Grok, Cursor 등이다. 정책 원문이 우선한다.

- GitHub 텍스트 쓰기: [baseline TICKET_SYNC_POLICY 1.3 §5.1](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/governance/TICKET_SYNC_POLICY.md#51-issue-본문-쓰기와-ai-도구-수동-편집-포함) · [baseline AGENTS.md](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/AGENTS.md) (baseline PR #107)
- 증적 편입: [증적 관리 규칙](governance/EVIDENCE_POLICY.md)

## GitHub Issue·Milestone 텍스트 쓰기

§5.1은 쓰기 경로를 가리지 않는다. GitHub MCP·커넥터, 도구가 대신 실행하는 `gh`/API, 에이전트 모드의 브라우저 조작이 모두 해당한다. baseline Issue·Milestone은 §5.1을 그대로 따른다. 이 저장소의 Issue(예: 후속 이슈 #4)에도 같은 기준을 적용한다. 손상이 대상 저장소가 아니라 쓰기 경로에서 일어났기 때문이다.

### 금지 — 본문·설명 직접 수정

- Issue 본문 전체 재작성
- 절·문단·표의 추가·삭제·수정
- 링크·관리 마커(`<!-- … -->`)·보관 원문 편집
- Milestone 설명 편집(요청에 설명 텍스트를 넣는 것 포함)

이런 변경은 교체 본문 파일(UTF-8, LF)과 plan으로 넘긴다. plan에는 `number`, 직전 재조회 `updated_at`, 변경 전 본문 SHA-256(LF), 파일 SHA-256을 적는다. 반영은 담당자가 로컬 `gh`로 직접 실행한다. Milestone 설명은 사람이 웹 UI에서 편집한다.
- baseline Issue: baseline의 audit 경로에 준비한다.
- 이 저장소 Issue: `records/` 아래 새 폴더에 준비한다(증적 관리 규칙의 '안내·정정·보완 문서' 경로).

### 허용 — 대상 줄만 치환

대상:
- baseline Issue 상단 필수 속성표(17개)의 값
- AC·Exit Criteria 등 체크리스트의 체크 상태(`[ ]`↔`[x]`)
- 잔여 항목 표기

이 저장소 Issue에는 필수 속성표가 없으므로 체크 상태와 잔여 항목 표기만 해당한다.

조건(모두 지킨다):
1. **대상 줄만 문자열 치환한다.** 조회한 원문에서 해당 줄만 바꿔 올린다. 본문 전체를 다시 출력해 쓰지 않는다.
2. **쓰기 직전에 `updated_at`을 다시 확인한다.**
3. **쓰기 뒤에 재조회한다.** 바뀐 줄 외 차이 0, 손상 신호(`&lt;`·`&gt;`·단독 ``` `` ```·footer) 증가 0을 확인한다. 어긋나면 즉시 멈추고 코멘트로 보고한다.
4. **근거를 코멘트로 남긴다.** 바꾼 항목, 전→후 값, 근거 링크, AI 사용 표기를 적는다.
5. **재조회 대조를 할 수 없는 도구는 쓰지 않는다.** 예를 들어 웹 채팅이 해당한다. 이런 도구는 변경안을 코멘트로 남긴다.

### 값만 바꾸는 변경

Milestone 기한, Issue 날짜 필드(Start date·Target date)처럼 텍스트 없이 값만 보내는 변경은 허용한다.
- 요청에 텍스트 필드를 넣지 않는다.
- 쓰기 직전에 현재 값과 `updated_at`을 확인한다.
- 쓰기 뒤에 재조회해 다른 필드가 바이트 그대로인지 확인한다.
- 전후 값을 기록한다.

### 항상 허용

- 읽기 전용 조회와 대조: 필수 속성 누락, AC 잔여 항목, 증적 연결 점검
- 교체 본문과 plan 준비
- Issue 코멘트와 PR 본문(AI 사용 표기 포함). Claude 세션 경로는 끝에 footer를 붙일 수 있다.

### 판단 권한

Status·AC 인수·종결은 담당 Lead가 결정한다. AI 도구는 결정과 근거를 반영할 뿐이며, 스스로 충족을 판정하지 않는다. 증적 PR의 독립 검토·병합만으로 업무 티켓을 Done 처리하지 않는다([증적 관리 규칙](governance/EVIDENCE_POLICY.md) '단계 구분').

## 증적 편입 작업

[증적 관리 규칙](governance/EVIDENCE_POLICY.md)을 따른다. AI 도구가 특히 어기기 쉬운 항목은 다음과 같다.

- 이미 병합된 `evidence/` 파일을 변경·삭제하지 않는다. 병합된 수집회차 폴더에 파일을 추가하지 않는다. 정정·보완은 새 경로에 쓴다.
- 수신 파일은 바이트 그대로 둔다. 줄바꿈·따옴표·인코딩을 정규화하지 않고, 압축 파일을 재압축하지 않는다.
- 수신 원본과 과거 문서에 적힌 서버 경로·논리 경로는 출처 정보이므로 고치지 않는다.
- 로컬에서 만든 Manifest·해시 일치를 과거 서버 검증, 시험 PASS, 승인으로 표시하지 않는다.
- 비밀키·토큰·암호·실제 credential이 든 파일을 커밋하지 않는다.
- 관리 문서를 바꾸면 `REGISTRY_SHA256SUMS`를 같은 PR에서 갱신하고, `python3 tools/check-evidence-layout.py --base origin/main` 결과를 PR에 적는다.
- 병합은 독립 검토 뒤 이권욱이 검토 Commit을 확인해 수행한다. AI 도구는 PR을 승인·병합하지 않는다.

## 문제 사례

2026-09-22~26 baseline #74·#75·#9·#7·#11·#16·#35와 Milestone #5가 AI 세션 경로의 쓰기로 손상됐다. 유형은 HTML 엔티티화, 링크 앞뒤 ``` `` ``` 삽입, 둥근 따옴표 변환, footer 추가다. 수정 대상이 아닌 줄과 보관 원문까지 바뀌었다. 상세와 전후 예시는 [baseline AGENTS.md](https://github.com/321Team/fds-project-baseline/blob/b2e78d9dd2bb5d5084ffce531f43ccdcaa5fb4d2/AGENTS.md) '문제 사례'에 있다.

- 도구의 성공 응답은 본문이 보존됐다는 증거가 아니다. 재조회해서 대조해야 알 수 있다.
- 손상 조건은 확인되지 않았다. "이번에는 괜찮았다"를 근거로 삼지 않는다.
