# P1-LB-01 Stage A — 수신 자료

- Ticket: In Progress; Stage A 기술 검토 PASS, Stage B Pending.
- Origin: `/var/log/fds-evidence/P1-LB-01/stage-a/` on k8s-api-lb01.
- Original archive: `P1-LB-01_Stage_A_Review_Input_v1.1.tar.gz`.
- Archive SHA-256: `62c64dfbd0cc672c96e4b1fbfa0c71a406e0c86d991b663c0ee02a47b82236a3`.
- 원본 21개는 수정 없이 보존했다. 원본 tar.gz와 sidecar는 기존 FDS_Evidence_Repository_Preparation_v1.0.zip의 source-archive/에 원래 바이트로 보관했다. 이번 Git 편입은 원본 21개와 검토 문서를 대상으로 하며 tar.gz의 Release Asset 등록은 수행하지 않는다.
- source-receipt/REVIEW_EXPORT_STATUS.json은 반출 당시 상태다. 누락된 원본 19/99를 소급 생성한 것으로 해석하지 않는다.
- 19_stage_a_handoff_review.md 및 99_SHA256SUMS.txt는 수신 후 작성한 검토 자료다.
- 보완 3건은 사용자 콘솔 제출본이다. 서버 .txt/.sha256 원본의 바이트 검증을 수행한 것은 아니다.
- 이하영 실제 인수·이권욱 최종 승인 Pending; kubeadm init/join HOLD.
- 증적 편입 검토 후보. 등록 Commit과 PR은 별도 인계 기록에서 참조한다. Git 저장소 내 파일 mode는 서버의 보안 권한 0640을 표현하지 않는다.

검증: 이 디렉터리에서 `sha256sum --check 99_SHA256SUMS.txt`를 실행한다.
