echo "# host=$(hostname -s) user=$(whoami) time=$(date --iso-8601=seconds)"
echo "== kube-system 파드: pod|node|container|image|pullPolicy|imageID"
kubectl -n kube-system get pods -o json | jq -r '.items[]|.metadata.name as $p|.spec.nodeName as $n|((.spec.initContainers//[])+.spec.containers)[] as $c|(((.status.initContainerStatuses//[])+(.status.containerStatuses//[]))|map(select(.name==$c.name))|first|.imageID//"") as $id|[$p,$n,$c.name,$c.image,$c.imagePullPolicy,$id]|@tsv'
echo "== 컨트롤러 스케줄 제약: kind|name|replicas|nodeSelector|tolerations|affinity"
kubectl -n kube-system get deploy,ds -o json | jq -r '.items[]|[.kind,.metadata.name,(.spec.replicas//"-"|tostring),(.spec.template.spec.nodeSelector|tostring),(.spec.template.spec.tolerations|tostring),(.spec.template.spec.affinity|tostring)]|@tsv'
echo "== 노드 플랫폼"
kubectl get nodes -o custom-columns=NAME:.metadata.name,ARCH:.status.nodeInfo.architecture,OS:.status.nodeInfo.osImage,CRI:.status.nodeInfo.containerRuntimeVersion
echo "(end)"
