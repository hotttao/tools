set -e

curl -o /tmp/tigera-operator-v3.25.0.tgz -L https://github.com/projectcalico/calico/releases/download/v3.25.0/tigera-operator-v3.25.0.tgz
helm show values /tmp/tigera-operator-v3.25.0.tgz > calico-value.yaml  // 查看 chart 中可定义的配置
helm install calico tigera-operator-v3.25.0.tgz -n kube-system -f calico-value.yaml