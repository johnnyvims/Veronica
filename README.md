# Verionca
## -- getting started

**note:only usable on kali**
apt update

apt install python3 python3-venv python3-pip nikto whatweb feroxbuster ffuf dirsearch curl unzip subfinder 

unzip Sub/vhost_MEGA.txt.zip

python3 -m venv .Veronica
source .Veronica/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python3 ReconBuster.py
