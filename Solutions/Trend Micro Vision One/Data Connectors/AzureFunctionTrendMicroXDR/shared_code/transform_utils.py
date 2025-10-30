import json
from typing import Any, List, Optional
import orjson
import os

from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)
from shared_code.models.oat import (
    ALLOWED_OAT_FIELDS,
    ALLOWED_OAT_DETAIL_FIELDS,
    OAT_OVERSIZED_FIELDS,
)
from shared_code.models.rca import RCA_RESULT_OVERSIZED_FIELDS
from shared_code.models.workbench import (
    ALLOWED_WORKBENCH_COLUMN,
    ALLOWED_WORKBENCH_DETAIL_COLUMN,
    XDR_INDICATORS_COLUMN_NAME,
    WB_OVERSIZED_FIELDS,
)


logger = get_customized_json_logger()

FIELD_BYTES_LIMIT = 32750


def _load_file(file_name):
    pwd = os.path.dirname(__file__)
    with open(f"{pwd}/data/{file_name}") as f:
        return json.load(f)


class MappingSet:
    mitre_tag_mapping = _load_file("mitre_tag_mapping.json")
    sae_tag_mapping = _load_file("sae_filter_mapping.json")
    operation_mapping = _load_file("operation_mapping.json")
    meta_key_mapping = _load_file("meta_key_mapping.json")
    file_true_type_mapping = _load_file("file_true_type_mapping.json")
    file_sub_true_type_mapping = _load_file("file_sub_true_type_mapping.json")


def _append_value_into_json_field(json_data, filed, value):
    if not filed in json_data:
        json_data[filed] = []

    if value and not value in json_data[filed]:
        json_data[filed].append(value)


def process_workbench_impact_scope(json_data):
    for impact_scope in json_data["impactScope"]:
        entity_type = impact_scope["entityType"]

        if entity_type == "account":
            account_value = impact_scope["entityValue"].split("\\")

            if len(account_value) == 2:
                account = account_value[1]
                _append_value_into_json_field(
                    json_data, "UserAccountNTDomain", account_value[0]
                )
            else:
                account = account_value[0]

            _append_value_into_json_field(json_data, "UserAccountName", account)
        elif entity_type == "host":
            _append_value_into_json_field(
                json_data, "HostHostName", impact_scope["entityValue"]["name"]
            )

    return json_data


def process_workbench_indicators(json_data):
    for indicator in json_data["indicators"]:
        object_type = indicator["objectType"]

        if object_type in XDR_INDICATORS_COLUMN_NAME.keys():
            _append_value_into_json_field(
                json_data,
                XDR_INDICATORS_COLUMN_NAME[object_type],
                indicator["objectValue"],
            )

    return json_data


def customize_workbench_json(clp_id, workbench_detail, workbench_record):

    xdr_log = {}

    for column in ALLOWED_WORKBENCH_COLUMN:
        xdr_log[column] = workbench_record[column] if column in workbench_record else ""

    for column in ALLOWED_WORKBENCH_DETAIL_COLUMN:
        xdr_log[column] = workbench_detail[column] if column in workbench_detail else ""

    xdr_log["xdrCustomerID"] = clp_id
    xdr_log["impactScope_Summary"] = json.dumps(workbench_detail["impactScope"])
    xdr_log = process_workbench_impact_scope(xdr_log)
    xdr_log = process_workbench_indicators(xdr_log)

    process_json_oversize(xdr_log, WB_OVERSIZED_FIELDS)

    return xdr_log


def transform_rca_task(xdr_customer_id, workbench_id, data):
    result = {"xdrCustomerID": xdr_customer_id, "workbenchId": workbench_id}
    result.update(data)
    return result


