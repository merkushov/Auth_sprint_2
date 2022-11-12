from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace import Span
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def init_tracer(app):
    trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": app.config["APP_NAME"]})))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=app.config["JAEGER_HOST"],
                agent_port=int(app.config["JAEGER_UDP"]),
            )
        )
    )

    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    tracer = FlaskInstrumentor().instrument_app(app) 

    return tracer

# Декоратор для трассировки отдельных вызовов или подзапрсов
def trace_export(span_name='span'):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(span_name):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
