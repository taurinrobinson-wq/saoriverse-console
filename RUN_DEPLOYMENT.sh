#!/bin/bash
set -e
cd /root
[ -d saoriverse-console ] || git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
git pull origin main
bash deploy.sh
