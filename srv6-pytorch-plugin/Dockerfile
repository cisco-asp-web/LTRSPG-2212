# SRv6 PyTorch Plugin Container
# Build: docker build -t srv6-pytorch-plugin:latest .

FROM ubuntu:24.04

LABEL maintainer="brmcdoug@cisco.com"
LABEL description="SRv6 route programming plugin for PyTorch distributed training"

# Install required system packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    iproute2 \
    iputils-ping \
    net-tools \
    libcap2-bin \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python packages from requirements.txt
RUN pip3 install --break-system-packages -r requirements.txt

# Copy the srv6_plugin package
COPY srv6_plugin/ /app/srv6_plugin/

# Copy example scripts
COPY examples/ /app/examples/

# Create a script to set capabilities at runtime
RUN echo '#!/bin/bash\nsetcap cap_net_admin,cap_net_raw+ep /sbin/ip\nexec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set Python path to include /app
ENV PYTHONPATH="/app:${PYTHONPATH}"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python3", "examples/test_connectivity.py"]

