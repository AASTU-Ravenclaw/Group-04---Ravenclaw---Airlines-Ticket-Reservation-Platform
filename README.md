# Airline Ticket Reservation System

A distributed, event-driven microservices-based airline ticket reservation platform built with Django, RabbitMQ, MongoDB, and Docker.

---

## Overview

The system consists of three independent microservices communicating through an event-driven architecture:

- **Authentication Service** — User registration, login, JWT token issuance.
- **Flight Service** — Manages flights, schedules, pricing, and seat inventory.
- **Reservation Service** — Handles reservation requests using a saga-style workflow.
- **API Gateway** — Central entry point for routing, authentication, and request handling.

Each service owns its own MongoDB database and is deployed as a separate container.

---

## System Architecture (Summary)

- **API Gateway**
  - Validates JWTs
  - Routes requests to the appropriate microservice
  - Returns standardized error responses (403/404/503)

- **Microservices**
  - **Auth Service**  
    - Stores users  
    - Issues JWT  
  - **Flight Service**  
    - Flight catalog  
    - Seat counts  
    - Publishes `flight.updated` events  
  - **Reservation Service**  
    - Creates reservations  
    - Saga workflow: pending → confirmed/failed  
    - Listens to `flight.updated` events  

- **RabbitMQ Event Channels**
  - `reservation.created`
  - `reservation.confirmed`
  - `reservation.failed`
  - `flight.updated`

- **Data Storage**
  - Independent MongoDB per service  
  - Event-driven consistency  

---

##  Planned Folder Structure

```plaintext
.
├── gateway/
├── auth-service/
├── flight-service/
├── reservation-service/
├── frontend/
├── docker-compose.yml
├── docs/
└── README.md
```

## Technologies

Python (Django REST Framework)

RabbitMQ (event broker)

MongoDB (per-service database)

Docker & Docker Compose

JWT Authentication

Nginx or Express-based API Gateway

## Setup Instructions

These steps will be valid once the initial service skeletons are added.

### 1. Clone the Repository
```
git clone https://github.com/AASTU-Ravenclaw/Airlines-Ticket-Reservation-Platform.git
cd Airlines-Ticket-Reservation-Platform
```
### 2. Prerequisites

Make sure the following are installed:

- Python 3.10+

- Docker & Docker Compose

- Git

### 3. Environment Variables

Each service will contain its own environment file:

/auth-service/.env
/flight-service/.env
/reservation-service/.env
/gateway/.env

A .env.example file will be provided.

### 4. Start All Services
```
docker compose up --build
```

### 5. Stopping the System
```
docker compose down
```


## Documentation

Additional architecture diagrams, API specifications, and design documents will be included in the /docs directory as the project evolves.