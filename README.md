# Secure API Platform using Kong on Kubernetes

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:

- **Minikube** - Lightweight Kubernetes cluster
- **kubectl** - Kubernetes command-line tool
- **Helm 3** - Kubernetes package manager
- **Docker** - Container runtime
- **Python 3** - For JWT token generation
- **hey** - Load testing tool (optional, for DDoS testing)

## Installation Scripts

All installation scripts are provided in `/home/abhijit/Talentica-Assignment-4/` for easy setup.

### 1. Install Minikube
```sh
bash /home/abhijit/install-minikube.sh
```
This script installs both Minikube and kubectl.

### 2. Install Docker
```sh
bash /home/abhijit/install-docker.sh
```
This script installs Docker and enables it as the Minikube driver.

### 3. Install Helm
```sh
bash /home/abhijit/install-helm.sh
```
This script installs Helm 3 for managing Kubernetes packages.

### 4. Install hey (Load Testing Tool)
```sh
bash /home/abhijit/install-hey.sh
```
This script installs the `hey` load testing tool for DDoS simulation and testing.

## Quick Start

Once all prerequisites are installed, follow these steps:

### 1. Start Minikube
```sh
minikube start --driver=docker
```

### 2. Set up Docker environment
```sh
eval $(minikube docker-env)
```

### 3. Build microservice Docker image
```sh
cd /home/abhijit/Talentica-Assignment-4/microservice
docker build -t user-service:latest .
```

### 4. Deploy microservice using Helm
```sh
helm install user-service /home/abhijit/Talentica-Assignment-4/helm/user-service
```

### 5. Deploy Kong using Helm
```sh
helm repo add kong https://charts.konghq.com
helm repo update
helm install kong kong/kong -f /home/abhijit/Talentica-Assignment-4/helm/kong/values.yaml
```

### 6. Apply Kong declarative configuration
```sh
kubectl port-forward svc/kong-kong-admin 8001:8001 -n default &
sleep 2
curl -i -X POST http://localhost:8001/config \
  --data-binary @/home/abhijit/Talentica-Assignment-4/kong/kong.yaml \
  -H "Content-Type: application/yaml"
```

### 7. Generate JWT Token
```sh
python3 /home/abhijit/generate_jwt.py robokey robosecret
```
Save this token for testing protected endpoints.

## Architecture Overview
The platform uses Kong Gateway as an API entrypoint on Kubernetes, routing requests to a FastAPI microservice with a local SQLite database. Kong enforces JWT authentication, rate limiting, IP whitelisting, and injects custom headers via a Lua plugin. DDoS protection is implemented using Kong plugins or ModSecurity.

## API Request Flow
1. Client sends a request to Kong's proxy endpoint.
2. Kong applies IP whitelisting, rate limiting, and (if required) JWT authentication.
3. Kong forwards the request to the microservice.
4. The microservice processes the request and responds via Kong to the client.

## JWT Authentication Flow
1. Client authenticates via `/login` and receives a JWT.
2. For protected endpoints (e.g., `/users`), the client includes the JWT in the `Authorization` header.
3. Kong validates the JWT using its JWT plugin and externalized secrets.
4. If valid, the request is forwarded to the microservice; otherwise, a 401 is returned.

## Authentication Bypass Strategy
- Endpoints `/health` and `/verify` are configured in Kong to bypass JWT authentication by not attaching the JWT plugin to these routes in the Kong declarative config.

## Testing Steps

### Rate Limiting
1. Obtain a valid JWT token.
2. Use a tool like `curl` or `hey` to send more than 10 requests per minute to a protected endpoint (e.g., `/users`).
   ```sh
   for i in {1..15}; do curl -H "Authorization: Bearer <JWT>" http://<KONG_PROXY>/users; done
   ```
3. Observe HTTP 429 responses after the limit is exceeded.

### IP Whitelisting
1. Ensure your IP is in the allowed CIDR list in Kong’s config.
2. Access a protected endpoint from an allowed IP and verify access.
3. Attempt access from a non-whitelisted IP and verify you receive HTTP 403 Forbidden.

### DDoS Protection
1. Use a load testing tool (e.g., `hey`, `ab`, or `wrk`) to simulate a large number of requests.
   ```sh
   hey -z 10s -c 50 http://<KONG_PROXY>/users
   ```
2. Confirm that Kong and/or ModSecurity block or throttle excessive requests, and the service remains available for legitimate traffic.

