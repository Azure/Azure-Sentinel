# -*- coding: utf-8 -*-

"""Functions to perform conversions between the different Confidence scales.
As specified in STIX™ Version 2.1. Part 1: STIX Core Concepts - Appendix B"""


def none_low_med_high_to_value(scale_value):
    """
    This method will transform a string value from the None / Low / Med /
    High scale to its confidence integer representation.

    The scale for this confidence representation is the following:

    .. list-table:: None, Low, Med, High to STIX Confidence
        :header-rows: 1

        * - None/ Low/ Med/ High
          - STIX Confidence Value
        * - Not Specified
          - Not Specified
        * - None
          - 0
        * - Low
          - 15
        * - Med
          - 50
        * - High
          - 85

    Args:
        scale_value (str): A string value from the scale. Accepted strings are
            "None", "Low", "Med" and "High". Argument is case sensitive.

    Returns:
        int: The numerical representation corresponding to values in the
            None / Low / Med / High scale.

    Raises:
        ValueError: If `scale_value` is not within the accepted strings.
    """
    if scale_value == 'None':
        return 0
    elif scale_value == 'Low':
        return 15
    elif scale_value == 'Med':
        return 50
    elif scale_value == 'High':
        return 85
    else:
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)


def value_to_none_low_medium_high(confidence_value):
    """
    This method will transform an integer value into the None / Low / Med /
    High scale string representation.

    The scale for this confidence representation is the following:

    .. list-table:: STIX Confidence to None, Low, Med, High
        :header-rows: 1

        * - Range of Values
          - None/ Low/ Med/ High
        * - 0
          - None
        * - 1-29
          - Low
        * - 30-69
          - Med
        * - 70-100
          - High

    Args:
        confidence_value (int): An integer value between 0 and 100.

    Returns:
        str: A string corresponding to the None / Low / Med / High scale.

    Raises:
        ValueError: If `confidence_value` is out of bounds.

    """
    if confidence_value == 0:
        return 'None'
    elif 29 >= confidence_value >= 1:
        return 'Low'
    elif 69 >= confidence_value >= 30:
        return 'Med'
    elif 100 >= confidence_value >= 70:
        return 'High'
    else:
        raise ValueError("Range of values out of bounds: %s" % confidence_value)


def zero_ten_to_value(scale_value):
    """
    This method will transform a string value from the 0-10 scale to its
    confidence integer representation.

    The scale for this confidence representation is the following:

    .. list-table:: 0-10 to STIX Confidence
        :header-rows: 1

        * - 0-10 Scale
          - STIX Confidence Value
        * - 0
          - 0
        * - 1
          - 10
        * - 2
          - 20
        * - 3
          - 30
        * - 4
          - 40
        * - 5
          - 50
        * - 6
          - 60
        * - 7
          - 70
        * - 8
          - 80
        * - 9
          - 90
        * - 10
          - 100

    Args:
        scale_value (str): A string value from the scale. Accepted strings are "0"
            through "10" inclusive.

    Returns:
        int: The numerical representation corresponding to values in the 0-10
            scale.

    Raises:
        ValueError: If `scale_value` is not within the accepted strings.

    """
    if scale_value == '0':
        return 0
    elif scale_value == '1':
        return 10
    elif scale_value == '2':
        return 20
    elif scale_value == '3':
        return 30
    elif scale_value == '4':
        return 40
    elif scale_value == '5':
        return 50
    elif scale_value == '6':
        return 60
    elif scale_value == '7':
        return 70
    elif scale_value == '8':
        return 80
    elif scale_value == '9':
        return 90
    elif scale_value == '10':
        return 100
    else:
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)


def value_to_zero_ten(confidence_value):
    """
    This method will transform an integer value into the 0-10 scale string
    representation.

    The scale for this confidence representation is the following:

    .. list-table:: STIX Confidence to 0-10
        :header-rows: 1

        * - Range of Values
          - 0-10 Scale
        * - 0-4
          - 0
        * - 5-14
          - 1
        * - 15-24
          - 2
        * - 25-34
          - 3
        * - 35-44
          - 4
        * - 45-54
          - 5
        * - 55-64
          - 6
        * - 65-74
          - 7
        * - 75-84
          - 8
        * - 95-94
          - 9
        * - 95-100
          - 10

    Args:
        confidence_value (int): An integer value between 0 and 100.

    Returns:
        str: A string corresponding to the 0-10 scale.

    Raises:
        ValueError: If `confidence_value` is out of bounds.

    """
    if 4 >= confidence_value >= 0:
        return '0'
    elif 14 >= confidence_value >= 5:
        return '1'
    elif 24 >= confidence_value >= 15:
        return '2'
    elif 34 >= confidence_value >= 25:
        return '3'
    elif 44 >= confidence_value >= 35:
        return '4'
    elif 54 >= confidence_value >= 45:
        return '5'
    elif 64 >= confidence_value >= 55:
        return '6'
    elif 74 >= confidence_value >= 65:
        return '7'
    elif 84 >= confidence_value >= 75:
        return '8'
    elif 94 >= confidence_value >= 85:
        return '9'
    elif 100 >= confidence_value >= 95:
        return '10'
    else:
        raise ValueError("Range of values out of bounds: %s" % confidence_value)


