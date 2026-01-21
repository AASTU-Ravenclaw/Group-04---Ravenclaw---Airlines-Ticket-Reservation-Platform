#!/bin/bash

# Start the Django server in the background
python manage.py runserver 0.0.0.0:8000 &

# Start the consumer
python manage.py runconsumer

# Wait for all background processes
wait