FROM kalilinux/kali-last-release
COPY . /
RUN apt update && apt install -y python3 git python3-venv python3-pip nikto whatweb feroxbuster ffuf dirsearch curl unzip subfinder
RUN pip install --break-system-packages -r /requirements.txt
RUN cd / && unzip -o Sub/vhost_MEGA.txt.zip
WORKDIR /
ENTRYPOINT ["python3", "http://ReconBuster.py"]

