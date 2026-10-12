#!/usr/bin/env bash
# #9 종결용 3인 IAM 사용자 상태 + 정책 내용 + IaC trust + CloudTrail 조회 가능 여부 — 읽기 전용 (v3)
# 실행: AWS CloudShell 서울, 개인 IAM 사용자 321team-gwonuk 또는 321team-hayeoung. root·역할 세션 금지
# 비용: 없음. 생성·수정·삭제 0. AccessDenied는 DENIED로 기록하고 0개로 바꾸지 않음
# v2 (PR #9 권욱 리뷰 6115764768 반영):
#   B1 정책 이름 목록뿐 아니라 사용자·그룹 inline 원문(get-*-policy)과 managed 기본 버전 원문(get-policy-version) 수집
#   B2 manifest·archive 실패를 STOP으로 전파
#   CloudTrail --no-paginate 명시, CLI 버전 기록, caller를 두 사람으로 한정하고 caller RC 확인
# v3 (권욱 리뷰 6116249967·6116387633): managed 정책 파일 키를 basename 대신 full-ARN SHA256으로, ARN은 policy-<sha>.arn에 기록
set -u
ACCOUNT=774055931866
REGION=ap-northeast-2
USERS="321team-gwonuk 321team-hayeoung 321team-jaehwan"
ALLOWED_CALLERS="321team-gwonuk 321team-hayeoung"
ROLE=FDS-IaC-Operator
OUT="$HOME/fds-iam-readback-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$OUT" && chmod 700 "$OUT" || exit 1
SUM="$OUT/summary.tsv"
printf 'case\trc\tresult\n' > "$SUM"
kst() { TZ=Asia/Seoul date '+%Y-%m-%dT%H:%M:%S%z'; }
{ echo "start_kst=$(kst)"; sha256sum "$0"; aws --version 2>&1; } > "$OUT/meta.txt"

safe() { printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '_'; }

run() {  # run NAME aws-args...  → stdout/stderr/rc 보존
  local n; n=$(safe "$1"); shift
  { echo "kst=$(kst)"; printf 'argv: aws'; printf ' %q' "$@"; echo; } > "$OUT/$n.cmd"
  aws "$@" --output json --no-cli-pager > "$OUT/$n.stdout" 2> "$OUT/$n.stderr"
  local rc=$?
  echo "rc=$rc" >> "$OUT/$n.cmd"
  local r=OK
  if [ $rc -ne 0 ]; then
    if grep -qE 'AccessDenied|UnauthorizedOperation|not authorized' "$OUT/$n.stderr"; then r=DENIED; else r=ERROR; fi
  elif grep -qE '"PolicyDocument"|"Document"' "$OUT/$n.stdout"; then
    # 판정 보조 표시일 뿐 판정이 아님: 모든 Action 허용 형태가 보이면 표시
    if tr -d ' \n\r\t' < "$OUT/$n.stdout" | grep -qE '"(Not)?Action":\[?"\*"'; then r="OK WILDCARD_ACTION_PRESENT"; else r="OK no_wildcard_action"; fi
  fi
  printf '%s\t%s\t%s\n' "$n" "$rc" "$r" >> "$SUM"
  echo "[$r] $n"
  return $rc
}

field() { sed -n "s/.*\"$1\": \"\\([^\"]*\\)\".*/\\1/p" "$OUT/$(safe "$2").stdout"; }

run caller sts get-caller-identity --region "$REGION" || { echo "STOP: caller 조회 실패"; exit 2; }
ARN=$(field Arn caller)
ok=no
for u in $ALLOWED_CALLERS; do [ "$ARN" = "arn:aws:iam::$ACCOUNT:user/$u" ] && ok=yes; done
[ $ok = yes ] || { echo "STOP: 허용된 개인 IAM 사용자가 아님 (현재 $ARN). root·역할 세션 금지"; exit 2; }
echo "caller=$ARN"

managed_content() {  # managed_content PREFIX ARN
  local p=$1 arn=$2 v
  local tag
  tag=$(printf '%s' "$arn" | sha256sum) || return 1   # v3: full-ARN 해시로 중복 제거 (권욱 리뷰 6116249967)
  tag=${tag%% *}
  echo "$arn" > "$OUT/policy-$tag.arn"
  [ -f "$OUT/policy-$tag-meta.stdout" ] && return 0
  run "policy-$tag-meta" iam get-policy --policy-arn "$arn" || return 0
  v=$(field DefaultVersionId "policy-$tag-meta")
  [ -n "$v" ] && run "policy-$tag-$v-document" iam get-policy-version --policy-arn "$arn" --version-id "$v"
  return 0
}