### Custom Lua Plugin
- Call any endpoint and show the custom header injected by the Lua plugin:
  ```sh
  curl -i http://<KONG_PROXY>/health
  ```
- In the response headers, show `X-Custom-Header` or similar.

## Demo Commands

### 1. JWT Authentication (Protected Endpoint)
- **Without JWT (should be rejected):**
  ```sh
  curl http://127.0.0.1:38659/users
  ```
- **With valid JWT (should succeed):**
  ```sh
  curl -H "Authorization: Bearer <VALID_JWT>" http://127.0.0.1:38659/users
  ```

### 2. Authentication Bypass (Public Endpoints)
- **No JWT required:**
  ```sh
  curl http://127.0.0.1:38659/health
  curl http://127.0.0.1:38659/verify
  ```

### 3. Rate Limiting
- **Exceed the rate limit (e.g., 10 requests/min):**
  ```sh
  for i in {1..15}; do curl -H "Authorization: Bearer <VALID_JWT>" http://127.0.0.1:38659/users; done
  ```
  - The last few requests should return HTTP 429 or a rate limit message.

### 4. IP Whitelisting
- **From an allowed IP:**  
  Access should succeed.
- **From a non-whitelisted IP:**  
  Access should return HTTP 403 Forbidden (test by changing the whitelist in Kong config and redeploying).

### 5. DDoS Protection
- **Simulate a DDoS attack:**
  ```sh
  hey -z 10s -c 50 http://127.0.0.1:38659/users
  ```
  - Observe that excessive requests are blocked or rate-limited.

### 6. Custom Lua Plugin
- **Show custom header injection:**
  ```sh
  curl -i http://127.0.0.1:38659/health
  ```
  - Look for `X-Custom-Header` or similar in the response headers.

## How to Demonstrate Each Deliverable

### 1. JWT Authentication via Kong JWT Plugin

- **Show that requests without JWT are rejected:**
  - Make a request to a protected endpoint (e.g., `/users`) **without** the Authorization header:
    ```sh
    curl http://<KONG_PROXY>/users
    ```
  - **Expected result:** You should receive a `401 Unauthorized` response or a message like `{"message":"Unauthorized"}` or `{"detail":"Missing or invalid Authorization header"}`.

- **Show that requests with an invalid JWT are rejected:**
  - Make a request with a random or malformed token:
    ```sh
    curl -H "Authorization: Bearer invalidtoken" http://<KONG_PROXY>/users
    ```
  - **Expected result:** You should receive a `401 Unauthorized` response or a message like `{"detail":"Invalid token"}`.

### 2. SQLite for User Storage, Auto-initialized
- Show that the SQLite DB file exists in the microservice container:
  ```sh
  kubectl exec -it <user-service-pod> -- ls /app/sqlite.db
  ```
- Register a user and show it is stored in SQLite.

### 3. Microservice Endpoints & Auth Bypass
- Show `/health` and `/verify` work without JWT:
  ```sh
  curl http://<KONG_PROXY>/health
  curl http://<KONG_PROXY>/verify
  ```
- Show `/users` requires JWT.

### 4. Kubernetes Deployment, Declarative & Containerized
- Show Helm chart files and Kubernetes manifests.
- Show running pods and services:
  ```sh
  kubectl get pods
  kubectl get svc
  ```

### 5. Kong Gateway as API Gateway
- Show Kong running as a pod/service in Kubernetes:
  ```sh
  kubectl get pods -l app.kubernetes.io/name=kong
  ```

### 6. Rate Limiting & IP Whitelisting via Kong Plugins
- Exceed rate limit and show HTTP 429:
  ```sh
  for i in {1..15}; do curl -H "Authorization: Bearer <JWT>" http://<KONG_PROXY>/users; done
  ```
- Attempt access from a non-whitelisted IP and show HTTP 403.

### 7. Custom Kong Lua Plugin
- Call any endpoint and show the custom header in the response:
  ```sh
  curl -i http://<KONG_PROXY>/health
  # Look for X-Custom-Header in the response headers
  ```

### 8. DDoS Protection (e.g., Kong + ModSecurity)
- Use a load testing tool to simulate a DDoS:
  ```sh
  hey -z 10s -c 50 http://<KONG_PROXY>/users
  ```
- Show that excessive requests are blocked or rate-limited.

### 9. Helm Charts & Parameterized values.yaml
- Open and show `helm/user-service/values.yaml` and `helm/kong/values.yaml` with parameters.

