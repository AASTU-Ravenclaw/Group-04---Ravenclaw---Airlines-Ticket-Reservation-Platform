# Booking Service — Running Tests in Kubernetes


## Prerequisites
- `kubectl` access to the cluster
- Namespace: `airlines`
- Deployed `booking-service` pods

## Run Tests in Kubernetes

1) List pods and choose one:
```bash
kubectl get pods -n airlines -l app=booking-service -o name
# e.g., pod/booking-service-6c5cf8cfc7-7cfhl
```

2) Run the tests in the pod (uses configured Postgres; Django will create a temp test DB):
```bash
POD=booking-service-6c5cf8cfc7-7cfhl
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

- If you prefer to avoid Postgres during tests, force SQLite for that run only:
```bash
kubectl exec -n airlines $POD -- sh -lc 'DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2'
```

## Local Development
```bash
cd "/home/kaleb/Desktop/project copy (7)/booking_service"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2
```
