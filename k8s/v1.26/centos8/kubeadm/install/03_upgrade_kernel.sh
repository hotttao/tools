#!/usr/bin/env bash

# Filename     :	prepare_env_update_kernel.sh
# Last modified:	2023-02-14 12:12
# Version      :
# Author       : jack.zang
# Email        : jack.zang@aishangwei.net
# Description  : 适用于 centos8，升级为最新内核
# 使用方法：source <(curl -sL https://gitee.com/jack_zang/kubernetes/raw/k8s-v1.26/install/kubeadm_1.26/prepare_env_update_kernel.sh)
# ******************************************************

## 配置内核仓库
rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
cat >> /etc/yum.repos.d/elrepo.repo << EOF
[elrepo-kernel]
name=elrepoyum
baseurl=https://mirrors.aliyun.com/elrepo/kernel/el8/x86_64/
enable=1
gpgcheck=0
EOF

yum -y install kernel-ml

## 使用序号为0的内核，序号0是前面查出来的可用内核编号
grub2-set-default 0

## 生成 grub 配置文件并重启
grub2-mkconfig -o /boot/grub2/grub.cfg