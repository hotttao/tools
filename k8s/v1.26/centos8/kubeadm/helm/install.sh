#!/usr/bin/env bash

# Filename     :	helm-cmd-install.sh
# Last modified:	2023-02-15 12:11
# Version      :
# Author       : jack.zang
# Email        : jack.zang@aishangwei.net
# Description  :
# 使用方法：source <(curl -sL https://gitee.com/jack_zang/public-scripts/raw/master/shell/helm/helm-cmd-install.sh)
# ******************************************************

read -t 20 -p "请输入要安装的 helm 版本，例：v3.11.0 ,直接回车安装默认版本 v3.11.0：" HELMVERSION

[ -z "$HELMVERSION" ] && HELMVERSION="v3.11.0"

## 下载 helm 二进制包
if ping files.aishangwei.net -c 1 > /dev/null 2>&1;
then
  echo "从 files.aishangwei 下载"
  curl -LO https://files.aishangwei.net/files/helm/helm-${HELMVERSION}-linux-amd64.tar.gz
else
  echo "从 helm 官网下载"
  curl -LO https://get.helm.sh/helm-${HELMVERSION}-linux-amd64.tar.gz
fi

## 安装 tar
if ! rpm -q tar > /dev/null 2>&1;
then
  dnf install -y tar
fi


tar -zxvf helm-${HELMVERSION}-linux-amd64.tar.gz
mv linux-amd64/helm  /usr/local/bin/
rm -rf ./linux-amd64 helm-${HELMVERSION}-linux-amd64.tar.gz

echo "----------- helm 版本 ----------"
helm version