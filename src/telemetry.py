import flask
from functools import wraps
from config import app_config


def init_tracer(app):
    if app_config.flask_env == "production":
        # Configure tracer for production - requires opentelemetry

        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter

        trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": app_config.app_name})))
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=app_config.jaeger_host,
                    agent_port=int(app_config.jaeger_udp),
                )
            )
        )

        # Чтобы видеть трейсы в консоли
        # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        tracer = FlaskInstrumentor().instrument_app(app) 

        return tracer

# Декоратор для трассировки отдельных вызовов или подзапрсов
def trace_export(span_name='span'):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
            if app_config.flask_env == 'production':
                from opentelemetry import trace
                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span(span_name):
                    result = func(*args, **kwargs)
                return result
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
