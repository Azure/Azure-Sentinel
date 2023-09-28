"""Python APIs for STIX 2 Object-based Semantic Equivalence and Similarity."""
import collections
import itertools
import logging
import time

from ...datastore import DataSource, DataStoreMixin, Filter
from ...utils import STIXdatetime, parse_into_datetime
from ..pattern import equivalent_patterns

logger = logging.getLogger(__name__)


def object_equivalence(
    obj1, obj2, prop_scores={}, threshold=70, ds1=None,
    ds2=None, ignore_spec_version=False,
    versioning_checks=False, max_depth=1, **weight_dict
):
    """This method returns a true/false value if two objects are semantically equivalent.
    Internally, it calls the object_similarity function and compares it against the given
    threshold value.

    Args:
        obj1: A stix2 object instance
        obj2: A stix2 object instance
        prop_scores: A dictionary that can hold individual property scores,
            weights, contributing score, matching score and sum of weights.
        threshold: A numerical value between 0 and 100 to determine the minimum
            score to result in successfully calling both objects equivalent. This
            value can be tuned.
        ds1 (optional): A DataStore object instance from which to pull related objects
        ds2 (optional): A DataStore object instance from which to pull related objects
        ignore_spec_version: A boolean indicating whether to test object types
            that belong to different spec versions (STIX 2.0 and STIX 2.1 for example).
            If set to True this check will be skipped.
        versioning_checks: A boolean indicating whether to test multiple revisions
            of the same object (when present) to maximize similarity against a
            particular version. If set to True the algorithm will perform this step.
        max_depth: A positive integer indicating the maximum recursion depth the
            algorithm can reach when de-referencing objects and performing the
            object_similarity algorithm.
        weight_dict: A dictionary that can be used to override what checks are done
            to objects in the similarity process.

    Returns:
        bool: True if the result of the object similarity is greater than or equal to
            the threshold value. False otherwise.

    Warning:
        Object types need to have property weights defined for the similarity process.
        Otherwise, those objects will not influence the final score. The WEIGHTS
        dictionary under `stix2.equivalence.object` can give you an idea on how to add
        new entries and pass them via the `weight_dict` argument. Similarly, the values
        or methods can be fine tuned for a particular use case.

    Note:
        Default weight_dict:

        .. include:: ../../similarity_weights.rst

    Note:
        This implementation follows the Semantic Equivalence Committee Note.
        see `the Committee Note <link here>`__.

    """
    similarity_result = object_similarity(
        obj1, obj2, prop_scores, ds1, ds2, ignore_spec_version,
        versioning_checks, max_depth, **weight_dict
    )
    if similarity_result >= threshold:
        return True
    return False


