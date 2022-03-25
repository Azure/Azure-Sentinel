"""
Author: Steven Steiner <steven.steiner@cyberark.com>
Version: 0.0.1
Date Created: 6/10/2019 16:19
"""
import certifi, json, requests, urllib3


def epmAuth(dispatcher, username, password):
    """
        EPM Authentication
        This method authenticates the user to EPM using username and password and returns
        a token that can be used in subsequent Rest API calls.
        After the configured timeout expires, users have to logon again using their
        username and password.
        The session timeout for all APIs is part of the session token and is defined by the
        Timeoutforinactivesession Server Configuration parameter.
        Args:
            diapatcher (str): The EPM SaaS site to get version information from and perform the initial logon
            username (str): Valid User ID with access to the Set(s)
            password (str): Password for the User ID logging into the Rest API

        Returns:
            list: Json list containing the EPMAuthenticationResult, ManagerURL, IsPasswordExpired (True/False)
    """
    # build the body of the request containing the credentials
    body = {}
    body['Username'] = username
    body['Password'] = password
    body['ApplicationID'] = 'Irrelevent'
    logonBody = json.dumps(body)

    # build the header and url
    myURL = dispatcher + "/EPM/API/Auth/EPM/Logon"
    hdr = {'Content-Type': 'application/json'}

    # make the Rest API call
    urllib3.disable_warnings()

    return requests.post(myURL, headers=hdr, data=logonBody, verify=False)


def winAuth(epmsrv, username, password, version=None):
    """
        Windows Authentication
        This method authenticates the user to EPM by Windows authentication and returns
        a token that can be used in subsequent Rest API calls.
        After the configured timeout expires, users have to logon again using their
        username and password.
        ***** Not for EPM SaaS use *****
    """
    # build the body of the request containing the credentials
    body = {}
    body['ApplicationID'] = 'Irrelevent'
    logonBody = json.dumps(body)

    # build the header and url
    if version == None:
        myURL = epmsrv + "/EPM/API/Auth/Windows/Logon"
    else:
        myURL = epmsrv + "/EPM/API/" + version + "/Auth/Windows/Logon"
    hdr = {'Content-Type': 'application/json'}

    # make the Rest API call
    urllib3.disable_warnings()
    return requests.post(myURL, headers=hdr, data=logonBody, verify=False)


def getVersion(dispatcher, version=None):
    """
        Get EPM version
        This method enables the user to retrieve the EPM version
    """
    # create the URL to the dispacthcer with the information passed in to the function
    if version == None:
        myURL = dispatcher + "/EPM/API/Server/Version"
    else:
        myURL = dispatcher + "/EPM/API/" + version + "/Server/Version"

    # make the Rest API call
    urllib3.disable_warnings()
    return requests.get(myURL, verify=False)


def getSetsList(epmserver, epmToken, authType, version=None):
    """
        Get Sets list
        This method enables the user to retrieve the list of Sets.
    """
    # build the URL
    if version == None:
        myURL = epmserver + "/EPM/API/Sets"
    else:
        myURL = epmserver + "/EPM/API/" + version + "/Sets"

    # build the header
    hdr = {}
    hdr['Content-Type'] = 'application/json'
    if authType == 'EPM':
        authToken = 'basic ' + epmToken
        hdr['Authorization'] = authToken
    else:
        authToken = epmToken
        hdr['VFUser'] = authToken

    # make the Rest API call
    urllib3.disable_warnings()
    return requests.get(myURL, headers=hdr, verify=False)


def getAggregatedEvents(epmserver, epmToken, authType, setid, data, next_cursor="start", limit=1000, **kwargs):
    """
        Get aggregated events
        This method enables the user to retrieve aggregated events from EPM according
    """

    # build the URL

    if next_cursor is not None:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/events/aggregations/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/events/aggregations/search?limit=" + str(limit)

    # build the header
    hdr = {}
    hdr['Content-Type'] = 'application/json'
    if authType == 'EPM':
        authToken = 'basic ' + epmToken
        hdr['Authorization'] = authToken
    else:
        authToken = epmToken
        hdr['VFUser'] = authToken

    # make the Rest API call
    urllib3.disable_warnings()
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them
    if len(kwargs) > 0:
        return requests.post(myURL, headers=hdr, verify=False, data=data, params=kwargs)
    else:
        return requests.post(myURL, headers=hdr, verify=False, data=data)


def getDetailedRawEvents(epmserver, epmToken, authType, setid, data, next_cursor="start", limit=1000, **kwargs):
    """
        Get detailed raw events
        This method enables the user to retrieve raw events from EPM according
        to a predefined filter
    """

    # build the URL
    if next_cursor is not None:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/Events/Search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/Events/Search?limit=" + str(limit)

    # build the header
    hdr = {}
    hdr['Content-Type'] = 'application/json'
    if authType == 'EPM':
        authToken = 'basic ' + epmToken
        hdr['Authorization'] = authToken
    else:
        authToken = epmToken
        hdr['VFUser'] = authToken

    # make the Rest API call
    urllib3.disable_warnings()
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return requests.post(myURL, headers=hdr, params=kwargs, verify=False, data=data)
    else:
        return requests.post(myURL, headers=hdr, verify=False, data=data)


def getAggregatedPolicyAudits(epmserver, epmToken, authType, setid, data, next_cursor="start", limit=1000, **kwargs):
    """
            Get aggregated policy audits
            This method enables the user to retrieve aggregated policy audits from EPM according
    """

    # build the URL
    if next_cursor is not None:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/policyaudits/aggregations/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/policyaudits/aggregations/search?limit=" + str(limit)

    # build the header
    hdr = {}
    hdr['Content-Type'] = 'application/json'
    if authType == 'EPM':
        authToken = 'basic ' + epmToken
        hdr['Authorization'] = authToken
    else:
        authToken = epmToken
        hdr['VFUser'] = authToken

    # make the Rest API call
    urllib3.disable_warnings()
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return requests.post(myURL, headers=hdr, params=kwargs, verify=False, data=data)
    else:
        return requests.post(myURL, headers=hdr, verify=False, data=data)


def getPolicyAuditRawEventDetails(epmserver, epmToken, authType, setid, data, next_cursor="start", limit=1000,
                                  **kwargs):
    """
            Get policy audit raw event details
            This method enables the user to retrieve policy audit raw event details from EPM according
    """

    # build the URL
    if next_cursor is not None:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/policyaudits/search?nextCursor=" + next_cursor + "&limit=" + str(
            limit)
    else:
        myURL = epmserver + "/EPM/API/Sets/" + setid + "/policyaudits/search?limit=" + str(limit)

    # build the header
    hdr = {}
    hdr['Content-Type'] = 'application/json'
    if authType == 'EPM':
        authToken = 'basic ' + epmToken
        hdr['Authorization'] = authToken
    else:
        authToken = epmToken
        hdr['VFUser'] = authToken

    # make the Rest API call
    urllib3.disable_warnings()
    # this url can take a query, the parameters for the query should be in kwargs
    # check to see if there are any keyword arguments passed in to this function
    # if so, use them

    if len(kwargs) > 0:
        return requests.post(myURL, headers=hdr, params=kwargs, verify=False, data=data)
    else:
        return requests.post(myURL, headers=hdr, verify=False, data=data)
