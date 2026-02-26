import requests, urllib3


urllib3.disable_warnings()


def _build_bearer_headers(bearer_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + bearer_token,
    }


def _request(method, url, headers=None, data=None, params=None):
    if method == 'GET':
        return requests.get(url, headers=headers, params=params)
    if method == 'POST':
        return requests.post(url, headers=headers, data=data, params=params)
    raise ValueError('Unsupported method')


def _build_auth_headers(epm_token, auth_type=None):
    return _build_bearer_headers(epm_token)


def get_version(dispatcher, version=None):
    """
        Get EPM version
        This method enables the user to retrieve the EPM version
    """
    # create the URL to the dispacthcer with the information passed in to the function
    if not version:
        target_url = dispatcher + "/EPM/API/Server/Version"
    else:
        target_url = dispatcher + "/EPM/API/" + version + "/Server/Version"

    # make the Rest API call
    return requests.get(target_url)


def get_sets_list(epm_server, epm_token, version=None):
    """
        Get Sets list
        This method enables the user to retrieve the list of Sets.
    """
    # build the URL
    if not version:
        target_url = epm_server + "/EPM/API/Sets"
    else:
        target_url = epm_server + "/EPM/API/" + version + "/Sets"

    # build the header
    hdr = _build_bearer_headers(epm_token)
    hdr['x-cybr-telemetry'] = 'aW49TWljcm9zb2Z0IFNlbnRpbmVsIEVQTSZpdj0yLjAmdm49TWljcm9zb2Z0Jml0PVNJRU0='

    # make the Rest API call
    return _request('GET', target_url, headers=hdr)


def get_aggregated_events(epm_server, epm_token, set_id, data, next_cursor="start", limit=1000, **kwargs):
    """
        Get aggregated events
        This method enables the user to retrieve aggregated events from EPM according
    """

    # build the URL

    if next_cursor:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/events/aggregations/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/events/aggregations/search?limit=" + str(limit)

    # build the header
    hdr = _build_bearer_headers(epm_token)

    # make the Rest API call
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them
    if len(kwargs) > 0:
        return _request('POST', target_url, headers=hdr, data=data, params=kwargs)
    else:
        return _request('POST', target_url, headers=hdr, data=data)


def get_detailed_raw_events(epm_server, epm_token, set_id, data, next_cursor="start", limit=1000, **kwargs):
    """
        Get detailed raw events
        This method enables the user to retrieve raw events from EPM according
        to a predefined filter
    """

    # build the URL
    if next_cursor:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/Events/Search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/Events/Search?limit=" + str(limit)

    # build the header
    hdr = _build_bearer_headers(epm_token)

    # make the Rest API call
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return _request('POST', target_url, headers=hdr, data=data, params=kwargs)
    else:
        return _request('POST', target_url, headers=hdr, data=data)


def get_aggregated_policy_audits(epm_server, epm_token, set_id, data, next_cursor="start", limit=1000, **kwargs):
    """
            Get aggregated policy audits
            This method enables the user to retrieve aggregated policy audits from EPM according
    """

    # build the URL
    if next_cursor:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/policyaudits/aggregations/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/policyaudits/aggregations/search?limit=" + str(limit)

    # build the header
    hdr = _build_bearer_headers(epm_token)

    # make the Rest API call
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return _request('POST', target_url, headers=hdr, data=data, params=kwargs)
    else:
        return _request('POST', target_url, headers=hdr, data=data)


def get_policy_audit_raw_event_details(epm_server, epm_token, set_id, data, next_cursor="start", limit=1000,
                                  **kwargs):
    """
            Get policy audit raw event details
            This method enables the user to retrieve policy audit raw event details from EPM according
    """

    # build the URL
    if next_cursor:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/policyaudits/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/policyaudits/search?limit=" + str(limit)

    # build the header
    hdr = _build_bearer_headers(epm_token)

    # make the Rest API call
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return _request('POST', target_url, headers=hdr, data=data, params=kwargs)
    else:
        return _request('POST', target_url, headers=hdr, data=data)

def get_admin_audit_events(epm_server, epm_token, set_id, start_time, end_time, limit=100):
    """
        Get Admin Audit Data
        This method enables the user to retrieve Admin Audit Data from EPM according
        to a range of time (between start_time and end_time)
    """
    # build the header
    hdr = _build_bearer_headers(epm_token)

    # make the Rest API call
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    rows_count = 0
    offset = 0
    events_json = []

    while True:
        #build the URL
        target_url = epm_server + "/EPM/API/Sets/" + set_id + "/AdminAudit?DateFrom=" + start_time + "&DateTo=" + end_time + "&limit=" + str(limit) + "&offset=" + str(offset)
        r = _request('GET', target_url, headers=hdr).json()
        events_json += r["AdminAudits"]
        #Get TotalCount from JSON
        total_count = r["TotalCount"]
        rows_count += len(r["AdminAudits"])

        if total_count > rows_count:
            offset += limit
        else:
            break
    if len(events_json) > 0:
        for admin_audit_event in events_json:
            admin_audit_event["event_type"] = "admin_audit"

    return events_json
