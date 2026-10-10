#!/usr/bin/env bash
# infra-terraform#8 — state 원문 접근 음성 시험 v1
# 목적: 허용 주체(FDS-IaC-Operator, root) 외에는 state/lock 8개 객체의 읽기·쓰기·삭제가
#       bucket policy에서 명시적으로 거부(explicitDeny)되는지 확인한다.
# 성격: 조회·시뮬레이션만. AWS 자원 생성/변경/삭제 없음. state 내용을 내려받지 않음.
# 실행: AWS CloudShell (ap-northeast-2), 321team-hayeoung 본인 로그인. set -e 미사용(단계별 RC 출력).

ACCOUNT=774055931866
REGION=ap-northeast-2
BUCKET="fds-tfstate-${ACCOUNT}-${REGION}"
SIM_CALLER="arn:aws:iam::${ACCOUNT}:user/321team-hayeoung"   # role 시험 시 simulator가 요구하는 IAM user caller
IAC_ROLE="arn:aws:iam::${ACCOUNT}:role/FDS-IaC-Operator"

USERS="321team-gwonuk 321team-jaehwan 321team-hayeoung"
ROLES="FDS-ReadOnly-Audit FDS-Network-Operator"
ACTIONS='["s3:GetObject","s3:GetObjectVersion","s3:PutObject","s3:DeleteObject","s3:DeleteObjectVersion"]'
KEYS="phase2/network/terraform.tfstate phase2/vpn/terraform.tfstate phase2/rosa-prereq/terraform.tfstate phase2/rosa-runtime/terraform.tfstate"
EXPECTED_PER_CASE=40   # 5 action x 8 object

umask 077
OUT=$(mktemp -d "$HOME/issue8-negative.XXXXXX")
echo "OUT_DIR=$OUT"
echo "START_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')" | tee "$OUT/00-meta.txt"

# ---------- 0. 계정·실행자 확인 ----------
aws sts get-caller-identity --output json > "$OUT/00-identity.json"
echo "IDENTITY_RC=$?"
acct=$(jq -r .Account "$OUT/00-identity.json")
caller=$(jq -r .Arn "$OUT/00-identity.json")
echo "CALLER=$caller" | tee -a "$OUT/00-meta.txt"
if [ "$acct" != "$ACCOUNT" ]; then echo "STOP=WRONG_ACCOUNT($acct)"; exit 2; fi

# ---------- 1. 실제 bucket policy 조회 ----------
aws s3api get-bucket-policy --bucket "$BUCKET" --region "$REGION" --output json > "$OUT/01-bucket-policy-raw.json"
rc=$?; echo "GET_BUCKET_POLICY_RC=$rc"
if [ $rc -ne 0 ]; then echo "STOP=BUCKET_POLICY_READ_FAILED"; exit 3; fi
jq -r .Policy "$OUT/01-bucket-policy-raw.json" > "$OUT/01-bucket-policy.json"
echo "BUCKET_POLICY_CANONICAL_SHA256=$(jq -S -c . "$OUT/01-bucket-policy.json" | sha256sum | cut -d' ' -f1)" | tee -a "$OUT/00-meta.txt"

RESOURCES=$(for k in $KEYS; do printf 'arn:aws:s3:::%s/%s\narn:aws:s3:::%s/%s.tflock\n' "$BUCKET" "$k" "$BUCKET" "$k"; done | jq -R . | jq -s -c .)

