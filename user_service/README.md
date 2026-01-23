# User Service — Running Tests in Kubernetes

This guide shows how to run the Django unit tests for the user-service directly inside a Kubernetes pod without modifying application code.

## Prerequisites
- `kubectl` configured for your cluster.
- Namespace: `airlines`.
- Deployed `user-service` pods running.

## Kubernetes (Recommended)

1) List user-service pods and pick one:

```bash
kubectl get pods -n airlines -l app=user-service -o name
# Example output:
# pod/user-service-6fcccd94c8-h77jc
# pod/user-service-6fcccd94c8-qsng9
```

2) Run the test suite in the pod:

```bash
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

- Django will create and destroy a temporary test database (e.g., `test_airlines_user`).
- If you prefer to avoid Postgres during tests, force SQLite for the test run only:

```bash
kubectl exec -n airlines $POD -- sh -lc 'DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2'
```

3) (Optional) Run on the second replica to verify consistency:

```bash
POD=user-service-6fcccd94c8-qsng9
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

## Local Development (Optional)
If you want to run tests locally without touching app code:

```bash
cd "/home/kaleb/Desktop/project copy (7)/user_service"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
DATABASE_URL=sqlite:///test.sqlite3 python manage.py test -v 2
```