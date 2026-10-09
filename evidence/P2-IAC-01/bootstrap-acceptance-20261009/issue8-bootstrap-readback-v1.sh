#!/usr/bin/env bash
# infra-terraform#8 — 중앙 bootstrap 설정 재조회(readback) v1
# 목적: 대조표(issue8-bootstrap-acceptance-table-draft.md)의 "실제" 칸을 본인 세션으로 직접 다시 읽어 채운다.
#       대상 행: S1–S7, S10, R1–R4, R6 (+ B3 DynamoDB 미사용 확인, phase2/ 현재 객체 목록)
# 성격: 조회만. AWS 자원 생성/변경/삭제 없음. state 내용을 내려받지 않음(객체 이름·크기만).
# 실행: AWS CloudShell (ap-northeast-2), 321team-hayeoung 본인 로그인(MFA). set -e 미사용(단계별 RC 출력).
# 짝: state 원문 접근 음성 시험은 issue8-state-negative-test-v1.sh 로 따로 실행한다.

ACCOUNT=774055931866
REGION=ap-northeast-2
BUCKET="fds-tfstate-${ACCOUNT}-${REGION}"
STACK=FDS-Central-Bootstrap-v1
RELAY=FDS-Relay-SSM
IAC_ROLE=FDS-IaC-Operator
SSM_CORE=arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

umask 077
OUT=$(mktemp -d "$HOME/issue8-readback.XXXXXX")
echo "OUT_DIR=$OUT"
echo "START_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')" | tee "$OUT/00-meta.txt"
aws --version 2>&1 | tee -a "$OUT/00-meta.txt"

ALL_PASS=1
# $1=행ID  $2=PASS|FAIL|WAIT|INFO  $3=관측값
row() {
  echo "ROW=$1 RESULT=$2 OBSERVED=$3" | tee -a "$OUT/summary.txt"
  [ "$2" = FAIL ] && ALL_PASS=0
  return 0
}
# $1=파일이름  나머지=aws 명령 인자. stdout→파일.json, stderr→파일.stderr.txt, RC 기록
call() {
  local name=$1; shift
  aws "$@" --output json > "$OUT/$name.json" 2> "$OUT/$name.stderr.txt"
  local rc=$?
  echo "CALL=$name RC=$rc" | tee -a "$OUT/calls.txt"
  return $rc
}

# ---------- 0. 계정·실행자 확인 (S1) ----------
call 00-identity sts get-caller-identity
acct=$(jq -r .Account "$OUT/00-identity.json" 2>/dev/null)
echo "CALLER=$(jq -r .Arn "$OUT/00-identity.json" 2>/dev/null)" | tee -a "$OUT/00-meta.txt"
if [ "$acct" != "$ACCOUNT" ]; then echo "STOP=WRONG_ACCOUNT($acct)"; exit 2; fi

# ---------- 1. CloudFormation stack (S10, 4자원 소유) ----------
if call 01-stack cloudformation describe-stacks --stack-name "$STACK" --region "$REGION"; then
  st=$(jq -r '.Stacks[0].StackStatus' "$OUT/01-stack.json")
  tp=$(jq -r '.Stacks[0].EnableTerminationProtection' "$OUT/01-stack.json")
  sid=$(jq -r '.Stacks[0].StackId' "$OUT/01-stack.json")
  case "$sid" in arn:aws:cloudformation:${REGION}:${ACCOUNT}:*) r=PASS ;; *) r=FAIL ;; esac
  row S1 "$r" "StackId=$sid"
  [ "$st" = CREATE_COMPLETE ] && [ "$tp" = true ] && r=PASS || r=FAIL
  row S10a "$r" "StackStatus=$st TerminationProtection=$tp"
else
  row S1 FAIL "describe-stacks RC!=0"; row S10a FAIL "describe-stacks RC!=0"