### 10. Terraform (Optional)
- Show any Terraform files if used for infra provisioning.

### 11. Repository Structure
- Show the folder structure in your terminal or editor.

### 12. Documentation
- Open `README.md` and `ai-usage.md` and show the required sections.

## Deployment Instructions

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/) or any Kubernetes cluster
- [Helm 3](https://helm.sh/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Docker

### Steps

1. **Start Minikube:**
   ```sh
   minikube start
   ```

2. **Build and load the microservice Docker image:**
   ```sh
   eval $(minikube docker-env)
   cd /home/abhijit/Talentica-Assignment-4/microservice
   docker build -t user-service:latest .
   ```

3. **Deploy the microservice using Helm:**
   ```sh
   helm install user-service /home/abhijit/Talentica-Assignment-4/helm/user-service
   ```

4. **Deploy Kong using Helm:**
   ```sh
   helm repo add kong https://charts.konghq.com
   helm repo update
   helm install kong kong/kong -f /home/abhijit/Talentica-Assignment-4/helm/kong/values.yaml
   ```

5. **Apply Kong declarative configuration and custom plugins:**
   - Port-forward Kong Admin API:
     ```sh
     kubectl port-forward svc/kong-kong-admin 8001:8001 -n default
     ```
   - In another terminal, apply the config:
     ```sh
     curl -i -X POST http://localhost:8001/config \
       --data-binary @/home/abhijit/Talentica-Assignment-4/kong/kong.yaml \
       -H "Content-Type: application/yaml"
     ```

6. **Expose Kong proxy and test endpoints:**
   ```sh
   minikube service kong-kong-proxy -n default --url
   # Use the provided URL to access your APIs via Kong
   ```

### DDoS Protection (Demo Instructions)

To demonstrate DDoS protection:

1. Use the `hey` tool to simulate a large number of concurrent requests:
   ```sh
   hey -z 10s -c 50 http://127.0.0.1:38659/users
   ```

2. **Expected result:**  
   - Most requests should return HTTP 401 (Unauthorized) if no JWT is provided, or HTTP 429 (Too Many Requests) if rate limiting is triggered.
   - The service should remain responsive and not crash under load.

3. **What to show in the demo:**  
   - The summary output from `hey`, especially the "Status code distribution" (e.g., `[401] 203792 responses` or `[429] ... responses`).
   - Point out that the API remains available and protected even under simulated attack.

### How to Confirm DDoS Protection Using Console

1. **Run the DDoS simulation:**
   ```sh
   hey -z 10s -c 50 http://127.0.0.1:38659/users
   ```

2. **Observe the output:**  
   - Look for the `Status code distribution:` section.
   - You should see a large number of `401` (Unauthorized) or `429` (Too Many Requests) responses.

3. **Interpretation:**  
   - If you see mostly `401` responses, it means unauthorized requests are blocked.
   - If you use a valid JWT and see `429` responses, it means rate limiting is working.
   - The service should not crash or become unresponsive.

4. **Optional:**  
   - You can also monitor pod logs during the test:
     ```sh
     kubectl logs <kong-pod-name>
     kubectl logs <user-service-pod-name>
     ```
   - Look for errors or signs of overload (there should be none).

**If all these checks pass, your DDoS protection is confirmed via the console.**

### IP Whitelisting (How to Test Locally)

1. **Edit your Kong config to allow only a non-local IP (e.g., `8.8.8.8`):**
   ```yaml
   plugins:
     - name: ip-restriction
       config:
         allow:
           - 8.8.8.8
   ```
2. **Re-apply the Kong config:**
   ```sh
   kubectl port-forward svc/kong-kong-admin 8001:8001 -n default
   curl -i -X POST http://localhost:8001/config \
     --data-binary @/home/abhijit/kong/kong.yaml \
     -H "Content-Type: application/yaml"
   ```
3. **Try to access a protected endpoint from your local machine:**
   ```sh
   curl -H "Authorization: Bearer <VALID_JWT>" http://127.0.0.1:38659/users
   ```
4. **Expected result:**  
   You should receive HTTP 403 Forbidden or a message like `{"message":"Your IP address is not allowed"}`.

5. **Demo explanation:**  
   - "Since my local IP is not in the allow list, Kong blocks my request. In a real-world scenario, you would test from different machines or networks to demonstrate allowed and denied access."