# ---------- 2. 시뮬레이션 함수 ----------
# $1=label  $2=PolicySourceArn  $3=CallerArn  $4=aws:PrincipalArn(context)
sim() {
  jq -n \
    --arg src "$2" --arg caller "$3" --arg parn "$4" \
    --arg owner "arn:aws:iam::${ACCOUNT}:root" \
    --rawfile rp "$OUT/01-bucket-policy.json" \
    --argjson actions "$ACTIONS" --argjson res "$RESOURCES" \
    '{PolicySourceArn:$src, CallerArn:$caller, ActionNames:$actions, ResourceArns:$res,
      ResourcePolicy:$rp, ResourceOwner:$owner,
      ContextEntries:[
        {ContextKeyName:"aws:PrincipalArn",ContextKeyValues:[$parn],ContextKeyType:"string"},
        {ContextKeyName:"aws:SecureTransport",ContextKeyValues:["true"],ContextKeyType:"boolean"},
        {ContextKeyName:"aws:PrincipalIsAWSService",ContextKeyValues:["false"],ContextKeyType:"boolean"},
        {ContextKeyName:"s3:x-amz-server-side-encryption",ContextKeyValues:["AES256"],ContextKeyType:"string"}]}' \
    > "$OUT/sim-$1.request.json"
  aws iam simulate-principal-policy --cli-input-json "file://$OUT/sim-$1.request.json" \
    --output json > "$OUT/sim-$1.result.json" 2> "$OUT/sim-$1.stderr.txt"
  local rc=$?
  # action x resource 단위로 펼치기 (ResourceSpecificResults 우선)
  jq -c '[.EvaluationResults[] as $e
          | (if (($e.ResourceSpecificResults // []) | length) > 0
               then $e.ResourceSpecificResults[] | {a:$e.EvalActionName, r:.EvalResourceName, d:.EvalResourceDecision,
                    res:any(.MatchedStatements[]?; .SourcePolicyType=="resource"),
                    m:(.MissingContextValues // [])}
               else {a:$e.EvalActionName, r:$e.EvalResourceName, d:$e.EvalDecision,
                    res:any($e.MatchedStatements[]?; .SourcePolicyType=="resource"),
                    m:($e.MissingContextValues // [])} end)]
         | unique_by(.a + "|" + .r)' "$OUT/sim-$1.result.json" > "$OUT/sim-$1.flat.json" 2>/dev/null
  echo $rc
}

ALL_PASS=1
report_negative() { # $1=label $2=rc
  local f="$OUT/sim-$1.flat.json"
  if [ "$2" -ne 0 ] || [ ! -s "$f" ]; then
    echo "CASE=$1 SIM_RC=$2 RESULT=ERROR ($(head -c 200 "$OUT/sim-$1.stderr.txt"))" | tee -a "$OUT/summary.txt"; ALL_PASS=0; return; fi
  local total deny other miss
  total=$(jq 'length' "$f")
  deny=$(jq '[.[] | select(.d=="explicitDeny" and .res)] | length' "$f")
  other=$(jq '[.[] | select((.d=="explicitDeny" and .res) | not)] | length' "$f")
  miss=$(jq -c '[.[].m[]] | unique' "$f")
  local result=FAIL
  [ "$total" -eq "$EXPECTED_PER_CASE" ] && [ "$deny" -eq "$EXPECTED_PER_CASE" ] && result=PASS
  [ "$result" = PASS ] || ALL_PASS=0
  echo "CASE=$1 SIM_RC=$2 TOTAL=$total DENY_BY_BUCKET_POLICY=$deny OTHER=$other MISSING_CONTEXT=$miss RESULT=$result" | tee -a "$OUT/summary.txt"
}

# ---------- 3. 음성 시험: 팀원 3명 ----------
for u in $USERS; do
  arn="arn:aws:iam::${ACCOUNT}:user/$u"
  if ! aws iam get-user --user-name "$u" --output json > "$OUT/exist-$u.json" 2> "$OUT/exist-$u.stderr.txt"; then
    echo "CASE=user-$u RESULT=SKIP_NOT_FOUND_OR_DENIED ($(head -c 150 "$OUT/exist-$u.stderr.txt"))" | tee -a "$OUT/summary.txt"; ALL_PASS=0; continue; fi
  rc=$(sim "user-$u" "$arn" "$arn" "$arn")
  report_negative "user-$u" "$rc"
done

# ---------- 4. 음성 시험: Audit / Network 역할 ----------
for r in $ROLES; do
  arn="arn:aws:iam::${ACCOUNT}:role/$r"
  if ! aws iam get-role --role-name "$r" --output json > "$OUT/exist-$r.json" 2> "$OUT/exist-$r.stderr.txt"; then
    if grep -q NoSuchEntity "$OUT/exist-$r.stderr.txt"; then
      echo "CASE=role-$r RESULT=SKIP_ROLE_ABSENT" | tee -a "$OUT/summary.txt"
    else
      echo "CASE=role-$r RESULT=ERROR ($(head -c 150 "$OUT/exist-$r.stderr.txt"))" | tee -a "$OUT/summary.txt"; ALL_PASS=0
    fi
    continue; fi
  rc=$(sim "role-$r" "$arn" "$SIM_CALLER" "$arn")
  report_negative "role-$r" "$rc"
done

# ---------- 5. 대조군: 허용 주체(FDS-IaC-Operator)는 bucket policy에 막히지 않아야 함 ----------
rc=$(sim "control-iac-operator" "$SIM_CALLER" "$SIM_CALLER" "$IAC_ROLE")
f="$OUT/sim-control-iac-operator.flat.json"
if [ "$rc" -eq 0 ] && [ -s "$f" ]; then
  hit=$(jq '[.[] | select(.d=="explicitDeny" and .res)] | length' "$f")
  dist=$(jq -c 'group_by(.d) | map({(.[0].d): length}) | add' "$f")
  cres=FAIL; [ "$hit" -eq 0 ] && cres=PASS
  [ "$cres" = PASS ] || ALL_PASS=0
  echo "CASE=control-iac-operator SIM_RC=$rc DENY_BY_BUCKET_POLICY=$hit DECISIONS=$dist RESULT=$cres" | tee -a "$OUT/summary.txt"
else
  echo "CASE=control-iac-operator SIM_RC=$rc RESULT=ERROR" | tee -a "$OUT/summary.txt"; ALL_PASS=0
fi

# ---------- 6. 실제 확인(본인만): 내용 없이 존재 여부 요청(head-object) → 403 기대 ----------
# root로 실행하면 root는 허용 주체이므로 건너뛴다.
case "$caller" in
  *":user/"*)
    for k in $KEYS; do for obj in "$k" "$k.tflock"; do
      aws s3api head-object --bucket "$BUCKET" --key "$obj" --region "$REGION" > /dev/null 2> "$OUT/head.stderr.tmp"
      hrc=$?
      code=$(grep -oE '\((403|404)\)' "$OUT/head.stderr.tmp" | tr -d '()')
      [ $hrc -eq 0 ] && code=200
      hres=FAIL; [ "$code" = 403 ] && hres=PASS
      [ "$hres" = PASS ] || ALL_PASS=0
      echo "RUNTIME_HEAD key=$obj HTTP=${code:-unknown} RESULT=$hres" | tee -a "$OUT/summary.txt"
    done; done
    rm -f "$OUT/head.stderr.tmp" ;;
  *) echo "RUNTIME_HEAD=SKIPPED (caller is not an IAM user)" | tee -a "$OUT/summary.txt" ;;
esac

# ---------- 7. 마무리 ----------
echo "END_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')" | tee -a "$OUT/00-meta.txt"
[ $ALL_PASS -eq 1 ] && FINAL=PASS || FINAL=CHECK_REQUIRED
echo "NEGATIVE_TEST=$FINAL" | tee -a "$OUT/summary.txt"
echo "AWS_MUTATION=NOT_RUN" | tee -a "$OUT/summary.txt"
(cd "$OUT" && sha256sum -- * > SHA256SUMS)
echo "SHA256SUMS_RC=$?"
echo "PRESERVED_DIR=$OUT"