fi
if call 01-stack-resources cloudformation list-stack-resources --stack-name "$STACK" --region "$REGION"; then
  res=$(jq -c '[.StackResourceSummaries[] | "\(.LogicalResourceId)=\(.ResourceType)=\(.ResourceStatus)"] | sort' "$OUT/01-stack-resources.json")
  n=$(jq '.StackResourceSummaries | length' "$OUT/01-stack-resources.json")
  ok=$(jq '[.StackResourceSummaries[] | select(.ResourceStatus=="CREATE_COMPLETE")] | length' "$OUT/01-stack-resources.json")
  [ "$n" -eq 4 ] && [ "$ok" -eq 4 ] && r=PASS || r=FAIL
  row S10b "$r" "count=$n $res"
fi

# ---------- 2. State bucket 설정 (S2–S7) ----------
if call 02-location s3api get-bucket-location --bucket "$BUCKET"; then
  loc=$(jq -r .LocationConstraint "$OUT/02-location.json")
  [ "$loc" = "$REGION" ] && r=PASS || r=FAIL
  row S2 "$r" "bucket=$BUCKET region=$loc"
else row S2 FAIL "get-bucket-location RC!=0"; fi

if call 02-encryption s3api get-bucket-encryption --bucket "$BUCKET" --region "$REGION"; then
  alg=$(jq -r '[.ServerSideEncryptionConfiguration.Rules[].ApplyServerSideEncryptionByDefault.SSEAlgorithm] | join(",")' "$OUT/02-encryption.json")
  kms=$(jq -r '[.ServerSideEncryptionConfiguration.Rules[].ApplyServerSideEncryptionByDefault.KMSMasterKeyID // empty] | length' "$OUT/02-encryption.json")
  [ "$alg" = AES256 ] && [ "$kms" -eq 0 ] && r=PASS || r=FAIL
  row S3 "$r" "SSEAlgorithm=$alg KMSKeyCount=$kms"
else row S3 FAIL "get-bucket-encryption RC!=0"; fi

if call 02-versioning s3api get-bucket-versioning --bucket "$BUCKET" --region "$REGION"; then
  v=$(jq -r '.Status // "NotSet"' "$OUT/02-versioning.json")
  mfa=$(jq -r '.MFADelete // "NotSet"' "$OUT/02-versioning.json")
  [ "$v" = Enabled ] && r=PASS || r=FAIL
  row S4 "$r" "Status=$v MFADelete=$mfa"
else row S4 FAIL "get-bucket-versioning RC!=0"; fi

if call 02-pab s3api get-public-access-block --bucket "$BUCKET" --region "$REGION"; then
  pab=$(jq -c '.PublicAccessBlockConfiguration' "$OUT/02-pab.json")
  allt=$(jq '[.PublicAccessBlockConfiguration[]] | all' "$OUT/02-pab.json")
  [ "$allt" = true ] && r=PASS || r=FAIL
  row S5 "$r" "$pab"
else row S5 FAIL "get-public-access-block RC!=0"; fi

if call 02-ownership s3api get-bucket-ownership-controls --bucket "$BUCKET" --region "$REGION"; then
  own=$(jq -r '[.OwnershipControls.Rules[].ObjectOwnership] | join(",")' "$OUT/02-ownership.json")
  [ "$own" = BucketOwnerEnforced ] && r=PASS || r=FAIL
  row S6 "$r" "ObjectOwnership=$own"
else row S6 FAIL "get-bucket-ownership-controls RC!=0"; fi

if call 02-policy-raw s3api get-bucket-policy --bucket "$BUCKET" --region "$REGION"; then
  jq -r .Policy "$OUT/02-policy-raw.json" > "$OUT/02-policy.json"
  echo "BUCKET_POLICY_CANONICAL_SHA256=$(jq -S -c . "$OUT/02-policy.json" | sha256sum | cut -d' ' -f1)" | tee -a "$OUT/00-meta.txt"
  sids=$(jq -c '[.Statement[].Sid] | sort' "$OUT/02-policy.json")
  echo "POLICY_SIDS=$sids" | tee -a "$OUT/00-meta.txt"
  # S7: TLS 강제 문장
  tls=$(jq '[.Statement[] | select(.Effect=="Deny" and .Condition.Bool."aws:SecureTransport"=="false")] | length' "$OUT/02-policy.json")
  [ "$tls" -ge 1 ] && r=PASS || r=FAIL
  row S7 "$r" "DenyInsecureTransport statements=$tls"
  # S8: 원문 접근 Deny 문장의 대상 객체 수·허용 주체 (실제 거부 동작은 음성 시험 스크립트)
  s8=$(jq -c '[.Statement[] | select(.Sid=="DenyStatePayloadAndMutationOutsideApprovedPrincipals")
              | {objects:(.Resource|length), allowed:(.Condition.ArnNotEquals."aws:PrincipalArn"|sort)}]' "$OUT/02-policy.json")
  echo "$s8" | grep -q '"objects":8' && echo "$s8" | grep -q "role/${IAC_ROLE}" && r=PASS || r=FAIL
  row S8-config "$r" "$s8"
