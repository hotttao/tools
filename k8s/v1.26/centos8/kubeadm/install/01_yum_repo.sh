#!/usr/bin/env bash

# Filename     :	centos8_use_aliyun_base_epel.sh
# Last modified:	2022-09-27 12:12
# Version      :
# Author       : jack.zang
# Email        : jack.zang@aishangwei.net
# Description  : source <(curl -sL https://gitee.com/jack_zang/public-scripts/raw/master/shell/repo/centos8_use_aliyun_base_epel.sh)
# ******************************************************
set -e
SHELL_PATH=`readlink -f $0`
PROJECT_ROOT=$(dirname  $SHELL_PATH)

[ -d /etc/yum.repos.d.bak ] || mkdir /etc/yum.repos.d.bak
mv /etc/yum.repos.d/* /etc/yum.repos.d.bak/
mv $PROJECT_ROOT/yum.repo/aliyum.repo  /etc/yum.repos.d/aliyun_base_epel.repo   
dnf clean all && dnf makecache