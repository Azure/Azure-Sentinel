import json
import os

from shared_code.customized_logger.customized_json_logger import (
    get_customized_json_logger,
)

logger = get_customized_json_logger()


def _load_file(file_name):
    pwd = os.path.dirname(__file__)
    with open(f"{pwd}/data/{file_name}") as f:
        return json.load(f)


class MappingSet:
    mitre_tag_mapping = _load_file('mitre_tag_mapping.json')
    sae_tag_mapping = _load_file('sae_filter_mapping.json')
    operation_mapping = _load_file('operation_mapping.json')
    meta_key_mapping = _load_file('meta_key_mapping.json')
    file_true_type_mapping = _load_file('file_true_type_mapping.json')
    file_sub_true_type_mapping = _load_file('file_sub_true_type_mapping.json')


def transform_rca_task(xdr_customer_id, workbench_id, data):
    result = {'xdrCustomerID': xdr_customer_id, 'workbenchId': workbench_id}
    result.update(data)
    return result


def transform_rca_result(target_info, data):
    result = []
    link_array = data['chain']['links']
    (parent_set, event_set) = _convert_link(link_array)

    object_array = data['chain']['objects']

    obj_mapping = {
        'objectHashId': 'objectHashId',
        'eventId': 'eventId',
        'objectName': 'name',
        'isMatched': 'isMatched',
    }

    for obj_item in object_array:
        # append workbench info
        result_item = target_info.copy()
        # process object info
        for mapping_key in obj_mapping.keys():
            result_item[mapping_key] = obj_item[obj_mapping[mapping_key]]
        # process parent id
        obj_id = result_item['objectHashId']
        result_item['parentObjectId'] = (
            parent_set[obj_id] if obj_id in parent_set else None
        )
        # process object meta
        result_item['objectMeta'] = _convert_meta(obj_item['meta'])
        # process object event
        if obj_id in event_set:
            result_item['objectEvent'] = event_set[obj_id]
        result.append(result_item.copy())
    return result


def transform_oat_log(clp_id, log):
    _META_TRANSFROM_FIELDS = {
        'tags': _convert_tag,
        'processTrueType': _convert_true_type_int,
    }

    for field, convert_func in _META_TRANSFROM_FIELDS.items():
        if field in log:
            log[field] = convert_func(log[field])

    log['xdrCustomerId'] = clp_id
    return log


def _convert_true_type_int(type):
    key = str(type)
    if key in MappingSet.file_true_type_mapping:
        return MappingSet.file_true_type_mapping[key]
    else:
        logger.error(f'Key {type} not in FILE_TRUE_TYPE_MAPPING.')
        return type


def _convert_true_type(params):
    key = str(params[0])
    if key in MappingSet.file_true_type_mapping:
        return MappingSet.file_true_type_mapping[key]
    else:
        logger.error(f'Key {params[0]} not in FILE_TRUE_TYPE_MAPPING.')
        return params[0]


def _convert_sub_true_type(params):
    sub_true_type = str(params[0])
    true_type = str(params[1])
    if true_type in MappingSet.file_true_type_mapping:
        if true_type in MappingSet.file_sub_true_type_mapping:
            if sub_true_type in MappingSet.file_sub_true_type_mapping[true_type]:
                return MappingSet.file_sub_true_type_mapping[true_type][sub_true_type]

    logger.error(
        f'Connot find sub true type mapping. true_type: {true_type}, sub_true_type: {sub_true_type}'
    )
    return sub_true_type


def _convert_int(params):
    return (int)(params[0])


def _convert_link(link_array):
    parent_set = {}
    event_set = {}
    for link_item in link_array:
        link_item.pop('eventTime')
        if 'tags' in link_item:
            link_item['tags'] = _convert_tag(link_item['tags'])
        link_item['firstSeen'] = int(link_item['firstSeen'])
        link_item['lastSeen'] = int(link_item['lastSeen'])

        # mapping operation
        operation_key = str(link_item['operation'])
        if operation_key in MappingSet.operation_mapping:
            link_item['operation'] = MappingSet.operation_mapping[operation_key]
        else:
            logger.warning(f'operation: "{link_item["operation"]}" not in mapping set.')
        src_obj = link_item['srcObj']
        tar_obj = link_item['tarObj']

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
                    MappingSet.sae_tag_mapping[tag_key]['name']
                    if tag_key in MappingSet.sae_tag_mapping
                    else tag
                )
            elif tag.startswith("MITRE"):
                tag_key = tag[tag.index(".") + 1 :]
                value = (
                    MappingSet.mitre_tag_mapping[tag_key]['name']
                    if tag_key in MappingSet.mitre_tag_mapping
                    else tag
                )
            else:
                logger.warning(f'Tag {tag} not in Mapping set.')
                value = tag

            result.append({'name': tag, 'value': value})
    return result


def _convert_meta(meta_object):
    result = []

    _META_VALUE_FUNC = {
        'objectFirstSeen': [_convert_int],
        'objectLastSeen': [_convert_int],
        'processLaunchTime': [_convert_int],
        'processTrueType': [_convert_true_type],
        'processSubTrueType': [
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
                logger.error(f'Do not have function in _META_VALUE_FUNC: {name}')
        else:
            value = meta_object[key]

        result.append({'name': name, 'value': value})
    return result