def object_similarity(
    obj1, obj2, prop_scores={}, ds1=None, ds2=None,
    ignore_spec_version=False, versioning_checks=False,
    max_depth=1, **weight_dict
):
    """This method returns a measure of similarity depending on how
    similar the two objects are.

    Args:
        obj1: A stix2 object instance
        obj2: A stix2 object instance
        prop_scores: A dictionary that can hold individual property scores,
            weights, contributing score, matching score and sum of weights.
        ds1 (optional): A DataStore object instance from which to pull related objects
        ds2 (optional): A DataStore object instance from which to pull related objects
        ignore_spec_version: A boolean indicating whether to test object types
            that belong to different spec versions (STIX 2.0 and STIX 2.1 for example).
            If set to True this check will be skipped.
        versioning_checks: A boolean indicating whether to test multiple revisions
            of the same object (when present) to maximize similarity against a
            particular version. If set to True the algorithm will perform this step.
        max_depth: A positive integer indicating the maximum recursion depth the
            algorithm can reach when de-referencing objects and performing the
            object_similarity algorithm.
        weight_dict: A dictionary that can be used to override what checks are done
            to objects in the similarity process.

    Returns:
        float: A number between 0.0 and 100.0 as a measurement of similarity.

    Warning:
        Object types need to have property weights defined for the similarity process.
        Otherwise, those objects will not influence the final score. The WEIGHTS
        dictionary under `stix2.equivalence.object` can give you an idea on how to add
        new entries and pass them via the `weight_dict` argument. Similarly, the values
        or methods can be fine tuned for a particular use case.

    Note:
        Default weight_dict:

        .. include:: ../../similarity_weights.rst

    Note:
        This implementation follows the Semantic Equivalence Committee Note.
        see `the Committee Note <link here>`__.

    """
    weights = WEIGHTS.copy()

    if weight_dict:
        weights.update(weight_dict)

    weights["_internal"] = {
        "ignore_spec_version": ignore_spec_version,
        "versioning_checks": versioning_checks,
        "ds1": ds1,
        "ds2": ds2,
        "max_depth": max_depth,
    }

    type1, type2 = obj1["type"], obj2["type"]

    if type1 != type2:
        raise ValueError('The objects to compare must be of the same type!')

    if ignore_spec_version is False and obj1.get("spec_version", "2.0") != obj2.get("spec_version", "2.0"):
        raise ValueError('The objects to compare must be of the same spec version!')

    try:
        weights[type1]
    except KeyError:
        logger.warning("'%s' type has no 'weights' dict specified & thus no object similarity method to call!", type1)
        sum_weights = matching_score = 0
    else:
        try:
            method = weights[type1]["method"]
        except KeyError:
            logger.debug("Starting object similarity process between: '%s' and '%s'", obj1["id"], obj2["id"])
            matching_score = 0.0
            sum_weights = 0.0

            for prop in weights[type1]:
                if check_property_present(prop, obj1, obj2):
                    w = weights[type1][prop][0]
                    comp_funct = weights[type1][prop][1]
                    prop_scores[prop] = {}

                    if comp_funct == partial_timestamp_based:
                        contributing_score = w * comp_funct(obj1[prop], obj2[prop], weights[type1]["tdelta"])
                    elif comp_funct == partial_location_distance:
                        threshold = weights[type1]["threshold"]
                        contributing_score = w * comp_funct(obj1["latitude"], obj1["longitude"], obj2["latitude"], obj2["longitude"], threshold)
                    elif comp_funct == reference_check or comp_funct == list_reference_check:
                        if max_depth > 0:
                            weights["_internal"]["max_depth"] = max_depth - 1
                            ds1, ds2 = weights["_internal"]["ds1"], weights["_internal"]["ds2"]
                            if _datastore_check(ds1, ds2):
                                contributing_score = w * comp_funct(obj1[prop], obj2[prop], ds1, ds2, **weights)
                            elif comp_funct == reference_check:
                                comp_funct = exact_match
                                contributing_score = w * comp_funct(obj1[prop], obj2[prop])
                            elif comp_funct == list_reference_check:
                                comp_funct = partial_list_based
                                contributing_score = w * comp_funct(obj1[prop], obj2[prop])
                            prop_scores[prop]["check_type"] = comp_funct.__name__
                        else:
                            continue  # prevent excessive recursion
                        weights["_internal"]["max_depth"] = max_depth
                    else:
                        contributing_score = w * comp_funct(obj1[prop], obj2[prop])

                    sum_weights += w
                    matching_score += contributing_score

                    prop_scores[prop]["weight"] = w
                    prop_scores[prop]["contributing_score"] = contributing_score
                    logger.debug("'%s' check -- weight: %s, contributing score: %s", prop, w, contributing_score)

            prop_scores["matching_score"] = matching_score
            prop_scores["sum_weights"] = sum_weights
            logger.debug("Matching Score: %s, Sum of Weights: %s", matching_score, sum_weights)
        else:
            logger.debug("Starting object similarity process between: '%s' and '%s'", obj1["id"], obj2["id"])
            try:
                matching_score, sum_weights = method(obj1, obj2, prop_scores, **weights[type1])
            except TypeError:
                # method doesn't support detailed output with prop_scores
                matching_score, sum_weights = method(obj1, obj2, **weights[type1])
            logger.debug("Matching Score: %s, Sum of Weights: %s", matching_score, sum_weights)

    if sum_weights <= 0:
        return 0
    equivalence_score = (matching_score / sum_weights) * 100.0
    return equivalence_score


def check_property_present(prop, obj1, obj2):
    """Helper method checks if a property is present on both objects."""
    if prop == "longitude_latitude":
        if all(x in obj1 and x in obj2 for x in ('latitude', 'longitude')):
            return True
    elif prop in obj1 and prop in obj2:
        return True
    return False


