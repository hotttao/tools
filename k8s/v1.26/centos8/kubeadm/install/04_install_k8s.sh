#!/usr/bin/env bash

# Filename     :	kubernetes_install.sh
# Last modified:	2023-02-14 12:12
# Version      :
# Author       : jack.zang
# Email        : jack.zang@aishangwei.net
# Description  : 适用于 centos8，安装 k8s
# 使用方法：source <(curl -sL https://gitee.com/jack_zang/kubernetes/raw/k8s-v1.26/install/kubeadm_1.26/kubernetes_install.sh)
# ******************************************************

###################
CONTAINERD_VERSION='1.6.*'
KUBE_VERSION='1.26.*'


dnf install -y iproute-tc

######### 安装 containerd ##########

cat > /etc/modules-load.d/containerd.conf <<EOF
overlay
br_netfilter
EOF
modprobe overlay
modprobe br_netfilter

curl -o  /etc/yum.repos.d/docker-ce.repo   https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

dnf install -y containerd.io-${CONTAINERD_VERSION}

## 生成配置文件
containerd config default > /etc/containerd/config.toml
sed -i 's#sandbox_image.*#sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.6"#' /etc/containerd/config.toml
## 配置 cgroup 驱动程序 systemd
sed -i 's#SystemdCgroup.*#SystemdCgroup = true#' /etc/containerd/config.toml
sed -i 's#config_path = ""#config_path = "/etc/containerd/certs.d"' etc/containerd/config.toml
mkdir /etc/containerd/certs.d/docker.io -pv
cat > /etc/containerd/certs.d/docker.io/hosts.toml << EOF
server = "https://docker.io"
[host."https://frz7i079.mirror.aliyuncs.com"]
  capabilities = ["pull", "resolve"]
EOF

systemctl enable containerd && systemctl start containerd
ctr version
runc -version

#crictl config runtime-endpoint unix:///var/run/containerd/containerd.sock

## 安装 kubernetes
cat > /etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
EOF

dnf -y install kubeadm-${KUBE_VERSION} kubectl-${KUBE_VERSION} kubelet-${KUBE_VERSION} cri-tools

cat > /etc/sysconfig/kubelet <<EOF
KUBELET_EXTRA_ARGS="--cgroup-driver=systemd"
EOF

# 配置开启自启
systemctl daemon-reload && systemctl enable kubelet