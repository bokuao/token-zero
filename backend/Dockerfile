FROM python:3.12-slim

# Install SOPS binary (diperlukan untuk sops -d di app/sops_decrypt.py)
RUN apt-get update && apt-get install -y wget && \
    wget -qO /usr/local/bin/sops https://github.com/getsops/sops/releases/download/v3.9.0/sops-v3.9.0.linux.amd64 && \
    chmod +x /usr/local/bin/sops && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
