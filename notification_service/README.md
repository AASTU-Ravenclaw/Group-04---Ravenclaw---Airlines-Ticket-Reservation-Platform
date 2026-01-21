# Notification Service — Running Tests in Kubernetes

## Prerequisites
- `kubectl` configured for the cluster
- Namespace: `airlines`
- Deployed `notification-service` pods

## Run Tests in Kubernetes
1) List pods and choose one:
```bash
kubectl get pods -n airlines -l app=notification-service -o name
# e.g., pod/notification-service-6555f59f-566hb
```
2) Run the test suite in the pod (uses in-memory SQLite for Django, Mongo is mocked in tests):
```bash
POD=notification-service-6555f59f-566hb
kubectl exec -n airlines $POD -- python manage.py test -v 2

## Local Development (Optional)
```bash
cd "/home/kaleb/Desktop/project copy (7)/notification_service"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py test -v 2
```
