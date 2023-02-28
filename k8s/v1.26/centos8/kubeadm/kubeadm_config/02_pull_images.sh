set -e
SHELL_PATH=`readlink -f $0`
PROJECT_ROOT=$(dirname  $SHELL_PATH)

# # 查看需要安装的镜像
# kubeadm config images list

# # pull 镜像
kubeadm config images pull --config $PROJECT_ROOT/kubeadm.yaml

# 重命名镜像
for i in `kubeadm config images list`; do
    image_aliyun=`echo "$i" |sed 's@registry.k8s.io@registry.cn-hangzhou.aliyuncs.com/google_containers@'`
    image_aliyun=`echo "$image_aliyun"| sed 's@coredns/@@'`
    echo "===================================="
    echo "sudo docker pull $image_aliyun"
    docker pull $image_aliyun
    docker tag $image_aliyun $i
done
