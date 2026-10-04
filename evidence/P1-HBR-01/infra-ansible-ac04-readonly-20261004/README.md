# P1-HBR-01 AC04 —2026-10-04 읽기 전용 원본 편입

상태: 수신·자체 검수 완료 / 독립 리뷰·편입 병합 PENDING. Phase1만 해당.

## 범위와 출처

ansible01/server01_ansible에서 기존 svc_ansible 경로로 harbor01을 수집한3회차입니다.
사용자가 원본 tar.gz와 sidecar를 제출했고, 원본 archive 해시·내부116개 manifest 항목을 확인했습니다.
raw/의119개 파일은 압축에서 추출한 원본 그대로입니다. collector/에는 실제 배포한3개 v1.0 kit 파일24개를 그대로 보존했습니다.
각 raw와 collector의 원래 SHA256SUMS를 유지합니다. README와 RECEIPT.json은 편입용 신규 기록입니다.
압축 원본 3개를 `archives/`에 수신 바이트 그대로 추가 보존했습니다(재압축 없음). 각 `.sha256` sidecar와 `registry/ARCHIVE_CONTENTS.json` 내부 목록을 함께 등록했습니다. 원 첨부 식별자·수신시각·바이트 수·해시는 RECEIPT.json에 유지하고 저장소 경로를 추가했습니다.

- [지원 작업 및 검수 이력](https://github.com/321Team/infra-ansible/issues/62)
- [검토 대상 문서 PR67](https://github.com/321Team/infra-ansible/pull/67)
- [운영 코드 PR63](https://github.com/321Team/infra-ansible/pull/63)
- [상위 HBR 티켓](https://github.com/321Team/fds-project-baseline/issues/13)

## 소스/실행/리뷰 범위

운영 source는 badbe29440916ec3ec79da8fc81722c2e6c4e75b로 동일합니다. 해당 repository code는10/4 08:59 KST HBR Lead APPROVED 기록이 있지만 적용 승인은 아닙니다.
별도 Python/supplemental 수집 도구는 assistant STATIC/MOCK 검증만 수행했고 **REVIEW=NOT PERFORMED (Pre-check)**입니다. 원본 playbook 코드 승인을 수집 도구에 승계하지 않습니다.
이 편입 역시 작성자/AI 자체 검수이며 독립 리뷰 완료가 아닙니다.

| 회차 | 실제 실행 | 현재 판정 |
|---|---|---|
| preapply |14:14:55–14:15:26 KST; discovery27/precheck47/surface3; changed0|기존 baseline 및 네트워크 관측 완료|
| path-loader |14:45:54–14:45:57 KST; surface3; changed0|docker-proxy IPv6→IPv4 경로, ens160 disable_ipv6=1, nft loader 관측|
| ipv6-config |15:15:46–15:15:50 KST; surface3; changed0|활성 UUID와 저장 profile의 ipv6.method=disabled 일치|

모든 회차 source/command/rc/stdout/stderr/result/manifest를 포함합니다. 정상 수집 marker는 운영 승인·AC PASS가 아닙니다.
실제 Apply·traffic·Docker restart persistence·VM reboot/reconnect는 미수행입니다.
clients/임시 예외/UI fallback/변경창 및 loader 운영 조건 수용은 미확정입니다.

## 검증과 제한

- raw116 manifest entries 및 collector21 manifest entries 해시 일치. 원본119개/도구24개 UTF-8 byte roundtrip 확인.
- Private key PEM, GitHub token, Authorization Bearer/Basic 패턴 검사에서 매칭0건. 전체 비밀정보 부재 인증을 뜻하지 않으며 독립 검토가 필요합니다.
- 내부 IP/MAC/host/account/로컬 파일 경로는 운영 증거로 남아 있습니다. 접근 권한 변경 없음.
- 새 수집회차 경로만 추가하고 기존 evidence 파일을 변경·삭제하지 않습니다.
- 전체 `python3 tools/check-evidence-layout.py --base origin/main` 및 repository tests는 CI에서 확인합니다. PR 생성 시점 전체 검사 PENDING; 지역 hash 검사를 전체 저장소 PASS로 표시하지 않습니다.
- 서명/서버 원본 진위·실행자 독립 확인·Lead 인수는 해시 일치만으로 판정하지 않습니다.

## 리뷰할 부분

1. 원본 출처·manifest 및 수신 bytes 대응, collector/source 승인 범위 구분.
2. 세 회차 관측이 문서 PR67과 일치하는지 및 미실행/미승인 표시.
3. 민감정보·누락·대장 연결·새 수집회차 경로·원본 보존.
4. 편입 승인과 Harbor AC04 인수는 별도임을 확인.

## B-105-01 보완 — 2026-10-04 KST

- 최초 수신 첨부에서 원본 tar.gz 3개를 확보해 RECEIPT의 크기(21,221 / 8,690 / 8,205 bytes)와 SHA-256을 다시 대조했고 모두 일치했습니다.
- 압축 내부 일반 파일 53 / 33 / 33개와 해당 raw 디렉터리의 파일 집합 및 bytes가 전부 일치합니다(총119개, 원래 SHA256SUMS 포함). 재수집·재압축·raw 수정 없음.
- 저장소 검사기의 `archive_entries()`와 동일한 계산으로 내부 이름·크기·SHA-256을 대장에 추가했습니다. 기존 archive index 항목은 유지합니다.
- collector kit zip 원본 추가 보존은 비차단 권고이며 이번 변경에 포함하지 않습니다. collector24파일·각 manifest는 그대로입니다.
- 이 보완은 작성자 검수이며 새 HEAD 독립 리뷰와 전체 CI는 별도입니다. AC04 Apply·PASS로 승격하지 않습니다.

AI 사용: CODEX_ASSISTED.