def admiralty_credibility_to_value(scale_value):
    """
    This method will transform a string value from the Admiralty Credibility
    scale to its confidence integer representation.

    The scale for this confidence representation is the following:

    .. list-table:: Admiralty Credibility Scale to STIX Confidence
        :header-rows: 1

        * - Admiralty Credibility
          - STIX Confidence Value
        * - 6 - Truth cannot be judged
          - (Not present)
        * - 5 - Improbable
          - 10
        * - 4 - Doubtful
          - 30
        * - 3 - Possibly True
          - 50
        * - 2 - Probably True
          - 70
        * - 1 - Confirmed by other sources
          - 90

    Args:
        scale_value (str): A string value from the scale. Accepted strings are
            "6 - Truth cannot be judged", "5 - Improbable", "4 - Doubtful",
            "3 - Possibly True", "2 - Probably True" and
            "1 - Confirmed by other sources". Argument is case sensitive.

    Returns:
        int: The numerical representation corresponding to values in the
            Admiralty Credibility scale.

    Raises:
        ValueError: If `scale_value` is not within the accepted strings.

    """
    if scale_value == '6 - Truth cannot be judged':
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)
    elif scale_value == '5 - Improbable':
        return 10
    elif scale_value == '4 - Doubtful':
        return 30
    elif scale_value == '3 - Possibly True':
        return 50
    elif scale_value == '2 - Probably True':
        return 70
    elif scale_value == '1 - Confirmed by other sources':
        return 90
    else:
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)


def value_to_admiralty_credibility(confidence_value):
    """
    This method will transform an integer value into the Admiralty Credibility
    scale string representation.

    The scale for this confidence representation is the following:

    .. list-table:: STIX Confidence to Admiralty Credibility Scale
        :header-rows: 1

        * - Range of Values
          - Admiralty Credibility
        * - N/A
          - 6 - Truth cannot be judged
        * - 0-19
          - 5 - Improbable
        * - 20-39
          - 4 - Doubtful
        * - 40-59
          - 3 - Possibly True
        * - 60-79
          - 2 - Probably True
        * - 80-100
          - 1 - Confirmed by other sources

    Args:
        confidence_value (int): An integer value between 0 and 100.

    Returns:
        str: A string corresponding to the Admiralty Credibility scale.

    Raises:
        ValueError: If `confidence_value` is out of bounds.

    """
    if 19 >= confidence_value >= 0:
        return '5 - Improbable'
    elif 39 >= confidence_value >= 20:
        return '4 - Doubtful'
    elif 59 >= confidence_value >= 40:
        return '3 - Possibly True'
    elif 79 >= confidence_value >= 60:
        return '2 - Probably True'
    elif 100 >= confidence_value >= 80:
        return '1 - Confirmed by other sources'
    else:
        raise ValueError("Range of values out of bounds: %s" % confidence_value)


def wep_to_value(scale_value):
    """
    This method will transform a string value from the WEP scale to its
    confidence integer representation.

    The scale for this confidence representation is the following:

    .. list-table:: WEP to STIX Confidence
        :header-rows: 1

        * - WEP
          - STIX Confidence Value
        * - Impossible
          - 0
        * - Highly Unlikely/Almost Certainly Not
          - 10
        * - Unlikely/Probably Not
          - 20
        * - Even Chance
          - 50
        * - Likely/Probable
          - 70
        * - Highly likely/Almost Certain
          - 90
        * - Certain
          - 100

    Args:
        scale_value (str): A string value from the scale. Accepted strings are
            "Impossible", "Highly Unlikely/Almost Certainly Not",
            "Unlikely/Probably Not", "Even Chance", "Likely/Probable",
            "Highly likely/Almost Certain" and "Certain". Argument is case
            sensitive.

    Returns:
        int: The numerical representation corresponding to values in the WEP
            scale.

    Raises:
        ValueError: If `scale_value` is not within the accepted strings.

    """
    if scale_value == 'Impossible':
        return 0
    elif scale_value == 'Highly Unlikely/Almost Certainly Not':
        return 10
    elif scale_value == 'Unlikely/Probably Not':
        return 30
    elif scale_value == 'Even Chance':
        return 50
    elif scale_value == 'Likely/Probable':
        return 70
    elif scale_value == 'Highly likely/Almost Certain':
        return 90
    elif scale_value == 'Certain':
        return 100
    else:
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)