def transform_rca_result(target_info, data):
    result = []
    link_array = data["chain"]["links"]
    (parent_set, event_set) = _convert_link(link_array)

    object_array = data["chain"]["objects"]

    obj_mapping = {
        "objectHashId": "objectHashId",
        "eventId": "eventId",
        "objectName": "name",
        "isMatched": "isMatched",
    }

    for obj_item in object_array:
        # append workbench info
        result_item = target_info.copy()
        # process object info
        for mapping_key in obj_mapping.keys():
            result_item[mapping_key] = obj_item[obj_mapping[mapping_key]]
        # process parent id
        obj_id = result_item["objectHashId"]
        result_item["parentObjectId"] = (
            parent_set[obj_id] if obj_id in parent_set else None
        )
        # process object meta
        result_item["objectMeta"] = _convert_meta(obj_item["meta"])
        # process object event
        if obj_id in event_set:
            result_item["objectEvent"] = event_set[obj_id]

        process_json_oversize(result_item, RCA_RESULT_OVERSIZED_FIELDS)
        result.append(result_item)
    return result


def extract_allowed_oat_fields(oat_log: dict):
    filtered_oat_log = {"detail": {}}
    for field in ALLOWED_OAT_FIELDS:
        if field in oat_log:
            filtered_oat_log[field] = oat_log[field]

    for field in ALLOWED_OAT_DETAIL_FIELDS:
        if field in oat_log.get("detail", {}):
            filtered_oat_log["detail"][field] = oat_log["detail"][field]

    return filtered_oat_log


def translate_oat_fields(oat_log: dict):
    _META_TRANSFORM_FIELDS = {
        "tags": _convert_tag,
        "processTrueType": _convert_true_type_int,
    }
    for field, convert_func in _META_TRANSFORM_FIELDS.items():
        if field in oat_log:
            oat_log[field] = convert_func(oat_log[field])


def transform_oat_log(clp_id, log):
    log = extract_allowed_oat_fields(log)
    translate_oat_fields(log)

    log["xdrCustomerId"] = clp_id
    process_json_oversize(log, OAT_OVERSIZED_FIELDS)

    return log


def _convert_true_type_int(type):
    key = str(type)
    if key in MappingSet.file_true_type_mapping:
        return MappingSet.file_true_type_mapping[key]
    else:
        logger.error(f"Key {type} not in FILE_TRUE_TYPE_MAPPING.")
        return type


def _convert_true_type(params):
    key = str(params[0])
    if key in MappingSet.file_true_type_mapping:
        return MappingSet.file_true_type_mapping[key]
    else:
        logger.error(f"Key {params[0]} not in FILE_TRUE_TYPE_MAPPING.")
        return params[0]


def _convert_sub_true_type(params):
    sub_true_type = str(params[0])
    true_type = str(params[1])
    if true_type in MappingSet.file_true_type_mapping:
        if true_type in MappingSet.file_sub_true_type_mapping:
            if sub_true_type in MappingSet.file_sub_true_type_mapping[true_type]:
                return MappingSet.file_sub_true_type_mapping[true_type][sub_true_type]

    logger.error(
        f"Connot find sub true type mapping. true_type: {true_type}, sub_true_type: {sub_true_type}"
    )
    return sub_true_type


def _convert_int(params):
    return (int)(params[0])


def _convert_link(link_array):
    parent_set = {}
    event_set = {}
    for link_item in link_array:
        link_item.pop("eventTime")
        if "tags" in link_item:
            link_item["tags"] = _convert_tag(link_item["tags"])
        link_item["firstSeen"] = int(link_item["firstSeen"])
        link_item["lastSeen"] = int(link_item["lastSeen"])

        # mapping operation
        operation_key = str(link_item["operation"])
        if operation_key in MappingSet.operation_mapping:
            link_item["operation"] = MappingSet.operation_mapping[operation_key]
        else:
            logger.warning(f'operation: "{link_item["operation"]}" not in mapping set.')
        src_obj = link_item["srcObj"]
        tar_obj = link_item["tarObj"]

        if src_obj in event_set:
            event_set[src_obj].append(link_item.copy())
        else:
            event_set[src_obj] = [link_item.copy()]

        if tar_obj in parent_set:
            if parent_set[tar_obj] != src_obj:
                logger.warning(
                    f'target: "{tar_obj}" different in parent_set: {parent_set[tar_obj]}.'
                )
        parent_set[tar_obj] = src_obj
    return parent_set, event_set


