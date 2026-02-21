# Install hey load testing tool

# For Linux (x86_64)
curl -LO https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64
chmod +x hey_linux_amd64
sudo mv hey_linux_amd64 /usr/local/bin/hey

# Verify installation
hey --version
