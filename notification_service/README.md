# Notification Service — Running Tests in Kubernetes

This guide shows how to run the Django test suite for the notification-service in Kubernetes. Tests are part of the image after rebuilds; no `kubectl cp` is required.

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
```
3) (Optional) Verify on another replica:
```bash
POD=notification-service-6555f59f-6h5qp
kubectl exec -n airlines $POD -- python manage.py test -v 2
```

## Local Development (Optional)
```bash
cd "/home/kaleb/Desktop/project copy (7)/notification_service"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py test -v 2
```

## Notes & Troubleshooting
- Tests mock Mongo queries; no live Mongo or Kafka needed for logic coverage. Kafka startup logs are expected when the app initializes.
- Auth for APIs requires `X-User-Id`; cross-user access should return 403.
- Health check lives at `/health/`.
- If you see "NO TESTS RAN", ensure the image was rebuilt so the updated tests are present.
