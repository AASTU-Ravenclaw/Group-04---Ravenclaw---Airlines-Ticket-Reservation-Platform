import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.tracecontext import TraceContextTextMapPropagator
from opentelemetry.propagators.baggage import BaggagePropagator
try:
    from opentelemetry.instrumentation.djangorestframework import DjangoRestFrameworkInstrumentor
except ImportError:
    DjangoRestFrameworkInstrumentor = None

from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

def _configure_propagators():
    propagators = [TraceContextTextMapPropagator(), BaggagePropagator()]
    try:
        from opentelemetry.propagators.jaeger import JaegerPropagator
        propagators.append(JaegerPropagator())
    except Exception:
        pass
    try:
        from opentelemetry.propagators.b3 import B3MultiFormat
        propagators.append(B3MultiFormat())
    except Exception:
        pass
    set_global_textmap(CompositePropagator(propagators))


def setup_opentelemetry():
    return # Manual instrumentation disabled for auto-instrumentation
    _configure_propagators()
    service_name = os.environ.get("OTEL_SERVICE_NAME", "notification-service")
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

    if service_name != 'notification-worker':
        DjangoInstrumentor().instrument()
        if DjangoRestFrameworkInstrumentor:
            DjangoRestFrameworkInstrumentor().instrument()
    
    RequestsInstrumentor().instrument()
    PymongoInstrumentor().instrument()

# setup_opentelemetry()