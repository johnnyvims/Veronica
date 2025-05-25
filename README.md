# Veronica

**Veronica** is an automated reconnaissance tool designed for pentesters, bug bounty hunters, and anyone who works full-time but still wants to dominate Hack The Box.  
Start it, go to sleep, and wake up with a full attack surface mapped out — CMS info, directories, CVEs, and more.

---

# Features

- Web recon (HTTP/HTTPS)
- CMS
- Subdomain & directory brute-forcing
- CVE enumeration

---

##  Getting Started

###  Kali-Only Setup (for now)

sudo apt update
sudo apt install -y python3 python3-venv python3-pip nikto whatweb feroxbuster ffuf dirsearch curl unzip subfinder


## clone and setup
git clone https://github.com/johnnyvims/Veronica.git
cd Veronica
unzip Sub/vhost_MEGA.txt.zip
python3 -m venv .Veronica
source .Veronica/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

---

## usage
python3 ReconBuster.py

---

## Sample Output

Here’s an example of Veronica’s recon output:

![Recon Screenshot](Screenshot1.png)
![Recon Screenshot](Screenshot2.png)

