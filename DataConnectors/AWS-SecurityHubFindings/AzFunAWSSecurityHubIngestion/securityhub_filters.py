import ast

import botocore.session
from botocore.exceptions import ParamValidationError
from botocore.validate import validate_parameters


INVALID_FILTER_MESSAGE = (
    "SecurityHubFilters must be a valid AWS Security Hub Filters dictionary."
)


def parse_securityhub_filters(filter_value):
    parse_failed = False
    try:
        filters = ast.literal_eval(filter_value)
    except (SyntaxError, ValueError, TypeError):
        parse_failed = True

    if parse_failed or not isinstance(filters, dict):
        raise ValueError(INVALID_FILTER_MESSAGE)

    validation_failed = False
    try:
        service_model = botocore.session.get_session().get_service_model("securityhub")
        input_shape = service_model.operation_model("GetFindings").input_shape
        validate_parameters({"Filters": filters}, input_shape)
        validation_failed = any(
            not filter_entries
            or any(
                not isinstance(filter_entry, dict) or not filter_entry
                for filter_entry in filter_entries
            )
            for filter_entries in filters.values()
        )
    except (ParamValidationError, TypeError):
        validation_failed = True

    if validation_failed:
        raise ValueError(INVALID_FILTER_MESSAGE)

    return filters