else row S7 FAIL "get-bucket-policy RC!=0"; row S8-config FAIL "get-bucket-policy RC!=0"; fi

# S7 실동작(선택): 암호화 안 된 http 요청은 거부돼야 함. 조회 요청이며 변경 없음.
aws s3api get-bucket-versioning --bucket "$BUCKET" --region "$REGION" \
  --endpoint-url "http://s3.${REGION}.amazonaws.com" > /dev/null 2> "$OUT/02-tls-http.stderr.txt"
hrc=$?
if [ $hrc -ne 0 ] && grep -q AccessDenied "$OUT/02-tls-http.stderr.txt"; then r=PASS; else r=FAIL; fi
row S7-runtime "$r" "http request RC=$hrc ($(head -c 120 "$OUT/02-tls-http.stderr.txt" | tr '\n' ' '))"

# ---------- 3. phase2/ 아래 현재 객체 (이름·크기·버전 수만, 내용 없음) ----------
if call 03-objects s3api list-object-versions --bucket "$BUCKET" --region "$REGION" --prefix phase2/ \
     --query '{Versions:Versions[].{Key:Key,Size:Size,IsLatest:IsLatest,LastModified:LastModified},DeleteMarkers:DeleteMarkers[].{Key:Key,IsLatest:IsLatest}}'; then
  row INFO-objects INFO "$(jq -c '{versions:((.Versions // [])|length), deleteMarkers:((.DeleteMarkers // [])|length), keys:([(.Versions // [])[].Key]|unique)}' "$OUT/03-objects.json")"
else row INFO-objects INFO "list-object-versions RC!=0 (권한 확인 필요)"; fi

# ---------- 4. 잠금: DynamoDB lock 테이블을 쓰지 않는지 (B3 보조) ----------
if call 04-ddb dynamodb list-tables --region "$REGION"; then
  hit=$(jq -c '[.TableNames[] | select(test("tf|terraform|lock|state";"i"))]' "$OUT/04-ddb.json")
  [ "$hit" = "[]" ] && r=PASS || r=FAIL
  row B3-aws "$r" "lock-like DynamoDB tables=$hit"
else row B3-aws INFO "dynamodb list-tables RC!=0 (권한 확인 필요)"; fi

# ---------- 5. Relay role / instance profile (R1–R4) ----------
if call 05-role iam get-role --role-name "$RELAY"; then
  arn=$(jq -r .Role.Arn "$OUT/05-role.json"); path=$(jq -r .Role.Path "$OUT/05-role.json")
  [ "$arn" = "arn:aws:iam::${ACCOUNT}:role/${RELAY}" ] && [ "$path" = / ] && r=PASS || r=FAIL
  row R1 "$r" "Arn=$arn Path=$path MaxSession=$(jq -r .Role.MaxSessionDuration "$OUT/05-role.json")"
  trust=$(jq -c '[.Role.AssumeRolePolicyDocument.Statement[] | {e:.Effect,p:.Principal,a:.Action,c:(.Condition // null)}]' "$OUT/05-role.json")
  [ "$trust" = '[{"e":"Allow","p":{"Service":"ec2.amazonaws.com"},"a":"sts:AssumeRole","c":null}]' ] && r=PASS || r=FAIL
  row R2 "$r" "$trust"
else row R1 FAIL "get-role RC!=0"; row R2 FAIL "get-role RC!=0"; fi

