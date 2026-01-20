# Flight Booking System

## Overview

This project is a microservices-based flight booking system that allows users to search for flights, make bookings, manage user accounts, and receive notifications. The system is designed for scalability and observability, with deployment orchestrated via Kubernetes.

## Architecture

The application follows a microservices architecture, consisting of multiple independent services that communicate via message queues (RabbitMQ) and APIs. It includes a frontend for user interaction and backend services for business logic.

### Key Components

- **Frontend**: A React-based web application served via Nginx, providing the user interface for flight search, booking, and account management.
- **Backend Services**:
  - **User Service**: Handles user authentication, registration, and profile management.
  - **Flight Service**: Manages flight data, search functionality, and flight-related operations.
  - **Booking Service**: Processes flight bookings, payment integration, and booking history.
  - **Notification Service**: Sends notifications to users via email or other channels, consuming messages from RabbitMQ.
- **Infrastructure**:
  - **Databases**: PostgreSQL for relational data (users, flights, bookings), MongoDB for notifications, Redis for caching.
  - **Message Queue**: RabbitMQ for asynchronous communication between services.
  - **Monitoring & Observability**: Prometheus for metrics, Grafana for dashboards, Jaeger for tracing, Loki for logging.
  - **Load Balancing & Ingress**: Traefik for routing and load balancing.
- **Deployment**: Kubernetes manifests for containerized deployment, including ConfigMaps, Secrets, Persistent Volumes, and Horizontal Pod Autoscalers (HPA).

## Project Structure

```
/home/kaleb/school/ravenclaw/project copy (7)/
├── booking_service/          # Django app for booking management
│   ├── bookings/             # App-specific code (models, views, etc.)
│   ├── config/               # Django settings and configuration
│   ├── dockerfile            # Docker build instructions
│   ├── manage.py             # Django management script
│   ├── requirements.txt      # Python dependencies
│   └── start.sh              # Startup script
├── flight_service/           # Django app for flight management
│   ├── config/               # Django settings
│   ├── flights/              # App-specific code
│   ├── dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   └── start.sh
├── user_service/             # Django app for user management
│   ├── config/               # Django settings
│   ├── users/                # App-specific code
│   ├── dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   └── start.sh
├── notification_service/     # Django app for notifications
│   ├── config/               # Django settings
│   ├── notifications/        # App-specific code
│   ├── dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   └── test_mq.py            # Message queue testing
├── frontend/                 # React frontend application
│   ├── src/                  # Source code
│   ├── dockerfile
│   ├── package.json          # Node.js dependencies
│   ├── vite.config.js        # Vite build configuration
│   └── nginx.conf            # Nginx configuration
├── k8s/                      # Kubernetes deployment manifests
│   ├── *-service.yaml        # Service-specific deployments
│   ├── configmap.yaml        # Configuration maps
│   ├── secrets.yaml          # Secrets management
│   ├── ingress.yaml          # Ingress configuration
│   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   ├── pvcs.yaml             # Persistent Volume Claims
│   └── ...                   # Other infrastructure configs
├── kubectl                   # kubectl configuration
├── targets.json              # Monitoring targets
└── traefik.yaml              # Traefik configuration
```

## Technologies Used

- **Backend**: Python, Django, Django REST Framework
- **Frontend**: React, Vite, Nginx
- **Databases**: PostgreSQL, MongoDB, Redis
- **Message Queue**: RabbitMQ
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana, Jaeger, Loki
- **Load Balancing**: Traefik
- **Observability**: OpenTelemetry (OTel)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (e.g., Minikube, Kind, or cloud provider)
- kubectl configured

### Installation

1. **Clone the repository** (if applicable) and navigate to the project root.

2. **Build and deploy services**:
   - Ensure all services are containerized using their respective Dockerfiles.
   - Apply Kubernetes manifests:
     ```
     kubectl apply -f k8s/
     ```

3. **Database Setup**:
   - PostgreSQL databases for user, flight, and booking services.
   - MongoDB for notifications.
   - Run migrations for Django services:
     ```
     # For each service (booking_service, flight_service, user_service, notification_service)
     cd <service_directory>
     python manage.py migrate
     ```

4. **Environment Variables**:
   - Configure secrets and configmaps in `k8s/secrets.yaml` and `k8s/configmap.yaml` for database connections, API keys, etc.

### Running the Application

- Access the frontend at the configured ingress URL (e.g., via Traefik).
- Services will be exposed internally via Kubernetes services.

### Monitoring

- Prometheus: Access metrics at configured endpoint.
- Grafana: Dashboards for visualization.
- Jaeger: Distributed tracing UI.
- Loki: Log aggregation.
