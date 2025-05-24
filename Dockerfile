FROM kalilinux/kali-last-release

# Set working directory
WORKDIR /veronica

# Copy project files into the container
COPY . .

# Install dependencies
RUN apt update && apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    nikto \
    whatweb \
    feroxbuster \
    ffuf \
    dirsearch \
    curl \
    unzip \
    subfinder

# Install Python requirements
RUN pip install --break-system-packages -r requirements.txt

# Unzip wordlist file
RUN unzip -o Sub/vhost_MEGA.txt.zip

# Run Veronica by default
ENTRYPOINT ["python3", "ReconBuster.py"]
