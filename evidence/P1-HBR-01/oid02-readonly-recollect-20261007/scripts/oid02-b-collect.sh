# 2026-10-07 16:26 ansible01에서 실행한 읽기 전용 수집 명령(그대로 보관). 서버를 변경하지 않는다.
cd ~/infra-ansible && D=~/oid02-b-$(date +%Y%m%dT%H%M%S) && mkdir -p $D
cap(){ n=$1; shift; s=$(date '+%F %T'); "$@" >$D/$n.out 2>$D/$n.err; rc=$?; echo "$n rc=$rc start=$s end=$(date '+%F %T') out=$(wc -c <$D/$n.out)B err=$(wc -c <$D/$n.err)B" >>$D/index.txt; }
K="ssh -o BatchMode=yes server02@10.1.93.102"
cap k1-nodes $K 'kubectl get nodes -o wide'
cap k2-taints $K 'kubectl get nodes -o custom-columns=NAME:.metadata.name,UNSCHED:.spec.unschedulable,TAINTS:.spec.taints[*].key'
cap k3-pods $K 'kubectl -n kube-system get pods -o wide'
cap k4-imageid $K 'kubectl -n kube-system get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,IMAGEID:.status.containerStatuses[*].imageID'
for h in k8s-control01 k8s-control02 k8s-control03 k8s-worker01 k8s-worker02 k8s-worker03; do
  cap node-$h ansible -i inventory/hosts.yml $h -b -m shell -a 'hostname; ctr -n k8s.io images ls; containerd --version; df -h /var/lib/containerd | tail -1'
done
(cd $D && sha256sum *.out *.err index.txt > oid02-b-sums.local.txt)