def _convert_tag(tag_array):
    result = []

    if tag_array:
        for tag in tag_array:
            if tag.startswith("XSAE"):
                tag_key = tag[tag.index(".") + 1 :]
                value = (
                    MappingSet.sae_tag_mapping[tag_key]["name"]
                    if tag_key in MappingSet.sae_tag_mapping
                    else tag
                )
            elif tag.startswith("MITRE"):
                tag_key = tag[tag.index(".") + 1 :]
                value = (
                    MappingSet.mitre_tag_mapping[tag_key]["name"]
                    if tag_key in MappingSet.mitre_tag_mapping
                    else tag
                )
            else:
                logger.warning(f"Tag {tag} not in Mapping set.")
                value = tag

            result.append({"name": tag, "value": value})
    return result


def _convert_meta(meta_object):
    result = []

    _META_VALUE_FUNC = {
        "objectFirstSeen": [_convert_int],
        "objectLastSeen": [_convert_int],
        "processLaunchTime": [_convert_int],
        "processTrueType": [_convert_true_type],
        "processSubTrueType": [
            _convert_sub_true_type,
            "110",
        ],
    }

    for key in meta_object.keys():
        if key in MappingSet.meta_key_mapping:
            name = MappingSet.meta_key_mapping[key]
        else:
            # Unknown field name
            logger.warning(f'rca meta key: "{key}" not in mapping set.')
            name = key

        if name in _META_VALUE_FUNC:
            func_value_list = _META_VALUE_FUNC[name]
            params = [meta_object[key]]
            exec_func = None
            for item in func_value_list:
                if callable(item):
                    exec_func = item
                else:
                    params.append(meta_object[item])
            if exec_func:
                value = exec_func(params)
            else:
                logger.error(f"Do not have function in _META_VALUE_FUNC: {name}")
        else:
            value = meta_object[key]

        result.append({"name": name, "value": value})
    return result


def _trim_oversized_json(json_data: dict, field_name: str, field_data: Any) -> bool:
    """Check if the field data in (list, str) type is over the limit size.
    if field_data is list, check if the total size of the list is over the limit.
    if field_data is string, check if the size of the string is over the limit.

    Args:
        json_data (dict): json data
        field_name (str): field name
        field_data (Any): field data

    Returns:
        bool: if the field data is over the limit size
    """
    is_oversized = False
    if (
        isinstance(field_data, list)
        and len(orjson.dumps(field_data)) > FIELD_BYTES_LIMIT
    ):
        field_size = 0
        data_count = 0
        is_oversized = True
        for item in field_data:
            # item len and json sign: ","
            field_size += len(orjson.dumps(item)) + 1
            if field_size > FIELD_BYTES_LIMIT:
                logger.warning(
                    f"[process_field_over_size] {field_name} over size. "
                    f"data_count last: {data_count}. "
                    f"total_data_count: {len(field_data)}"
                )
                del field_data[data_count:]
                break
            data_count += 1
    elif (
        isinstance(field_data, str)
        and len(bytes_string := field_data.encode()) > FIELD_BYTES_LIMIT
    ):
        is_oversized = True
        logger.warning(
            f"[process_field_over_size] {field_name} over size. "
            f"field_size: {len(bytes_string)}."
        )
        field_data = bytes_string[:FIELD_BYTES_LIMIT].decode(errors="ignore")
        inner_field_keys = field_name.split(".")
        if len(inner_field_keys) == 1:
            json_data[inner_field_keys[0]] = field_data
        elif len(inner_field_keys) == 2:
            json_data[inner_field_keys[0]][inner_field_keys[1]] = field_data
        else:
            logger.error(f"[process_field_over_size] {field_name} depth is not supported.")

    return is_oversized


def process_json_oversize(
    json_data: dict, oversized_fields: Optional[List[List[str]]] = None
):
    """Do trimming if the field data in (list, str) type is over the limit size.
    If no oversized_fields provided, do nothing.

    Args:
        json_data (_type_): json data
    """
    if not oversized_fields:
        return

    for inner_fields in oversized_fields:
        field_data = json_data
        for field in inner_fields:
            field_data = field_data.get(field, {})

        is_oversized = False
        if field_data:
            is_oversized = _trim_oversized_json(json_data, ".".join(inner_fields), field_data)

        if is_oversized:
            json_data[".".join(inner_fields) + "_over_size"] = is_oversized
