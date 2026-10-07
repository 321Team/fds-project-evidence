# P1-SEC-01 PSA version label 변경 원본(`received-20261006T1220Z`) 정정 기록, 2026-10-07

기존 원본은 변경하지 않는다. 대상은 `evidence/P1-SEC-01/received-20261006T1220Z/`([fds-project-evidence#128](https://github.com/321Team/fds-project-evidence/pull/128), merge `1d059a46bbcad9388694602db4f99725686d0caa`)이다. 이 폴더의 README와 아카이브는 그대로 두고, 아래 정정과 보완은 이 새 폴더로만 남긴다.

**이 문서는 PASS·AC-01 충족을 주장하지 않는다.** 정정은 시험 결과(label 3줄 추가, level 불변, monitoring-api 준수 Pod 허용·위반 Pod 거부)나 AC 판정을 바꾸지 않는다.

근거: SEC Lead 정합화 기록 [#19 6017262499](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6017262499) §1~§3, 이를 검토한 PMO/QA 심층 리뷰 [#19 6031943799](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6031943799) §1(비차단 "정정은 새 기록" 요청), 정정의 근거가 된 PMO/QA 대조 [#19 6016629505](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6016629505) §1-3.

## 정정 1건
**시험 Pod 정의가 #49와 같은지 여부.** 원본 README의 "한계와 주의" 1번("#49의 `psa-compliant`/`psa-privileged`와 이름·container 이름이 같을 뿐 **같은 정의인지는 확인하지 못했다**")과 PR #128 본문의 같은 취지의 문장을 다음으로 정정한다.

- **정정 후: 같지 않다(다르다).** PMO/QA 대조에 따르면 [evidence#49](https://github.com/321Team/fds-project-evidence/pull/49)의 `psa-privileged`는 **6개 항목**(privileged, allowPrivilegeEscalation, capabilities, runAsNonRoot, runAsUser=0, seccomp)을 위반한 정의였고, 이 변경에서 쓴 `psa-privileged.yaml`은 `privileged`와 `allowPrivilegeEscalation` **2개 항목만** 위반한다(원본 `t2-privileged.err`에도 두 항목만 나온다).
- **원인:** [변경 GO 6014740196](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6014740196)의 "#49 정의 재사용 가능" 전제가 **정의 파일의 존재를 확인하지 않은 것**이었다. #49 원본에는 결과 파일만 있고 정의 파일이 없어 같은 정의를 재사용할 수 없었고, 그래서 새 정의를 쓴 것이다.
- **영향:** 시험 목적은 `restricted:v1.36` 위반 거부 확인이며, PMO/QA는 이것이 AC-01 판단에 영향이 없다고 판단했다. 이 판단을 따르며 본 정정이 그것을 다시 판단하지 않는다.
- **확인의 한계:** 이 정정은 PMO/QA 대조에 의존한다. 정정을 작성한 쪽은 #49의 서버 스크립트(`01-psa-violation.sh`)를 열어 재확인하지 않았다.

## 보완 1건 (오류 정정이 아니라 누락 보완)
**원본 폴더는 같은 변경의 "첫 작업 창"(기록 A) 원본만 담는다.** 같은 실행자가 **두 번째 작업 창**(root 셸, 기록 B)에서도 21:24:04 사전 확인과 21:30:40 검증(server dry-run만, 변경 없음)을 따로 수행했고, 그 원본(`psa-pre-out.txt` `b820445e…`, `psa-managed-fields.txt` `7e46b102…`, `psa-verify-out.txt` `d198c354…`)은 **증적으로 편입하지 않았다.** 이 경위와 절차 이탈 2건(승인 창 21:30 종료 40초 뒤의 검증 시작, #49 정의 대신 새 정의 사용)은 [#19 6017262499](https://github.com/321Team/fds-project-baseline/issues/19#issuecomment-6017262499) §1·§3에 기록되어 있다. 기록 B는 이 정정에서도 **결과 근거로 인용하지 않는다.**

## 확인 방법
2026-10-07 이 정정은 위 #19 코멘트와 #128 원본 README를 다시 읽어 문구를 대조했다. 서버 접속이나 새 시험은 없었고, 정정 대상 폴더의 파일은 수정하지 않았다.

AI usage: CLAUDE_ASSISTED (대조·정리 보조). 판단은 이하영.