def partial_timestamp_based(t1, t2, tdelta):
    """Performs a timestamp-based matching via checking how close one timestamp is to another.

    Args:
        t1: A datetime string or STIXdatetime object.
        t2: A datetime string or STIXdatetime object.
        tdelta (float): A given time delta. This number is multiplied by 86400 (1 day) to
            extend or shrink your time change tolerance.

    Returns:
        float: Number between 0.0 and 1.0 depending on match criteria.

    """
    if not isinstance(t1, STIXdatetime):
        t1 = parse_into_datetime(t1)
    if not isinstance(t2, STIXdatetime):
        t2 = parse_into_datetime(t2)
    t1, t2 = time.mktime(t1.timetuple()), time.mktime(t2.timetuple())
    result = 1 - min(abs(t1 - t2) / (86400 * tdelta), 1)
    logger.debug("--\t\tpartial_timestamp_based '%s' '%s' tdelta: '%s'\tresult: '%s'", t1, t2, tdelta, result)
    return result


def partial_list_based(l1, l2):
    """Performs a partial list matching via finding the intersection between
    common values. Repeated values are counted only once. This method can be
    used for *_refs equality checks when de-reference is not possible.

    Args:
        l1: A list of values.
        l2: A list of values.

    Returns:
        float: 1.0 if the value matches exactly, 0.0 otherwise.

    """
    l1_set, l2_set = set(l1), set(l2)
    result = len(l1_set.intersection(l2_set)) / max(len(l1_set), len(l2_set))
    logger.debug("--\t\tpartial_list_based '%s' '%s'\tresult: '%s'", l1, l2, result)
    return result


def exact_match(val1, val2):
    """Performs an exact value match based on two values. This method can be
    used for *_ref equality check when de-reference is not possible.

    Args:
        val1: A value suitable for an equality test.
        val2: A value suitable for an equality test.

    Returns:
        float: 1.0 if the value matches exactly, 0.0 otherwise.

    """
    result = 0.0
    if val1 == val2:
        result = 1.0
    logger.debug("--\t\texact_match '%s' '%s'\tresult: '%s'", val1, val2, result)
    return result


def partial_string_based(str1, str2):
    """Performs a partial string match using the Jaro-Winkler distance algorithm.

    Args:
        str1: A string value to check.
        str2: A string value to check.

    Returns:
        float: Number between 0.0 and 1.0 depending on match criteria.

    """
    from rapidfuzz import fuzz
    result = fuzz.token_sort_ratio(str1, str2)
    logger.debug("--\t\tpartial_string_based '%s' '%s'\tresult: '%s'", str1, str2, result)
    return result / 100.0


def custom_pattern_based(pattern1, pattern2):
    """Performs a matching on Indicator Patterns.

    Args:
        pattern1: An Indicator pattern
        pattern2: An Indicator pattern

    Returns:
        float: Number between 0.0 and 1.0 depending on match criteria.

    """
    return equivalent_patterns(pattern1, pattern2)


def partial_external_reference_based(ext_refs1, ext_refs2):
    """Performs a matching on External References.

    Args:
        ext_refs1: A list of external references.
        ext_refs2: A list of external references.

    Returns:
        float: Number between 0.0 and 1.0 depending on matches.

    """
    allowed = {"veris", "cve", "capec", "mitre-attack"}
    matches = 0

    ref_pairs = itertools.chain(
        itertools.product(ext_refs1, ext_refs2),
    )

    for ext_ref1, ext_ref2 in ref_pairs:
        sn_match = False
        ei_match = False
        url_match = False
        source_name = None

        if check_property_present("source_name", ext_ref1, ext_ref2):
            if ext_ref1["source_name"] == ext_ref2["source_name"]:
                source_name = ext_ref1["source_name"]
                sn_match = True
        if check_property_present("external_id", ext_ref1, ext_ref2):
            if ext_ref1["external_id"] == ext_ref2["external_id"]:
                ei_match = True
        if check_property_present("url", ext_ref1, ext_ref2):
            if ext_ref1["url"] == ext_ref2["url"]:
                url_match = True

        # Special case: if source_name is a STIX defined name and either
        # external_id or url match then its a perfect match and other entries
        # can be ignored.
        if sn_match and (ei_match or url_match) and source_name in allowed:
            result = 1.0
            logger.debug(
                "--\t\tpartial_external_reference_based '%s' '%s'\tresult: '%s'",
                ext_refs1, ext_refs2, result,
            )
            return result

        # Regular check. If the source_name (not STIX-defined) or external_id or
        # url matches then we consider the entry a match.
        if (sn_match or ei_match or url_match) and source_name not in allowed:
            matches += 1

    result = matches / max(len(ext_refs1), len(ext_refs2))
    logger.debug(
        "--\t\tpartial_external_reference_based '%s' '%s'\tresult: '%s'",
        ext_refs1, ext_refs2, result,
    )
    return result


