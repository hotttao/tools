#!/bin/bash
# 作用: 生成 kubeadm 的默认配置文件

set -e
SHELL_PATH=`readlink -f $0`
PROJECT_ROOT=$(dirname  $SHELL_PATH)

kubeadm config print init-defaults --component-configs KubeletConfiguration > $PROJECT_ROOT/kubeadm_default.yaml
