FROM ubuntu:22.04

LABEL maintainer="nicmcl@cisco.com"
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Full Networking Stack & Troubleshooting Tools
RUN apt-get update && apt-get install -y \
    # Core Networking & SSH
    iproute2 iputils-ping curl net-tools \
    traceroute mtr-tiny tcpdump \
    openssh-server sudo vim ca-certificates procps \
    # Advanced Troubleshooting (The "Swiss Army Knife")
    iperf3 socat dnsutils nmap fping jq \
    # IPv6 Specific
    ndisc6 \
    # Python for Ansible and Scripting
    python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

# 2. Setup SSH Runtime
RUN mkdir -p /var/run/sshd

# 3. Create Users (cisco and admin for VS Code compatibility)
RUN useradd -m -s /bin/bash cisco && echo "cisco:cisco123" | chpasswd && usermod -aG sudo cisco \
    && useradd -m -s /bin/bash admin && echo "admin:cisco123" | chpasswd && usermod -aG sudo admin

# 4. Allow Passwordless Sudo (Essential for lab speed)
RUN echo "cisco ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && echo "admin ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 5. SSH Hardening for Lab Environments
RUN sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config

# 6. Final Prep
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]