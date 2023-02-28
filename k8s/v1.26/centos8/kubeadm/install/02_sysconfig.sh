#!/usr/bin/env bash

# Filename     :	prepare_env.sh
# Last modified:	2023-02-14 12:12
# Version      :
# Author       : jack.zang
# Email        : jack.zang@aishangwei.net
# Description  : 适用于 centos8，k8s 安装前的环境配置
# 使用方法：source <(curl -sL https://gitee.com/jack_zang/kubernetes/raw/k8s-v1.26/install/kubeadm_1.26/prepare_env.sh)
# ******************************************************

echo "请自行配置主机名以及主机名的解析！"

## 关闭防火墙和 Selinux
systemctl disable --now firewalld
setenforce 0
sed -i 's#SELINUX=enforcing#SELINUX=disabled#g' /etc/selinux/config

## 关闭 swap，之前的版本 swap 可能会影响性能，目前版本也是不建议开启
sed -ri 's/.*swap.*/#&/' /etc/fstab
swapoff -a && sysctl -w vm.swappiness=0
free

## 配置系统句柄数
ulimit -SHn 65535
cat > /etc/security/limits.d/k8s-limit.conf <<EOF
# open files
* soft nofile 655360
* hard nofile 131072
# max user processes
* soft nproc 655350
* hard nproc 655350
* seft memlock unlimited
* hard memlock unlimitedd
EOF

## 内核优化
cat <<EOF > /etc/sysctl.d/k8s.conf
## 开启数据包转发功能（实现vxlan）
net.ipv4.ip_forward=1
## iptables对bridge的数据进行处理
net.bridge.bridge-nf-call-iptables=1
net.bridge.bridge-nf-call-ip6tables=1
net.bridge.bridge-nf-call-arptables=1
## 关闭tcp_tw_recycle，否则和NAT冲突，会导致服务不通
net.ipv4.tcp_tw_recycle=0
## 不允许将TIME-WAIT sockets重新用于新的TCP连接
net.ipv4.tcp_tw_reuse=0
## socket监听(listen)的backlog上限
net.core.somaxconn=32768
## 最大跟踪连接数，默认 nf_conntrack_buckets * 4
net.netfilter.nf_conntrack_max=1000000
## 禁止使用 swap 空间，只有当系统 OOM 时才允许使用它
vm.swappiness=0
## 计算当前的内存映射文件数。
vm.max_map_count=655360
## 内核可分配的最大文件数
fs.file-max=6553600
## 持久连接
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_intvl=30
net.ipv4.tcp_keepalive_probes=10
## 其它以后看
vm.overcommit_memory = 1
vm.panic_on_oom = 0
fs.inotify.max_user_watches = 89100
fs.file-max = 52706963
fs.nr_open = 52706963
net.ipv4.tcp_max_tw_buckets = 36000
net.ipv4.tcp_max_orphans = 327680
net.ipv4.tcp_orphan_retries = 3
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_max_syn_backlog = 16384
net.ipv4.tcp_timestamps = 0
net.core.somaxconn = 16384
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
net.ipv6.conf.lo.disable_ipv6 = 0
net.ipv6.conf.all.forwarding = 1
EOF

sysctl -p /etc/sysctl.d/k8s.conf
modprobe br_netfilter
lsmod |grep conntrack
modprobe ip_conntrack


## 开启 ipvs
yum install ipvsadm ipset sysstat conntrack libseccomp -y
cat > /etc/modules-load.d/k8s-ipvs.conf <<EOF
ip_vs
ip_vs_rr
ip_vs_wrr
ip_vs_sh
nf_conntrack
nf_conntrack_ipv4
br_netfilter
overlay
EOF

systemctl restart systemd-modules-load.service
lsmod | grep -e ip_vs -e nf_conntrack

## 清空 iptables 规则（不知道需不需要）
iptables -F && iptables -X && iptables -F -t nat && iptables -X -t nat
iptables -P FORWARD ACCEPT


## 时区配置为中国-上海
timedatectl set-timezone Asia/Shanghai

## 配置时间同步
dnf install -y chrony
sed -i '/^pool 2.centos/d' /etc/chrony.conf
cat >> /etc/chrony.conf <<EOF
server ntp.aliyun.com iburst
server cn.ntp.org.cn iburst
EOF

systemctl restart chronyd && systemctl enable chronyd
chronyc  sources -v