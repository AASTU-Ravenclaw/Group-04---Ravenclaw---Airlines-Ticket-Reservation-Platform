import os
import sys
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
try:
    from opentelemetry.instrumentation.djangorestframework import DjangoRestFrameworkInstrumentor
except ImportError:
    DjangoRestFrameworkInstrumentor = None

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

logger = logging.getLogger(__name__)

def setup_opentelemetry():
    service_name = os.environ.get("OTEL_SERVICE_NAME", "unknown-service")
    print(f"Setting up OpenTelemetry for service: {service_name}")
    
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.SERVICE_NAMESPACE: "airlines",
    })

    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_endpoint = os.environ.get('OTLP_ENDPOINT', 'http://otel-collector.observability.svc.cluster.local:4318/v1/traces')
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)

    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Add Console Exporter for debugging
    # trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    # Skip DjangoInstrumentor for workers (avoids command discovery issues)
    if service_name != 'booking-worker' and service_name != 'notification-worker':
        DjangoInstrumentor().instrument()
        if DjangoRestFrameworkInstrumentor:
            DjangoRestFrameworkInstrumentor().instrument()
            print("Instrumented Django and DRF")
        else:
            print("Instrumented Django (DRF instrumentation not found)")
    else:
        print("Skipping DjangoInstrumentor for worker")

    RequestsInstrumentor().instrument()
    
    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        try:
            Psycopg2Instrumentor().instrument(skip_dep_check=True)
            print("Instrumented Psycopg2 (skip_dep_check=True)")
        except TypeError:
            Psycopg2Instrumentor().instrument()
            print("Instrumented Psycopg2")
    except Exception as e:
        print(f"Skipping Psycopg2 instrumentation due to error: {e}")

setup_opentelemetry()
