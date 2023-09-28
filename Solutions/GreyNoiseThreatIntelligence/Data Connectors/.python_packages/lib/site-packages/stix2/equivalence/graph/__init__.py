"""Python APIs for STIX 2 Graph-based Semantic Equivalence and Similarity."""
import logging

from ..object import (
    WEIGHTS, _bucket_per_type, _object_pairs, object_similarity,
)

logger = logging.getLogger(__name__)


def graph_equivalence(
    ds1, ds2, prop_scores={}, threshold=70,
    ignore_spec_version=False, versioning_checks=False,
    max_depth=1, **weight_dict
):
    """This method returns a true/false value if two graphs are semantically equivalent.
    Internally, it calls the graph_similarity function and compares it against the given
    threshold value.

    Args:
        ds1: A DataStore object instance representing your graph
        ds2: A DataStore object instance representing your graph
        prop_scores: A dictionary that can hold individual property scores,
            weights, contributing score, matching score and sum of weights.
        threshold: A numerical value between 0 and 100 to determine the minimum
            score to result in successfully calling both graphs equivalent. This
            value can be tuned.
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
        bool: True if the result of the graph similarity is greater than or equal to
            the threshold value. False otherwise.

    Warning:
        Object types need to have property weights defined for the similarity process.
        Otherwise, those objects will not influence the final score. The WEIGHTS
        dictionary under `stix2.equivalence.graph` can give you an idea on how to add
        new entries and pass them via the `weight_dict` argument. Similarly, the values
        or methods can be fine tuned for a particular use case.

    Note:
        Default weight_dict:

        .. include:: ../../similarity_weights.rst

    Note:
        This implementation follows the Semantic Equivalence Committee Note.
        see `the Committee Note <link here>`__.

    """
    similarity_result = graph_similarity(
        ds1, ds2, prop_scores, ignore_spec_version,
        versioning_checks, max_depth, **weight_dict
    )
    if similarity_result >= threshold:
        return True
    return False


def graph_similarity(
    ds1, ds2, prop_scores={}, ignore_spec_version=False,
    versioning_checks=False, max_depth=1, **weight_dict
):
    """This method returns a similarity score for two given graphs.
    Each DataStore can contain a connected or disconnected graph and the
    final result is weighted over the amount of objects we managed to compare.
    This approach builds on top of the object-based similarity process
    and each comparison can return a value between 0 and 100.

    Args:
        ds1: A DataStore object instance representing your graph
        ds2: A DataStore object instance representing your graph
        prop_scores: A dictionary that can hold individual property scores,
            weights, contributing score, matching score and sum of weights.
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
        dictionary under `stix2.equivalence.graph` can give you an idea on how to add
        new entries and pass them via the `weight_dict` argument. Similarly, the values
        or methods can be fine tuned for a particular use case.

    Note:
        Default weight_dict:

        .. include:: ../../similarity_weights.rst

    Note:
        This implementation follows the Semantic Equivalence Committee Note.
        see `the Committee Note <link here>`__.

    """
    results = {}
    similarity_score = 0
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

    if max_depth <= 0:
        raise ValueError("'max_depth' must be greater than 0")

    pairs = _object_pairs(
        _bucket_per_type(ds1.query([])),
        _bucket_per_type(ds2.query([])),
        weights,
    )

    logger.debug("Starting graph similarity process between DataStores: '%s' and '%s'", ds1.id, ds2.id)
    for object1, object2 in pairs:
        iprop_score = {}
        object1_id = object1["id"]
        object2_id = object2["id"]

        result = object_similarity(
            object1, object2, iprop_score, ds1, ds2,
            ignore_spec_version, versioning_checks,
            max_depth, **weights
        )

        if object1_id not in results:
            results[object1_id] = {"lhs": object1_id, "rhs": object2_id, "prop_score": iprop_score, "value": result}
        elif result > results[object1_id]["value"]:
            results[object1_id] = {"lhs": object1_id, "rhs": object2_id, "prop_score": iprop_score, "value": result}

        if object2_id not in results:
            results[object2_id] = {"lhs": object2_id, "rhs": object1_id, "prop_score": iprop_score, "value": result}
        elif result > results[object2_id]["value"]:
            results[object2_id] = {"lhs": object2_id, "rhs": object1_id, "prop_score": iprop_score, "value": result}

    matching_score = sum(x["value"] for x in results.values())
    len_pairs = len(results)
    if len_pairs > 0:
        similarity_score = matching_score / len_pairs

    prop_scores["matching_score"] = matching_score
    prop_scores["len_pairs"] = len_pairs
    prop_scores["summary"] = results

    logger.debug(
        "DONE\t\tLEN_PAIRS: %.2f\tMATCHING_SCORE: %.2f\t SIMILARITY_SCORE: %.2f",
        len_pairs,
        matching_score,
        similarity_score,
    )
    return similarity_score
