set -e
SHELL_PATH=`readlink -f $0`
PROJECT_ROOT=$(dirname  $SHELL_PATH)

# 修改 /etc/containerd/config.toml 配置文件
mkdir -pv $PROJECT_ROOT/containerd
containerd config default > $PROJECT_ROOT/containerd/config_default.toml
containerd config default | sed 's@SystemdCgroup = false@SystemdCgroup = true@' | \
                            sed 's@k8s.gcr.io/pause:3.6@registry.aliyuncs.com/google_containers/pause:3.9@' | \
                            sed 's@registry.k8s.io/pause:3.6@registry.aliyuncs.com/google_containers/pause:3.9@' \
                            > $PROJECT_ROOT/containerd/config.toml

mkdir /etc/containerd/
cp $PROJECT_ROOT/containerd/config.toml /etc/containerd/
systemctl restart containerd