for u in $USERS; do
  run "$u-mfa"          iam list-mfa-devices --user-name "$u"
  run "$u-access-keys"  iam list-access-keys --user-name "$u"
  if run "$u-attached" iam list-attached-user-policies --user-name "$u"; then
    for a in $(field PolicyArn "$u-attached"); do managed_content "$u" "$a"; done
  fi
  if run "$u-inline" iam list-user-policies --user-name "$u"; then
    for p in $(sed -n '/"PolicyNames"/,/]/s/^ *"\([^"]*\)",\{0,1\}$/\1/p' "$OUT/$u-inline.stdout"); do
      run "$u-inline-$p-document" iam get-user-policy --user-name "$u" --policy-name "$p"
    done
  fi
  if run "$u-groups" iam list-groups-for-user --user-name "$u"; then
    for g in $(field GroupName "$u-groups" | sort -u); do
      [ -f "$OUT/group-$(safe "$g")-attached.cmd" ] && continue
      if run "group-$g-attached" iam list-attached-group-policies --group-name "$g"; then
        for a in $(field PolicyArn "group-$g-attached"); do managed_content "group-$g" "$a"; done
      fi
      if run "group-$g-inline" iam list-group-policies --group-name "$g"; then
        for p in $(sed -n '/"PolicyNames"/,/]/s/^ *"\([^"]*\)",\{0,1\}$/\1/p' "$OUT/$(safe "group-$g-inline").stdout"); do
          run "group-$g-inline-$p-document" iam get-group-policy --group-name "$g" --policy-name "$p"
        done
      fi
    done
  fi
done

run iac-role iam get-role --role-name "$ROLE"
run iac-role-attached iam list-attached-role-policies --role-name "$ROLE"
run iac-role-inline iam list-role-policies --role-name "$ROLE"

# CloudTrail 조회 권한 확인: 이벤트 1건만, 자동 pagination 끔, 내용은 저장하지 않고 개수만
{ echo "kst=$(kst)"; echo "argv: aws cloudtrail lookup-events --max-results 1 --no-paginate --region $REGION (stdout 내용 미저장, 개수만)"; } > "$OUT/cloudtrail-lookup.cmd"
CT=$(aws cloudtrail lookup-events --max-results 1 --no-paginate --region "$REGION" --output json --no-cli-pager 2> "$OUT/cloudtrail-lookup.stderr")
rc=$?
echo "rc=$rc" >> "$OUT/cloudtrail-lookup.cmd"
if [ $rc -eq 0 ]; then
  n=$(printf '%s' "$CT" | grep -c '"EventId"'); r="ALLOWED events_returned=$n"
elif grep -qE 'AccessDenied|not authorized' "$OUT/cloudtrail-lookup.stderr"; then r=DENIED
else r=ERROR; fi
CT=
printf 'cloudtrail-lookup\t%s\t%s\n' "$rc" "$r" >> "$SUM"
echo "[$r] cloudtrail-lookup"

# 포장: 실패를 성공으로 넘기지 않음 (권욱 리뷰 B2 제안 그대로)
echo "end_kst=$(kst)" >> "$OUT/meta.txt" || exit 1
( set -o pipefail
  cd "$OUT" &&
  find . -maxdepth 1 -type f ! -name SHA256SUMS -print0 |
  sort -z | xargs -0 sha256sum > SHA256SUMS &&
  sha256sum --check --quiet SHA256SUMS
) || { echo "STOP: manifest failed" >&2; exit 1; }
tar czf "$OUT.tar.gz" -C "$(dirname "$OUT")" "$(basename "$OUT")" ||
  { echo "STOP: archive failed; preserve raw directory $OUT" >&2; exit 1; }
archive_sha=$(sha256sum "$OUT.tar.gz") || exit 1
archive_bytes=$(wc -c < "$OUT.tar.gz") || exit 1
echo
column -t -s $'\t' "$SUM"
echo
printf 'archive: %s\nsha256: %s\nbytes: %s\n' "$OUT.tar.gz" "$archive_sha" "$archive_bytes"
