set -e

wget -o /tmp/vscode.rpm https://az764295.vo.msecnd.net/stable/441438abd1ac652551dbe4d408dfcec8a499b8bf/code-1.75.1-1675893486.el7.x86_64.rpm
yum install /tmp/vscode.rpm
