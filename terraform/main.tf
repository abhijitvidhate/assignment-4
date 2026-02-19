# Example: Provision a Kubernetes namespace using Terraform
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "kong" {
  metadata {
    name = "kong"
  }
}

resource "kubernetes_namespace" "user-service" {
  metadata {
    name = "user-service"
  }
}