from flask import request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import get_default_span_name
from config import app_config

from gevent.pywsgi import WSGIServer

from app import create_app

app = create_app()
jaeger_span = None


@app.before_request
def before_request():
    global jaeger_span

    request_id = request.headers.get('X-Request-Id')
    if app_config.telemetry_enabled and not request_id:
        raise RuntimeError('X-Request-Id is required for client identification')

    tracer = trace.get_tracer(__name__)
    jaeger_span = tracer.start_span(name='movie_catalog')
    jaeger_span.set_attribute('http.request_id', request_id)


@app.after_request
def after_request(response):
    global jaeger_span

    if jaeger_span:
        jaeger_span.end()
    return response


http_server = WSGIServer((app_config.wsgi_host, app_config.wsgi_port), app)
http_server.serve_forever()