def value_to_wep(confidence_value):
    """
    This method will transform an integer value into the WEP scale string
    representation.

    The scale for this confidence representation is the following:

    .. list-table:: STIX Confidence to WEP
        :header-rows: 1

        * - Range of Values
          - WEP
        * - 0
          - Impossible
        * - 1-19
          - Highly Unlikely/Almost Certainly Not
        * - 20-39
          - Unlikely/Probably Not
        * - 40-59
          - Even Chance
        * - 60-79
          - Likely/Probable
        * - 80-99
          - Highly likely/Almost Certain
        * - 100
          - Certain

    Args:
        confidence_value (int): An integer value between 0 and 100.

    Returns:
        str: A string corresponding to the WEP scale.

    Raises:
        ValueError: If `confidence_value` is out of bounds.

    """
    if confidence_value == 0:
        return 'Impossible'
    elif 19 >= confidence_value >= 1:
        return 'Highly Unlikely/Almost Certainly Not'
    elif 39 >= confidence_value >= 20:
        return 'Unlikely/Probably Not'
    elif 59 >= confidence_value >= 40:
        return 'Even Chance'
    elif 79 >= confidence_value >= 60:
        return 'Likely/Probable'
    elif 99 >= confidence_value >= 80:
        return 'Highly likely/Almost Certain'
    elif confidence_value == 100:
        return 'Certain'
    else:
        raise ValueError("Range of values out of bounds: %s" % confidence_value)


def dni_to_value(scale_value):
    """
    This method will transform a string value from the DNI scale to its
    confidence integer representation.

    The scale for this confidence representation is the following:

    .. list-table:: DNI Scale to STIX Confidence
        :header-rows: 1

        * - DNI Scale
          - STIX Confidence Value
        * - Almost No Chance / Remote
          - 5
        * - Very Unlikely / Highly Improbable
          - 15
        * - Unlikely / Improbable
          - 30
        * - Roughly Even Chance / Roughly Even Odds
          - 50
        * - Likely / Probable
          - 70
        * - Very Likely / Highly Probable
          - 85
        * - Almost Certain / Nearly Certain
          - 95

    Args:
        scale_value (str): A string value from the scale. Accepted strings are
            "Almost No Chance / Remote", "Very Unlikely / Highly Improbable",
            "Unlikely / Improbable", "Roughly Even Chance / Roughly Even Odds",
            "Likely / Probable", "Very Likely / Highly Probable" and
            "Almost Certain / Nearly Certain". Argument is case sensitive.

    Returns:
        int: The numerical representation corresponding to values in the DNI
            scale.

    Raises:
        ValueError: If `scale_value` is not within the accepted strings.

    """
    if scale_value == 'Almost No Chance / Remote':
        return 5
    elif scale_value == 'Very Unlikely / Highly Improbable':
        return 15
    elif scale_value == 'Unlikely / Improbable':
        return 30
    elif scale_value == 'Roughly Even Chance / Roughly Even Odds':
        return 50
    elif scale_value == 'Likely / Probable':
        return 70
    elif scale_value == 'Very Likely / Highly Probable':
        return 85
    elif scale_value == 'Almost Certain / Nearly Certain':
        return 95
    else:
        raise ValueError("STIX Confidence value cannot be determined for %s" % scale_value)


def value_to_dni(confidence_value):
    """
    This method will transform an integer value into the DNI scale string
    representation.

    The scale for this confidence representation is the following:

    .. list-table:: STIX Confidence to DNI Scale
        :header-rows: 1

        * - Range of Values
          - DNI Scale
        * - 0-9
          - Almost No Chance / Remote
        * - 10-19
          - Very Unlikely / Highly Improbable
        * - 20-39
          - Unlikely / Improbable
        * - 40-59
          - Roughly Even Chance / Roughly Even Odds
        * - 60-79
          - Likely / Probable
        * - 80-89
          - Very Likely / Highly Probable
        * - 90-100
          - Almost Certain / Nearly Certain

    Args:
        confidence_value (int): An integer value between 0 and 100.

    Returns:
        str: A string corresponding to the DNI scale.

    Raises:
        ValueError: If `confidence_value` is out of bounds.

    """
    if 9 >= confidence_value >= 0:
        return 'Almost No Chance / Remote'
    elif 19 >= confidence_value >= 10:
        return 'Very Unlikely / Highly Improbable'
    elif 39 >= confidence_value >= 20:
        return 'Unlikely / Improbable'
    elif 59 >= confidence_value >= 40:
        return 'Roughly Even Chance / Roughly Even Odds'
    elif 79 >= confidence_value >= 60:
        return 'Likely / Probable'
    elif 89 >= confidence_value >= 80:
        return 'Very Likely / Highly Probable'
    elif 100 >= confidence_value >= 90:
        return 'Almost Certain / Nearly Certain'
    else:
        raise ValueError("Range of values out of bounds: %s" % confidence_value)
