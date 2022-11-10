from flask import request
from gevent.pywsgi import WSGIServer
from app import create_app

app = create_app()

@app.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('X-Request-Id is required for client identification') 

http_server = WSGIServer((app.config["WSGI_HOST"], app.config["WSGI_PORT"]), app)
http_server.serve_forever()
