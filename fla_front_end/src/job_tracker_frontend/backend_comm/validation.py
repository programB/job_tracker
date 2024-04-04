from datetime import datetime

from .allowed_choices import bins, contract_types, job_levels, job_modes, tags


def check_inputs(
    i_start_date: datetime,
    i_end_date: datetime,
    i_binning: str,
    i_tags,
    i_contract_type,
    i_job_mode,
    i_job_level,
) -> None:
    """Checks API request parameters validity

    Returns None
    Raises AttributeError error if any of the parameters is invalid
    """

    if i_end_date < i_start_date:
        raise AttributeError("end date earlier than start date")
    if i_binning not in bins:
        raise AttributeError(
            (
                f"unknown binning requested {i_binning}, "
                f"allowed values are: {', '.join(bins)}"
            )
        )
    # TODO: imported tag list is populated only once when fronted app starts
    #       and will not be updated afterwards (although the dropdown in
    #       the UI gets updated every time the user clicks the submit button)
    #       this causes the code below to raise false errors if a tag that was
    #       not in the backend's database appeared there, was added to the
    #       dropdown during the uptime of the fronted and selected by the user.
    # for i_tag in i_tags:
    #     if i_tag and i_tag not in tags:
    #         raise AttributeError(
    #             (
    #                 f"unknown tag requested {i_tag}, "
    #                 f"allowed values are: {', '.join(tags)}"
    #             )
    #         )
    if i_contract_type and i_contract_type not in contract_types:
        raise AttributeError(
            (
                f"unknown contract type requested {i_contract_type}, "
                f"allowed values are: {', '.join(contract_types)}"
            )
        )
    if i_job_mode and i_job_mode not in job_modes:
        raise AttributeError(
            (
                f"unknown job mode requested {i_job_mode}, "
                f"allowed values are: {', '.join(job_modes)}"
            )
        )
    if i_job_level and i_job_level not in job_levels:
        raise AttributeError(
            (
                f"unknown job level requested {i_job_level}, "
                f"allowed values are: {', '.join(job_levels)}"
            )
        )
