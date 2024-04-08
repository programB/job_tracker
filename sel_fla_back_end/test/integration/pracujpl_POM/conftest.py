"""Fixtures implicitly auto-imported all POM tests"""

import logging
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest


# @pytest.fixture(scope="function")
# def local_server_fixture(
# @pytest.fixture
# def stored_results_page(
@pytest.fixture(scope="function")
def stored_results_page(
    request, shared_datadir, http_test_server_url, http_test_server_port
):
    """Fixture starts local http server serving a html file from data directory.

    The server spun up here will be running in a separate thread.

    This fixture uses pytest-datadir plugin (its shared_datadir fixture)
    to copy the contents of ./data directory, which contains the webpage
    with its assets (scripts, images, stylesheets), to a temporary directory
    that is removed after the test. This way one test can't, even accidentally,
    affect other tests by making lasting changes in the test data.

    http_test_server_url and http_test_server_url fixtures used here
    allow to pass url at which this server should be running when used
    in docker environment.

    Other arguments allow to add test-specific properties resulting object
    should poses.
    """

    # server_address = "localhost"
    # binding to 0.0.0.0 makes this server visible inside docker network
    # and reachable by the name given to the container running the test.
    bind_address = "0.0.0.0"
    # server_port = 8000 if not http_test_server_port else int(http_test_server_port)
    server_port = http_test_server_port or "8000"

    # Introspect requesting test module to get the html file name to serve
    # (This file must be present in the 'data' subdirectory.
    file_to_serve = getattr(request.module, "file_to_serve")
    logging.warning("file_to_serve is: %s (%s)", file_to_serve, type(file_to_serve))

    # file_marker = request.node.get_closest_marker("file_to_serve")
    # if file_marker is None:
    #     raise UnboundLocalError(
    #         "missing file_to_serve marker. What html did you intend to serve?"
    #     )
    # file_to_serve = file_marker.args[0]

    # Introspect requesting test module to get the dictionary of the
    # special properties the resulting server object should end up having.
    special_properties = getattr(request.module, "special_properties")
    logging.warning("special_properties is: %s (%s)", special_properties, type(special_properties))
    # properties_marker = request.node.get_closest_marker("special_properties")
    # if properties_marker is None:
    #     raise UnboundLocalError(
    #         "missing special_properties marker."
    #     )
    # special_properties = properties_marker.args[0]

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=shared_datadir, **kwargs)

    class LocalServer(threading.Thread):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            for s_prop_name, s_prop_val in special_properties.items():
                setattr(self, s_prop_name, s_prop_val)

        if http_test_server_url:
            print("I AM NOT NONE")
            base_url = http_test_server_url + ":" + server_port
        else:
            print("I AM NONE !!!!!")
            base_url = "http://" + bind_address + ":" + server_port
        url = base_url + "/" + file_to_serve

        def run(self):
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
    # logging.info("yielding control to the test function")
    # -- setup is done

    yield locsrv

    # -- teardown
    locsrv.stop()
    if not locsrv.is_alive():
        logging.info("Local webserver successfully stopped")
    else:
        logging.error("Local webserver couldn't be stopped !")
