# Airline Booking System

A microservices-based airline booking system with separate services for users, flights, bookings, and notifications.

## Architecture

- **User Service**: User authentication and management
- **Flight Service**: Flight and location management
- **Booking Service**: Booking operations and business logic
- **Notification Service**: Asynchronous notifications via RabbitMQ
- **Frontend**: React application with modern UI

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your actual values:
   - Database credentials
   - Django secret keys
   - Service API keys
   - Message broker URLs

## Running the Application

1. Start all services:
   ```bash
   docker-compose up --build
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:801
   - RabbitMQ Management: http://localhost:15672

## Database Migrations

To run Django migrations for the services when using Docker, execute the following commands after starting the services:

```bash
docker exec -it user_service python manage.py makemigrations
docker exec -it user_service python manage.py migrate

docker exec -it flight_service python manage.py makemigrations
docker exec -it flight_service python manage.py migrate

docker exec -it booking_service python manage.py makemigrations
docker exec -it booking_service python manage.py migrate
```

## Services

### Databases
- PostgreSQL for user, flight, and booking services
- MongoDB for notification service
- RabbitMQ for message queuing

### API Endpoints
- User Service: `/api/v1/auth`, `/api/v1/users`
- Flight Service: `/api/v1/flights`, `/api/v1/locations`
- Booking Service: `/api/v1/bookings`
- Notification Service: `/api/v1/notifications`
