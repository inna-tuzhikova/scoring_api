import logging
from http.server import HTTPServer

from scoring_api.api.handler import MainHTTPHandler


logger = logging.getLogger(__name__)


def run_server(host: str = 'localhost', port: int = 8080) -> None:
    server = HTTPServer((host, port), MainHTTPHandler)
    logger.info('Starting server at http://%s:%s', host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
