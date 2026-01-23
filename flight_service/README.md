# Flight Service — Running Tests in Kubernetes

This guide explains how to run the Django test suite for the flight-service inside a Kubernetes pod without modifying application code.

## Prerequisites
- `kubectl` configured to reach the cluster
- Namespace: `airlines`
- Deployed `flight-service` pods

## Run Tests in Kubernetes 
1) List pods and pick one:
```bash
kubectl get pods -n airlines -l app=flight-service -o name
# e.g., pod/flight-service-779f5f587c-bgvpd
```

2) Run the test suite in the pod (uses configured Postgres; creates a temp test DB):
```bash
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

- If you prefer to avoid Postgres during tests, force SQLite for that run only:
```bash
kubectl exec -n airlines $POD -- sh -lc 'DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2'
```

3) (Optional) Verify on the second replica:
```bash
POD=flight-service-779f5f587c-zzrzn
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

## Local Development (Optional)
```bash
cd "/home/kaleb/Desktop/project copy (7)/flight_service"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2
```

