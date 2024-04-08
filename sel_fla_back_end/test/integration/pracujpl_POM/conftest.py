"""Fixtures implicitly auto-imported by all POM tests"""

import logging
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest


# function context is required by the shared_datadir plugin
@pytest.fixture(scope="function")
def local_http_server(
    request, shared_datadir, http_test_server_url, http_test_server_port
):
    """Fixture starts local http server serving a html file from 'data' directory.

    The server spun up here will be running in a separate thread.

    This fixture uses pytest-datadir plugin (its shared_datadir fixture)
    to copy the contents of ./data directory, which contains the webpage
    with its assets (scripts, images, stylesheets), to a temporary directory
    that is removed after the test. This way one test can't, even accidentally,
    affect other tests by making lasting changes to the test data.

    http_test_server_url and http_test_server_url fixtures used here
    allow to pass url at which this server should be running when tests
    are being run in the docker environment.

    This fixture introspects modules from which test functions called it
    to find out which files should be served and what special properties
    to create on the yielded object.
    """

    # server_address = "localhost"
    # binding to 0.0.0.0 makes this server visible inside docker network
    # and reachable by the name given to the container running the test.
    # without having to pass a url.
    bind_address = "0.0.0.0"
    server_port = http_test_server_port or "8000"

    # Introspect requesting test module to get the html file name to serve
    # (This file must be present in the 'data' subdirectory.
    file_to_serve = getattr(request.module, "file_to_serve")

    # Introspect requesting test module to get the dictionary of the
    # special properties the resulting server object should end up having.
    special_properties = getattr(request.module, "special_properties")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=shared_datadir, **kwargs)

    class LocalServer(threading.Thread):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            for s_prop_name, s_prop_val in special_properties.items():
                setattr(self, s_prop_name, s_prop_val)

        if http_test_server_url:
            base_url = http_test_server_url + ":" + server_port
        else:
            base_url = "http://" + bind_address + ":" + server_port
        url = base_url + "/" + file_to_serve

        def run(self):
            # ThreadingHTTPServer requires port number to be passed as int not str
            self.server = ThreadingHTTPServer((bind_address, int(server_port)), Handler)
            self.server.serve_forever()

        def stop(self):
            self.server.shutdown()

    locsrv = LocalServer()
    locsrv.start()
    if locsrv.is_alive():  # technically the thread not the server itself
        logging.info("Local webserver running at: %s:%s", bind_address, server_port)
    else:
        logging.error("Local webserver failed to start !")
    # -- setup is done
    # logging.info("yielding control to the test function")

    yield locsrv

    # -- teardown
    locsrv.stop()
    if not locsrv.is_alive():
        logging.info("Local webserver successfully stopped")
    else:
        logging.error("Local webserver couldn't be stopped !")
