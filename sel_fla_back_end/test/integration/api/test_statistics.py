from datetime import date, datetime, timedelta

import pytest


def iterate_months(start_date, end_date):
    """Yields timestamp of 1st day of every month between start and end dates

    Time is always set to 00:00:00
    Range includes both start_date and end_date
    """
    year = start_date.year
    month = start_date.month
    while True:
        current = datetime(year, month, 1)
        yield current
        if current.month == end_date.month and current.year == end_date.year:
            break
        else:
            month = ((month + 1) % 12) or 12
            if month == 1:
                year += 1


class TestHappyPaths:
    @pytest.mark.parametrize(
        "sd, ed", [("2023-01-01", "2023-12-31"), ("2023-05-13", "2023-10-22")]
    )
    def test_should_get_year_statistics_for_single_year(
        self, httpx_test_client, sd, ed
    ):
        binning = "year"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) and len(data) == 1
        assert data[0]["date"] == "2023-01-01"  # beginning of the year
        assert data[0]["count"] == 1000  # all offers in the year 2023

    def test_should_get_year_statistics_for_multiple_years(self, httpx_test_client):
        sd = "2023-01-01"
        ed = "2024-12-31"
        binning = "year"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) and len(data) == 2
        assert data[0]["date"] == "2023-01-01"  # beginning of the year
        assert data[0]["count"] == 1000  # all offers in the year 2023
        assert data[1]["date"] == "2024-01-01"  # beginning of the year
        assert data[1]["count"] == 2  # all offers posted in 2024

    @pytest.mark.parametrize(
        "sd, ed", [("2023-09-01", "2023-09-30"), ("2023-09-13", "2023-09-22")]
    )
    def test_should_get_month_statistics_for_single_month(
        self, httpx_test_client, sd, ed
    ):
        binning = "month"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) and len(data) == 1
        assert data[0]["date"] == "2023-09-01"  # beginning of the month
        assert data[0]["count"] == 528  # all offers in September of 2023

    @pytest.mark.parametrize(
        "sd, ed, expected_counts",
        [
            (
                date(2023, 1, 1),
                date(2024, 12, 31),
                # test offers by posted date
                # 0 (Jan-Aug 2023) 528 (Sept) 472 (Oct) 0 (Nov-Dec)
                # 2 (Jan.2024) 0 (Feb-Dec.2024)
                8 * [0] + [528, 472] + 2 * [0] + [2] + 11 * [0],
            ),
            (
                date(2023, 7, 17),
                date(2024, 4, 11),
                # 0 (Jul-Aug 2023) 528 (Sept) 472 (Oct) 0 (Nov-Dec)
                # 2 (Jan.2024) 0 (Feb-Mar.2024)
                2 * [0] + [528, 472] + 2 * [0] + [2] + 3 * [0],
            ),
        ],
    )
    def test_should_get_month_statistics_across_multiple_years(
        self, httpx_test_client, sd, ed, expected_counts
    ):
        # sd = "2023-01-01"
        # ed = "2024-12-31"
        binning = "month"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(expected_counts)
        first_day_of_month = iterate_months(sd, ed)
        for i, dp in enumerate(data):
            assert dp["date"] == next(first_day_of_month).date().isoformat()
            assert dp["count"] == expected_counts[i]

    @pytest.mark.parametrize(
        "sd, ed, expected_counts",
        [
            (
                date(2023, 9, 21),
                date(2023, 9, 25),
                # test offers by posted date
                [0, 0, 0, 0, 0],
            ),
            (
                date(2023, 10, 20),
                date(2024, 1, 16),
                # 27 20.10.2023 , 1 6.01.2024, 1 9.01.2024
                [27] + 77 * [0] + [1] + [0] + [0] + [1] + 7 * [0],
            ),
        ],
    )
    def test_should_get_day_statistics_for_single_month(
        self, httpx_test_client, sd, ed, expected_counts
    ):
        binning = "day"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
            },
        )
        # print(response.text)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(expected_counts)
        for i, dp in enumerate(data):
            assert dp["date"] == (sd + timedelta(days=i)).isoformat()
            assert dp["count"] == expected_counts[i]

    @pytest.mark.parametrize(
        "the_same_date, binning, expected_counts",
        [
            ("2023-09-09", "day", 22),
            ("2023-09-09", "month", 528),
            ("2023-09-09", "year", 1000),
        ],
    )
    def test_should_get_statistics_if_start_and_end_date_the_same(
        self, httpx_test_client, the_same_date, binning, expected_counts
    ):
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": the_same_date,
                "end_date": the_same_date,
                "binning": binning,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["count"] == expected_counts

    def test_should_get_statistics_with_additional_criteria(self, httpx_test_client):
        sd = "2023-09-01"
        ed = "2023-09-30"
        binning = "month"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
                "contract_type": "full time",
                # job_mode is not yet implemented
                "job_level": "junior",
            },
        )
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["date"] == "2023-09-01"
        assert data[0]["count"] == 101

    @pytest.mark.parametrize(
        "tags, expected_counts",
        [
            ([], 101),
            (["Python", "Java"], 0),
        ],
    )
    def test_should_get_statistics_when_criteria_include_tags(
        self, httpx_test_client, tags, expected_counts
    ):
        sd = "2023-09-01"
        ed = "2023-09-30"
        binning = "month"
        response = httpx_test_client.get(
            "/api/statistics",
            params={
                "start_date": sd,
                "end_date": ed,
                "binning": binning,
                "contract_type": "full time",
                # job_mode is not yet implemented
                "job_level": "junior",
                "tags": tags,
            },
        )
        # print(response.text)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["date"] == "2023-09-01"
        assert data[0]["count"] == expected_counts


class TestDateParametersSchemaViolations:
    @pytest.mark.parametrize(
        "some_required_params_missing",
        [
            {"end_date": "2023-09-30", "binning": "month"},
            {"start_date": "2023-09-01", "binning": "month"},
            {"start_date": "2023-09-01", "end_date": "2023-09-30"},
        ],
    )
    def test_should_get_400error_when_required_params_missing(
        self, httpx_test_client, some_required_params_missing
    ):

        response = httpx_test_client.get(
            "/api/statistics",
            params=some_required_params_missing,
        )
        assert response.status_code == 400

    @pytest.mark.parametrize(
        "some_invalid_required_params",
        [
            {"start_date": "2023-09-00", "end_date": "2023-09-30", "binning": "month"},
            {"start_date": "2023-09-11", "end_date": "2023-09-77", "binning": "month"},
            {"start_date": "2023-09-01", "end_date": "2023-09-30", "binning": "dog"},
        ],
    )
    def test_should_get_400error_when_invalid_date_passed(
        self, httpx_test_client, some_invalid_required_params
    ):
        response = httpx_test_client.get(
            "/api/statistics",
            params=some_invalid_required_params,
        )
        print(response.text)
        assert response.status_code == 400


def test_should_get_400error_when_end_date_eariler_then_start_date(httpx_test_client):
    sd = "2023-09-30"
    ed = "2023-09-01"
    binning = "month"
    response = httpx_test_client.get(
        "/api/statistics",
        params={
            "start_date": sd,
            "end_date": ed,
            "binning": binning,
        },
    )
    assert response.status_code == 400


@pytest.mark.xfail(reason="not yet implemented")
def test_should_get_500error_if_server_not_healthy(httpx_test_client):
    assert False
