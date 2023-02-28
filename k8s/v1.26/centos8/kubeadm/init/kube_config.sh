mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

cat > /etc/profile.d/kubernetes.sh <<EOF
export PATH=$PATH:/usr/local/bin
EOF

source /etc/profile.d/kubernetes.sh