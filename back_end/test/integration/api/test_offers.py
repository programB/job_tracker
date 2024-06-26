from datetime import datetime

import pytest


@pytest.mark.parametrize("pplimit", [10, 20, 30])
class TestHappyPaths:
    def test_should_get_existing_offers(self, httpx_test_client, pplimit):
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": pplimit, "subpage": "1"}
        )
        assert response.status_code == 200
        ans = response.json()
        ans_info = ans["info"]
        assert ans_info["curr_subpage"] == 1
        assert ans_info["tot_subpages"] >= 1
        received_offers = ans["offers"]
        assert len(received_offers) == pplimit
        ISO8601_format = "%Y-%m-%dT%H:%M:%S"
        for offer in received_offers:
            if offer["title"].startswith("Test offer"):
                assert len(offer["tags"]) == 2
                assert all(
                    item in ["Java", "Selenium", "Python"] for item in offer["tags"]
                )
            else:
                # Other offers have no tags
                assert offer["tags"] == []
            assert isinstance(
                datetime.strptime(offer["posted"], ISO8601_format), datetime
            )
            assert isinstance(
                datetime.strptime(offer["collected"], ISO8601_format), datetime
            )
            assert offer["contracttype"] and isinstance(offer["contracttype"], str)
            assert offer["jobmode"] and isinstance(offer["jobmode"], str)
            assert offer["joblevel"] and isinstance(offer["joblevel"], str)
            assert "USD/mo" in offer["salary"]
            assert offer["detailsurl"].startswith("https:")
            assert isinstance(offer["tags"], list) and all(
                isinstance(item, str) for item in offer["tags"]
            )

    def test_should_get_all_offers_relying_on_default_value_of_subpage(
        self, httpx_test_client, pplimit
    ):
        # subpage should default to 1 if not passed in params
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": pplimit}
        )
        assert response.status_code == 200


class TestPerpagelimitSchemaViolations:
    def test_should_get_400error_when_required_params_missing(self, httpx_test_client):
        none_of_the_required = {}
        response = httpx_test_client.get("/api/offers", params=none_of_the_required)
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_perpagelimit", ["dog", 4.0])
    def test_should_get_400error_when_perpagelimit_of_invalid_type(
        self, httpx_test_client, invalid_perpagelimit
    ):
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": invalid_perpagelimit, "subpage": "1"}
        )
        assert response.status_code == 400

    def test_should_get_400error_when_perpagelimit_not_multipleof10(
        self, httpx_test_client
    ):
        pplimit = 9
        assert pplimit % 10 != 0
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": pplimit, "subpage": "1"}
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("pplimit", [0, 40])
    def test_should_get_400error_when_perpagelimit_outside_allowed_range(
        self, httpx_test_client, pplimit
    ):
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": pplimit, "subpage": "1"}
        )
        assert response.status_code == 400


class TestSubpageViolations:
    @pytest.mark.parametrize("invalid_subpage", ["dog", 4.0, -1])
    def test_should_get_400error_when_subpage_of_invalid_type(
        self, httpx_test_client, invalid_subpage
    ):
        response = httpx_test_client.get(
            "/api/offers", params={"perpagelimit": 10, "subpage": invalid_subpage}
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("invalid_subpage_request", [0])
    def test_should_get400error_if_subpage_less_then_1(
        self, httpx_test_client, invalid_subpage_request
    ):
        response = httpx_test_client.get(
            "/api/offers",
            params={"perpagelimit": 10, "subpage": invalid_subpage_request},
        )
        assert response.status_code == 400


def test_should_get_404error_when_pagination_out_of_range(httpx_test_client):
    not_existing_subpage = 9999
    response = httpx_test_client.get(
        "/api/offers", params={"perpagelimit": 10, "subpage": not_existing_subpage}
    )
    assert response.status_code == 404


@pytest.mark.xfail(reason="not yet implemented")
def test_should_get_500error_if_server_not_healthy(httpx_test_client):
    assert False
