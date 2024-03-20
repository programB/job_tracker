import json


class TestHappyPaths:
    def test_should_see_other_services_are_online(self, httpx_test_client):
        # During integration tests both selenium and database
        # are expected to be running and accepting jobs.
        response = httpx_test_client.get("/api/health")
        assert response.status_code == 200
        assert json.loads(response.text) == {
            "is_selenium_grid_healthy": True,
            "is_database_online": True,
        }
