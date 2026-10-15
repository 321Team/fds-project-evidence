"""Local evidence index. Does not publish, dispatch or touch retained originals."""
import json,pathlib
import runtime as r
assert r.load(r.O/'WINDOW_RETURN.json')['runtime_complete']
frozen={
 'detail_card':(r.B/'round5/FINAL_OPERATOR_CARD.md','cda3353af5f5894f6c9a01b1094f79d534f4f71cf2d48ee2773492c4a2986786'),
 'timing_contract':(r.B/'round5/TIMING_CONTRACT.md','9e46cd279e618a7d4cafaf989adc0670c3fd3cbd54b46dde5f1663fc964bbf92'),
 'recovery_helper':(r.B/'round4/console_restore_current.py','b01fd209dc089db3ed8da9eca590294d8b36523b119e76af962396d62e11d7f4'),
 'edge_helper':(r.B/'round4/edge_metrics_raw.py','0a5e52a99f25cc84b1e48fb815d45035503d16c8e63356d21a9b2a303da38cba'),
 'edge_launcher':(r.B/'round4/run_edge_capture.py','fbfca05e908262ee5b5bb50a3e43747516d446f996c4c9f7b16b61cd1cda9dd6'),
 'native_bundle':(r.B/'native-source.bundle.json','16366261081cf95639480cfb9256255541bc1099fde717225e4ad8f6e322ae8b')}
for name,(p,h) in frozen.items():assert r.sha(p.read_bytes())==h,name
members=r.load(r.O/'CONTROLLER_PACKAGE.json')['members']
source=[(r.B/'source'/p.split('/')[-1],h) for p,h in members.items() if p.startswith('tools/')]
assert len(source)==37 and all(r.sha(p.read_bytes())==h for p,h in source)
a=r.load(r.ROOT/'deliverables/phase1-central-control-20261015/AC09_USER_AUTHORIZATION_1535.json')
card=r.ROOT/'deliverables/phase1-central-control-20261015'/a['card'];assert r.sha(card.read_bytes())==a['card_sha256']=='7bdad3c96100c578ac80ba7ab450dcfa971b37ca719003fbea4bd5cc43222a34'
index='''# AC09 실제 원본 인덱스

기준: 2026-10-15 16:06:17 KST 단독 실행 종료. [실행 결과](RUNTIME_RESULT.md), [창 반환](WINDOW_RETURN.json), [시각 판정](TIMING_ASSESSMENT.json). 추가 Run·Token·POST·수동 PATCH 없음. 원본에는 공개 저장소에 올리지 않은 정상 관측 응답이 포함되므로 기존 승인된 비공개 보관 기준을 유지한다.

| 묶음 | 원본/판정 경로 |
|---|---|
| 승인과 입력 | `AUTHORIZATION_BINDINGS.json`, `R1/approval.json`, `R2/approval.json`, 회차별 deploy JSON, `STAGED.json` |
| 정확 4 Run·4 Job·로그 ZIP | `github-final/RUN_SUMMARY.json` 및 각 Run 폴더 |
| R1/R2 원 claim·checkpoint | `r1-journal-final/r1/stdout.json`, `r2-journal-final/r2/stdout.json` (원 mtime/ctime/inode/bytes/SHA 포함) |
| 첫 PATCH 구간 | `P_FIRST_ORIGINAL.json`, `R2_FIRST_PATCH_INTERVAL.json`, 첫 journal 원본 폴더 |
| 실제 전후 6대 시계 | `clocks-before-r1`, `clocks-after-finish`; 각각 6호스트·18명령 |
| 최소 업무 2회 | `r1-post-one/stdout.json`, `r2-post-one/stdout.json`, `r1/r2-before-mon`, `r1/r2-after-mon` 원 HTTP/metrics 응답 |
| 직접 포트 및 기존 경로 관측 | `r1/r2-before-edge-api`, `r1/r2-before-api`, 각 observer inventory의 Pod UID/container/PID/netns 결속 |
| 추가 Edge GET 4개 | 상위 `round4/edge-pre`, `round4/edge-during`; 원 helper 불변 |
| 현행 복귀/최종 상태 | `R2_CURRENT_PODS.json`, `RECOVERY_HTTP_CONFIRMED.json`, `r2-final-state`, `return-current-state` |
| 토큰 수량·만료 원본 | `operations/broker-execute-38693979785`, `operations/broker-execute-38694721511`; 토큰 값은 기록하지 않음 |
| 임시 공급 제거 | `EXACT_CLEANUP_RECEIPT.json`, `cleanup-inventory-*`, `operations/cleanup-exact-*`; 제거 전 파일별 SHA와 inode/mtime 보존 |
| 증적 보존 잔존물 | 원 서버 claim/checkpoint·Workflow 결과·native source 디렉터리 8개, 별도 삭제 없음. `return-ansible.json`, `return-control01`, `return-runner`에서 공개 소스 7개씩 canonical bundle SHA 일치 재확인 |
| 로컬 준비 예외 | `R1/actual-scope-over-local-metadata.original.json`와 `AUTHORIZATION_BINDINGS.json`; 원격 승인/입력 불변·발급 전 복구 |

`EVIDENCE_MANIFEST.json`은 이 폴더의 실제 파일과 외부 동결 기준/추가 Edge 원본을 파일별 SHA-256으로 연결한다. 원본·파생 결과·실행 보조 코드를 구분하며 SHA 일치 자체를 AC 통과로 판정하지 않는다. 매니페스트·자체 영수증만 자기 참조 방지를 위해 제외한다. 원 파일을 보존한 상태에서 결과/대장을 추후 추가하면 새 버전 인덱스로 별도 관리한다.

중앙이 #11 최종 umbrella 기록 및 다음 실행창을 담당한다. 이 세션은 중복 최종 댓글이나 타 세션 실행 메시지를 전송하지 않았다. DB 동일 ID 행 미수집·엄격 시각 상한 미입증을 유지하며, 후속 독립 리뷰에서 판정한다.
'''
(r.O/'EVIDENCE_INDEX.md').write_bytes(index.encode())
exclude={'EVIDENCE_MANIFEST.json','EVIDENCE_SEAL.json'}
entries=[]
for p in sorted(r.O.rglob('*')):
 if not p.is_file() or p.name in exclude or '__pycache__' in p.parts:continue
 rel=p.relative_to(r.O).as_posix()
 category='LOCAL_ORCHESTRATION' if p.suffix=='.py' else 'ORIGINAL_OR_CAPTURE_RECEIPT' if ('/stdout.' in rel or '/stderr.' in rel or 'journal' in rel or 'clocks-' in rel or 'github-final/' in rel or 'operations/' in rel) else 'DERIVED_OR_PINNED_INPUT'
 entries.append({'path':rel,'bytes':p.stat().st_size,'sha256':r.sha(p.read_bytes()),'category':category})
