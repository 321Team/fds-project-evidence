# P1-HBR-01 — node-exporter `1.12.1-fds.1` 소스 빌드 이미지 Harbor push·Trivy (2026-10-01 14:32~14:41 KST)

MON Lead(이재환)가 실행했다. 빌드는 ansible01(`server01_ansible`), 대조·push·스캔은 k8s-control01(`server02`)에서 했다.
- 빌드 입력·절차: [infra-monitoring#31](https://github.com/321Team/infra-monitoring/pull/31)(GWONUK APPROVED, merge `b76ecef`) `kubernetes/monitoring/build/node-exporter/`
- HBR 승인 근거: 2026-10-01 회의 구두 승인(push `robot$push`, 조회·스캔), 서면 [#13 5923320268](https://github.com/321Team/fds-project-baseline/issues/13#issuecomment-5923320268) 조건(TLS 검증 유지, 자격증명 미기록)
- 기존 이미지 `fds/node-exporter@sha256:56566542…`의 Trivy High 9 결과: [evidence#85](https://github.com/321Team/fds-project-evidence/pull/85)

## 수신·대조

| 폴더 | 서버 원본 | archive | 대조 |
|---|---|---|---|
| `control01/ne-push-20261001T143641/` | control01 `~/ne-push-20261001T143641/` 중 22개(빌드 근거 일부 사본 포함) | `ne-push-small-20261001.tar.xz` 5,436 B, SHA-256 `dae14167…3eda6e5e90` | base64로 받아 복원, 서버 `sha256sum`과 일치. `SHA256SUMS-push` 22줄 모두 OK |

개별 파일은 archive를 그대로 푼 것이다(archive 안 최상위 폴더 `ne-push-small/`만 벗김). archive 내부 목록은 [ARCHIVE_CONTENTS](../../../registry/ARCHIVE_CONTENTS.json)에 올렸다.

편입하지 않은 원본(크기 때문에 해시와 위치만 기록):

| 파일 | 크기 | SHA-256 | 위치 |
|---|---|---|---|
| `node-exporter-1.12.1-fds.1.tar`(이미지) | 26,962,944 B | `5f5014b75a10dcc562c999b019f339a04a53c18405d0ef242772407a66ab782a` | ansible01 `~/ne-build-20261001T143224/`, control01 `~/ne-push-20261001T143641/` |
| `build-evidence-node-exporter-1.12.1-fds.1.tar.gz`(빌드 근거 묶음, 소스 tar 포함) | 428,994 B | `8fb077c0a4d293edcedf5a9b3ebc0952dd6d545b32ca41b63d8a402cfe731992` | 같음 |

근거 묶음 안의 작은 파일(`build-inputs.txt`·`gomod.diff`·`version.txt`·`image-id.txt`·`image-config.txt`·`ne-src.sha256`·`result.txt`·`kit.sha256`·`meta.txt`)과 그 `SHA256SUMS`(`build-SHA256SUMS`로 이름 바꿈)는 사본으로 함께 넣었다. `build.log`·`go.mod.updated`·`go.sum.updated`·`gomod.log`·소스 tar는 근거 묶음 원본에만 있다.

## 빌드 (ansible01, 14:32:24~14:33:06)

| 항목 | 근거 파일 | 결과 |
|---|---|---|
| 입력 키트 | `kit.sha256` | `Containerfile` `5c534187…`, `build.sh` `c87e07bc…` = #31 병합본. clone하지 않고 파일 내용을 터미널로 옮겨 만들었고, 실행 전 두 SHA를 대조했다 |
| 소스 | `ne-src.sha256` | node_exporter `6044da78…`(v1.12.1) tar `cfec7478…` = BUILD.md 고정값 |
| base 이미지 | `build-inputs.txt` | golang `0f063af2…`, chainguard static `c5fed92d…` — 실제 pull digest = 고정값 |
| 의존성 변경 | `gomod.diff` | `go 1.25.0→1.26.0`, `golang.org/x/crypto v0.54.0→v0.56.0`, `golang.org/x/text v0.40.0→v0.41.0`(x/crypto 요구). 그 밖의 변경 없음. 새 go.sum 4줄은 sum.golang.org 조회값과 같다(x/crypto는 build.sh가 대조, x/text는 PC에서 조회 대조) |
| 결과 | `version.txt`, `image-id.txt`, `image-config.txt`, `result.txt` | `node_exporter, version 1.12.1-fds.1 (branch: v1.12.1, revision: 6044da78…)`, go1.26.8, netgo·osusergo / image ID `0d5993fabf0016a15ef59d26c4fc5a065612ef262bb19ede968b080bbc850203` / `65534:65534`, Entrypoint `/bin/node_exporter` / DONE. build.sh의 buildinfo 검사(go1.26.8, x/crypto v0.56.0) 통과 |
| 전달 | — | ansible01 → control01 `scp`(사용자 실행) |

## 대조·push·스캔 (control01, 14:36~14:41)

| 단계 | 근거 파일 | 결과 |
|---|---|---|
| 인수 검증 | `verify.txt` | sidecar 대조 후 근거 묶음+이미지 tar로 `sha256sum -c SHA256SUMS` 17개 모두 OK |
| load | `load.txt`, `loaded-id.txt` | image ID `0d5993fa…` = 빌드 `image-id.txt` |
| push | `push.log`, `push-rc.txt`, `pushed.digest`, `pushed-at.txt` | 14:38:27, `robot$push`, TLS 검증(`--cert-dir`, Root PEM SHA-256 `20ddfa5e…053f`), rc=0, **`10.1.93.54/fds/node-exporter@sha256:4d5c92fcbea9fd5f2769a13192885366f6d348443ea6b48783590c9d9be43318`**(태그 `1.12.1-fds.1-candidate-20261001`), 로그아웃 |
| manifest | `manifest-ne.json` | 파일 SHA-256 = push digest, `config.digest` = `0d5993fa…`(빌드 image ID와 같음) |
| Trivy | `scan-req.txt`, `art-ne.json`, `vuln-ne.json` | 스캔 요청 HTTP 202. Trivy v0.62.1, 14:39:24~14:39:26 KST, Success, **Critical 0 / High 0 / Medium 0** / Unknown 1(GO-2026-5932, `golang.org/x/crypto` v0.56.0, 수정 버전 없음), fixable 0 |

- manifest·artifact·스캔 API는 Harbor `admin`으로 호출했다(`robot$push`는 403). 서면 조건 밖이며 회의 구두 승인이다. 자격증명은 `read -s`로 입력해 `curl -K -`로 넘겼고, 레지스트리 token도 `-K -`로 넘긴 뒤 바로 지웠다. 파일·명령줄에 남기지 않았고, 응답 헤더는 저장하지 않았다.
- 기존 `56566542…`(Critical 0 / High 9 / Medium 2 / Unknown 1) 대비 High 9건과 Medium 2건이 모두 없어졌다.

## 판정 범위

- 이 증적이 보여 주는 것: #31 병합본으로 만든 이미지가 같은 config(`0d5993fa…`)로 Harbor `4d5c92fc…`에 들어갔고, Trivy Critical·High가 0이다.
- 확정하지 않는 것: 승인 digest 확정은 HBR Lead 대조 대상이다(#13). 클러스터 적용(`node-exporter.yaml` digest 교체, DaemonSet 순차 교체)은 별도 PR·변경 창에서 한다. 기존 `56566542…`는 원복용으로 Harbor에 둔다.

AI 사용: CLAUDE_ASSISTED (명령 준비, 수신 대조·문서화, 실행은 담당자 본인)