call 05-role-attached iam list-attached-role-policies --role-name "$RELAY"
call 05-role-inline iam list-role-policies --role-name "$RELAY"
att=$(jq -c '[.AttachedPolicies[].PolicyArn] | sort' "$OUT/05-role-attached.json" 2>/dev/null)
inl=$(jq -c '.PolicyNames' "$OUT/05-role-inline.json" 2>/dev/null)
call 05-ssmcore iam get-policy --policy-arn "$SSM_CORE"
ver=$(jq -r .Policy.DefaultVersionId "$OUT/05-ssmcore.json" 2>/dev/null)
[ "$att" = "[\"$SSM_CORE\"]" ] && [ "$inl" = "[]" ] && r=PASS || r=FAIL
row R3 "$r" "attached=$att inline=$inl SSMCoreDefaultVersion=$ver"

if call 05-profile iam get-instance-profile --instance-profile-name "$RELAY"; then
  parn=$(jq -r .InstanceProfile.Arn "$OUT/05-profile.json")
  proles=$(jq -c '[.InstanceProfile.Roles[].RoleName]' "$OUT/05-profile.json")
  [ "$parn" = "arn:aws:iam::${ACCOUNT}:instance-profile/${RELAY}" ] && [ "$proles" = "[\"$RELAY\"]" ] && r=PASS || r=FAIL
  row R4 "$r" "Arn=$parn Path=$(jq -r .InstanceProfile.Path "$OUT/05-profile.json") Roles=$proles"
else row R4 FAIL "get-instance-profile RC!=0"; fi

# ---------- 6. PassRole (R6) — FDS-IaC-Operator 가 아직 없으면 '대기' ----------
if call 06-iac-role iam get-role --role-name "$IAC_ROLE"; then
  call 06-iac-attached iam list-attached-role-policies --role-name "$IAC_ROLE"
  : > "$OUT/06-passrole-statements.jsonl"
  for p in $(jq -r '.AttachedPolicies[].PolicyArn' "$OUT/06-iac-attached.json"); do
    v=$(aws iam get-policy --policy-arn "$p" --query Policy.DefaultVersionId --output text 2>/dev/null)
    aws iam get-policy-version --policy-arn "$p" --version-id "$v" --output json 2>/dev/null \
      | jq -c --arg p "$p" '.PolicyVersion.Document.Statement[] | select(.Effect=="Allow" and ((.Action|tostring)|test("iam:PassRole"))) | {policy:$p,Resource,Condition}' \
      >> "$OUT/06-passrole-statements.jsonl"
  done
  n=$(wc -l < "$OUT/06-passrole-statements.jsonl")
  good=$(jq -s "[.[] | select(.Resource==\"arn:aws:iam::${ACCOUNT}:role/${RELAY}\" and .Condition.StringEquals.\"iam:PassedToService\"==\"ec2.amazonaws.com\")] | length" "$OUT/06-passrole-statements.jsonl")
  [ "$n" -eq 1 ] && [ "$good" -eq 1 ] && r=PASS || r=FAIL
  row R6 "$r" "Allow PassRole statements=$n matching=$good (inline 정책은 별도 확인)"
else
  if grep -q NoSuchEntity "$OUT/06-iac-role.stderr.txt"; then
    row R6 WAIT "$IAC_ROLE ABSENT — Grant 후 재실행"
  else
    row R6 FAIL "get-role $IAC_ROLE 오류 ($(head -c 120 "$OUT/06-iac-role.stderr.txt" | tr '\n' ' '))"
  fi
fi

# ---------- 7. 마무리 ----------
echo "END_KST=$(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M:%S')" | tee -a "$OUT/00-meta.txt"
[ $ALL_PASS -eq 1 ] && FINAL=PASS || FINAL=CHECK_REQUIRED
echo "READBACK=$FINAL" | tee -a "$OUT/summary.txt"
echo "AWS_MUTATION=NOT_RUN" | tee -a "$OUT/summary.txt"
(cd "$OUT" && sha256sum -- * > SHA256SUMS)
echo "SHA256SUMS_RC=$?"
echo "PRESERVED_DIR=$OUT"
