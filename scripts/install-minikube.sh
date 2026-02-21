#!/bin/bash
# Install Minikube and kubectl

# Install kubectl
sudo apt-get update
sudo apt-get install -y curl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Clean up
rm kubectl minikube-linux-amd64

echo "Minikube and kubectl installed. You can now run: minikube start"