external={}
ext_paths=[p for p,h in frozen.values()]+[p for p,h in source]+[card,r.ROOT/'deliverables/phase1-central-control-20261015/AC09_USER_AUTHORIZATION_1535.json']
for d in ['edge-pre','edge-during']:
 ext_paths.extend(p for p in (r.B/'round4'/d).rglob('*') if p.is_file())
for p in ext_paths:external[str(p.relative_to(r.ROOT)).replace('\\','/')]=r.sha(p.read_bytes())
manifest={'at_utc':r.now().isoformat(),'execution_source':r.SOURCE,'local_root':str(r.O),'files':entries,'external_frozen_or_original':external,'frozen_invariants':'source37 / card / timing / helper3 / bundle unchanged','acceptance':'NOT_COMPLETE','counts':r.load(r.O/'WINDOW_RETURN.json')['counts']}
r.save(r.O/'EVIDENCE_MANIFEST.json',manifest)
for v in entries:assert r.sha((r.O/v['path']).read_bytes())==v['sha256']
receipt={'at_utc':r.now().isoformat(),'file_count':len(entries),'external_file_count':len(external),'manifest_sha256':r.sha((r.O/'EVIDENCE_MANIFEST.json').read_bytes()),'verified':True,'window_returned_kst':r.load(r.O/'WINDOW_RETURN.json')['returned_at_kst'],'runtime_counts':manifest['counts'],'external_post_by_this_executor':False}
r.save(r.O/'EVIDENCE_SEAL.json',receipt)
r.status('**AC09 반환 후 원본 인덱스·해시 마감 완료.** 창 반환시각 16:06:17 KST, 추가 실행0. [원본 인덱스](../p1-cicd-ac09-preparation-20261015/runtime-1535/EVIDENCE_INDEX.md), [매니페스트](../p1-cicd-ac09-preparation-20261015/runtime-1535/EVIDENCE_MANIFEST.json), [검증영수증](../p1-cicd-ac09-preparation-20261015/runtime-1535/EVIDENCE_SEAL.json). 파일 '+str(len(entries))+'개·외부 동결/추가 원본 '+str(len(external))+'개 SHA 대조 완료. source37·승인카드·시각계약·helper3·bundle 불변. 실제 수량 false2/true2/Token2/POST2/추가EdgeGET4, 신규Runner0·수동복구PATCH0. 중앙의 #11 최종 umbrella 게시와 중복되지 않게 최종댓글·타세션 메시지0. DB행 대조 및 SEC 시각 사후판정은 중앙 인수 사항, AC09 최종완료 미선언.')
print(json.dumps(receipt,ensure_ascii=False))