def partial_location_distance(lat1, long1, lat2, long2, threshold):
    """Given two coordinates perform a matching based on its distance using the Haversine Formula.

    Args:
        lat1: Latitude value for first coordinate point.
        lat2: Latitude value for second coordinate point.
        long1: Longitude value for first coordinate point.
        long2: Longitude value for second coordinate point.
        threshold (float): A kilometer measurement for the threshold distance between these two points.

    Returns:
        float: Number between 0.0 and 1.0 depending on match.

    """
    from haversine import Unit, haversine
    distance = haversine((lat1, long1), (lat2, long2), unit=Unit.KILOMETERS)
    result = 1 - (distance / threshold)
    logger.debug(
        "--\t\tpartial_location_distance '%s' '%s' threshold: '%s'\tresult: '%s'",
        (lat1, long1), (lat2, long2), threshold, result,
    )
    return result


def _versioned_checks(ref1, ref2, ds1, ds2, **weights):
    """Checks multiple object versions if present in graph.
    Maximizes for the similarity score of a particular version."""
    results = {}

    pairs = _object_pairs(
        _bucket_per_type(ds1.query([Filter("id", "=", ref1)])),
        _bucket_per_type(ds2.query([Filter("id", "=", ref2)])),
        weights,
    )
    ignore_spec_version = weights["_internal"]["ignore_spec_version"]
    versioning_checks = weights["_internal"]["versioning_checks"]
    max_depth = weights["_internal"]["max_depth"]

    for object1, object2 in pairs:
        result = object_similarity(
            object1, object2, ds1=ds1, ds2=ds2,
            ignore_spec_version=ignore_spec_version,
            versioning_checks=versioning_checks,
            max_depth=max_depth, **weights,
        )
        if ref1 not in results:
            results[ref1] = {"matched": ref2, "value": result}
        elif result > results[ref1]["value"]:
            results[ref1] = {"matched": ref2, "value": result}

    result = results.get(ref1, {}).get("value", 0.0)
    logger.debug(
        "--\t\t_versioned_checks '%s' '%s'\tresult: '%s'",
        ref1, ref2, result,
    )
    return result


def reference_check(ref1, ref2, ds1, ds2, **weights):
    """For two references, de-reference the object and perform object_similarity.
    The score influences the result of an edge check."""
    type1, type2 = ref1.split("--")[0], ref2.split("--")[0]
    result = 0.0

    if type1 == type2 and type1 in weights:
        ignore_spec_version = weights["_internal"]["ignore_spec_version"]
        versioning_checks = weights["_internal"]["versioning_checks"]
        max_depth = weights["_internal"]["max_depth"]
        if versioning_checks:
            result = _versioned_checks(ref1, ref2, ds1, ds2, **weights) / 100.0
        else:
            o1, o2 = ds1.get(ref1), ds2.get(ref2)
            if o1 and o2:
                result = object_similarity(
                    o1, o2, ds1=ds1, ds2=ds2,
                    ignore_spec_version=ignore_spec_version,
                    versioning_checks=versioning_checks,
                    max_depth=max_depth, **weights,
                ) / 100.0

    logger.debug(
        "--\t\treference_check '%s' '%s'\tresult: '%s'",
        ref1, ref2, result,
    )
    return result


def list_reference_check(refs1, refs2, ds1, ds2, **weights):
    """For objects that contain multiple references (i.e., object_refs) perform
    the same de-reference procedure and perform object_similarity.
    The score influences the objects containing these references. The result is
    weighted on the amount of unique objects that could 1) be de-referenced 2) """
    results = {}

    pairs = _object_pairs(
        _bucket_per_type(refs1, "id-split"),
        _bucket_per_type(refs2, "id-split"),
        weights,
    )

    for ref1, ref2 in pairs:
        type1, type2 = ref1.split("--")[0], ref2.split("--")[0]
        if type1 == type2:
            score = reference_check(ref1, ref2, ds1, ds2, **weights)

            if ref1 not in results:
                results[ref1] = {"matched": ref2, "value": score}
            elif score > results[ref1]["value"]:
                results[ref1] = {"matched": ref2, "value": score}

            if ref2 not in results:
                results[ref2] = {"matched": ref1, "value": score}
            elif score > results[ref2]["value"]:
                results[ref2] = {"matched": ref1, "value": score}

    result = 0.0
    total_sum = sum(x["value"] for x in results.values())
    max_score = len(results)

    if max_score > 0:
        result = total_sum / max_score

    logger.debug(
        "--\t\tlist_reference_check '%s' '%s'\ttotal_sum: '%s'\tmax_score: '%s'\tresult: '%s'",
        refs1, refs2, total_sum, max_score, result,
    )
    return result


