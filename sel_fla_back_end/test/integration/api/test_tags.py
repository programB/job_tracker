import pytest


class TestHappyPaths:
    def test_should_get_all_existing_tags(self, httpx_test_client):
        response = httpx_test_client.get("/api/tags")
        assert response.status_code == 200
        received_tags = response.json()

        assert isinstance(received_tags, list) and all(
            isinstance(item, str) for item in received_tags
        )
        assert len(received_tags) == 3
        assert all(tag in ["Java", "Selenium", "Python"] for tag in received_tags)


@pytest.mark.xfail(reason="communication with the selenium selenium not yet implemented.")
def test_should_get_500error_if_server_not_healthy(httpx_test_client):
    assert False
