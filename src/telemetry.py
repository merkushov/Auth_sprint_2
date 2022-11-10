from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider        
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def init_tracer(app):
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=app.config["JAEGER_HOST"],
                agent_port=int(app.config["JAEGER_PORT"]),
            )
        )
    )

    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    tracer = FlaskInstrumentor().instrument_app(app) 

    return tracer