# Kubernetes Setup for Airlines Project

This directory contains Kubernetes manifests equivalent to the docker-compose setup.

## Prerequisites
- A Kubernetes cluster (e.g., Minikube, EKS, etc.)
- kubectl configured
- Docker images built and pushed for the services:
  - user-service:latest
  - flight-service:latest
  - booking-service:latest
  - notification-service:latest
  - frontend:latest

## Setup Instructions

1. Create the namespace:
   ```
   kubectl apply -f namespace.yaml
   ```

2. Update the secrets.yaml with base64 encoded values for your environment variables.

3. Apply the manifests in order:
   ```
   kubectl apply -f secrets.yaml
   kubectl apply -f configmap.yaml
   kubectl apply -f pvcs.yaml
   kubectl apply -f traefik.yaml
   kubectl apply -f rabbitmq.yaml
   kubectl apply -f postgres-user.yaml
   kubectl apply -f postgres-flight.yaml
   kubectl apply -f postgres-booking.yaml
   kubectl apply -f mongo-notification.yaml
   kubectl apply -f redis.yaml
   kubectl apply -f user-service.yaml
   kubectl apply -f flight-service.yaml
   kubectl apply -f booking-service.yaml
   kubectl apply -f notification-service.yaml
   kubectl apply -f frontend.yaml
   ```

4. Check the status:
   ```
   kubectl get pods -n airlines
   kubectl get services -n airlines
   ```

5. Access the application:
   - Traefik dashboard: Get the external IP of traefik service, port 8080
   - API Gateway: External IP of traefik service, port 80
   - Frontend: If exposed separately, or via traefik