def _datastore_check(ds1, ds2):
    if (
        issubclass(ds1.__class__, (DataStoreMixin, DataSource)) or
        issubclass(ds2.__class__, (DataStoreMixin, DataSource))
    ):
        return True
    return False


def _bucket_per_type(graph, mode="type"):
    """Given a list of objects or references, bucket them by type.
    Depending on the list type: extract from 'type' property or using
    the 'id'.
    """
    buckets = collections.defaultdict(list)
    if mode == "type":
        [buckets[obj["type"]].append(obj) for obj in graph]
    elif mode == "id-split":
        [buckets[obj.split("--")[0]].append(obj) for obj in graph]
    return buckets


def _object_pairs(graph1, graph2, weights):
    """Returns a generator with the product of the comparable
    objects for the graph similarity process. It determines
    objects in common between graphs and objects with weights.
    """
    types_in_common = set(graph1.keys()).intersection(graph2.keys())
    testable_types = types_in_common.intersection(weights.keys())

    return itertools.chain.from_iterable(
        itertools.product(graph1[stix_type], graph2[stix_type])
        for stix_type in testable_types
    )


# default weights used for the similarity process
WEIGHTS = {
    "attack-pattern": {
        "name": (30, partial_string_based),
        "external_references": (70, partial_external_reference_based),
    },
    "campaign": {
        "name": (60, partial_string_based),
        "aliases": (40, partial_list_based),
    },
    "course-of-action": {
        "name": (60, partial_string_based),
        "external_references": (40, partial_external_reference_based),
    },
    "grouping": {
        "name": (20, partial_string_based),
        "context": (20, partial_string_based),
        "object_refs": (60, list_reference_check),
    },
    "identity": {
        "name": (60, partial_string_based),
        "identity_class": (20, exact_match),
        "sectors": (20, partial_list_based),
    },
    "incident": {
        "name": (30, partial_string_based),
        "external_references": (70, partial_external_reference_based),
    },
    "indicator": {
        "indicator_types": (15, partial_list_based),
        "pattern": (80, custom_pattern_based),
        "valid_from": (5, partial_timestamp_based),
        "tdelta": 1,  # One day interval
    },
    "intrusion-set": {
        "name": (20, partial_string_based),
        "external_references": (60, partial_external_reference_based),
        "aliases": (20, partial_list_based),
    },
    "location": {
        "longitude_latitude": (34, partial_location_distance),
        "region": (33, exact_match),
        "country": (33, exact_match),
        "threshold": 1000.0,
    },
    "malware": {
        "malware_types": (20, partial_list_based),
        "name": (80, partial_string_based),
    },
    "marking-definition": {
        "name": (20, exact_match),
        "definition": (60, exact_match),
        "definition_type": (20, exact_match),
    },
    "relationship": {
        "relationship_type": (20, exact_match),
        "source_ref": (40, reference_check),
        "target_ref": (40, reference_check),
    },
    "report": {
        "name": (30, partial_string_based),
        "published": (10, partial_timestamp_based),
        "object_refs": (60, list_reference_check),
        "tdelta": 1,  # One day interval
    },
    "sighting": {
        "first_seen": (5, partial_timestamp_based),
        "last_seen": (5, partial_timestamp_based),
        "sighting_of_ref": (40, reference_check),
        "observed_data_refs": (20, list_reference_check),
        "where_sighted_refs": (20, list_reference_check),
        "summary": (10, exact_match),
    },
    "threat-actor": {
        "name": (60, partial_string_based),
        "threat_actor_types": (20, partial_list_based),
        "aliases": (20, partial_list_based),
    },
    "tool": {
        "tool_types": (20, partial_list_based),
        "name": (80, partial_string_based),
    },
    "vulnerability": {
        "name": (30, partial_string_based),
        "external_references": (70, partial_external_reference_based),
    },
}  # :autodoc-skip:
