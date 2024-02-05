#!/usr/bin/env python

import hmac
import hashlib
import base64
import requests
import datetime

from typing import Optional

tformat = '%Y-%m-%dT%H:%M:%S.%f'
pathTypes = {
    'Tier Zero Attack Paths': [
        'NonT0DCSyncers',
        'T0AddAllowedToAct',
        'T0AddKeyCredentialLink',
        'T0AddMember',
        'T0AddSelf',
        'T0Admins',
        'T0AllExtendedRights',
        'T0AllowedToAct',
        'T0AllowedToDelegate',
        'T0DCOM',
        'T0ForceChangePassword',
        'T0GenericAll',
        'T0GenericWrite',
        'T0HasSIDHistory',
        'T0Logins',
        'T0Owns',
        'T0PSRemote',
        'T0RDP',
        'T0ReadGMSA',
        'T0ReadLAPS',
        'T0SQLAdmin',
        'T0WriteDACL',
        'T0WriteOwner',
        'T0WriteSPN',
        'T0WriteAccountRestrictions',
        'T0SyncLAPSPassword'
    ],
    'Abusable Kerberos Configurations': [
        'ASREPRoasting',
        'T0MarkSensitive',
        'Kerberoasting',
        'UnconstrainedAddKeyCredentialLink',
        'UnconstrainedAdmins',
        'UnconstrainedAllowedToDelegate',
        'UnconstrainedDCOM',
        'UnconstrainedForceChangePassword',
        'UnconstrainedGenericAll',
        'UnconstrainedGenericWrite',
        'UnconstrainedOwns',
        'UnconstrainedPSRemote',
        'UnconstrainedRDP',
        'UnconstrainedReadLAPS',
        'UnconstrainedSQLAdmin',
        'UnconstrainedWriteDACL',
        'UnconstrainedWriteOwner',
        'UnconstrainedWriteAccountRestrictions',
        'UnconstrainedSyncLAPSPassword'
    ],
    'Least Privilege Enforcement': [
        'LargeDefaultGroupsOwns',
        'LargeDefaultGroupsAddAllowedToAct',
        'LargeDefaultGroupsAddKeyCredentialLink',
        'LargeDefaultGroupsAddMember',
        'LargeDefaultGroupsAddSelf',
        'LargeDefaultGroupsAdmins',
        'LargeDefaultGroupsAllExtendedRights',
        'LargeDefaultGroupsDCOM',
        'LargeDefaultGroupsGenericAll',
        'LargeDefaultGroupsGenericWrite',
        'LargeDefaultGroupsPSRemote',
        'LargeDefaultGroupsRDP',
        'LargeDefaultGroupsReadGMSA',
        'LargeDefaultGroupsReadLAPS',
        'LargeDefaultGroupsSQLAdmin',
        'LargeDefaultGroupsWriteDacl',
        'LargeDefaultGroupsWriteOwner',
        'LargeDefaultGroupsWriteSPN',
        'LargeDefaultGroupsForceChangePassword',
        'LargeDefaultGroupsWriteAccountRestrictions',
        'LargeDefaultGroupsSyncLAPSPassword'
  ]
}

def get_path_type(path_id) -> str:
    for pathType, findingTypes in pathTypes.items():
        for findingType in findingTypes:
            if path_id == findingType:
                return pathType
    return 'Unknown'


class Credentials(object):
    def __init__(self, token_id: str, token_key: str) -> None:
        self.token_id = token_id
        self.token_key = token_key

class AttackPath(object):
    def __init__(self, id: str, title: str, domain) -> None:
        self.id = id
        self.title = title
        self.type = get_path_type(id)
        self.domain_id = domain['id']
        self.domain_name = domain['name'].strip()

    def __lt__(self, other):
        return self.exposure < other.exposure

class BHEClient(object):
    def __init__(self, scheme: str, host: str, port: int, credentials: Credentials) -> None:
        self._scheme = scheme
        self._host = host
        self._port = port
        self._credentials = credentials

    def _format_url(self, uri: str) -> str:
        formatted_uri = uri
        if uri.startswith('/'):
            formatted_uri = formatted_uri[1:]

        return f'{self._scheme}://{self._host}:{self._port}/{formatted_uri}'

    def _request(self, method: str, uri: str, body: Optional[bytes] = None) -> requests.Response:
        digester = hmac.new(self._credentials.token_key.encode(), None, hashlib.sha256)
        digester.update(f'{method}{uri}'.encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)
        datetime_formatted = datetime.datetime.now().astimezone().isoformat('T')
        digester.update(datetime_formatted[:13].encode())
        digester = hmac.new(digester.digest(), None, hashlib.sha256)

        if body is not None:
            digester.update(body)

        # Perform the request with the signed and expected headers
        return requests.request(
            method=method,
            url=self._format_url(uri),
            headers={
                'User-Agent': 'bhe-sentinel-integration v0.0.1',
                'Authorization': f'bhesignature {self._credentials.token_id}',
                'RequestDate': datetime_formatted,
                'Signature': base64.b64encode(digester.digest()),
                'Content-Type': 'application/json',
            },
            data=body,
        )

    def get_api_version(self):
        return self._request('GET', '/api/version')

    def get_domains(self) -> list:
        response = self._request('GET', '/api/v2/available-domains')
        domain_data = response.json()['data']
        return domain_data

    def get_paths(self, domain) -> list:
        response = self._request('GET', '/api/v2/domains/' + domain['id'] + '/available-types')
        path_ids = response.json()['data']

        paths = list()
        for path_id in path_ids:
            ## Get nice title from API and strip newline
            path_title = self._request('GET', '/ui/findings/' + path_id + '/title.md')

            ## Create attackpath object
            path = AttackPath(path_id, path_title.text.strip(), domain)
            paths.append(path)

        return paths

    def get_path_timeline(self, path, from_timestamp, to_timestamp):
        ## Sparkline data
        response = self._request('GET', '/api/v2/domains/' + path.domain_id + '/sparkline?finding=' + path.id + '&from=' + from_timestamp + '&to=' + to_timestamp)
        exposure_data = response.json()['data']

        events = list()
        for event in exposure_data:
            e = {}
            e['finding_id'] = path.id
            e['domain_id'] = path.domain_id
            e['path_title'] = path.title
            e['path_type'] = path.type
            e['exposure'] = event['CompositeRisk']
            e['finding_count'] = event['FindingCount']
            e['principal_count'] = event['ImpactedAssetCount']
            e['id'] = event['id']
            e['created_at'] = event['created_at']
            e['updated_at'] = event['updated_at']
            e['deleted_at'] = event['deleted_at']

            ## Determine severity from exposure
            e['severity'] = self.get_severity(e['exposure'])
            events.append(e)

        return events

    def get_path_principals(self, path: AttackPath) -> list:
        # Get path details from API
        response = self._request('GET', '/api/v2/domains/' + path.domain_id + '/details?finding=' + path.id + '&skip=0&limit=0&Accepted=eq:False')
        payload = response.json()

        # Build dictionary of impacted pricipals
        if 'count' in payload:
            path.impacted_principals = list()
            for path_data in payload['data']:
                # Check for both From and To to determine whether relational or configuration path
                if (path.id.startswith('LargeDefault')):

                    # Get from and to principal names
                    if ('name' in path_data['FromPrincipalProps']):
                        from_principal = path_data['FromPrincipalProps']['name']
                    else:
                        from_principal = path_data['FromPrincipal']
                    if ('name' in path_data['ToPrincipalProps']):
                        to_principal = path_data['ToPrincipalProps']['name']
                    else:
                        to_principal = path_data['ToPrincipal']

                    principals = {
                        'Group': from_principal,
                        'Principal': to_principal
                    }

                elif ('FromPrincipalProps' in path_data) and ('ToPrincipalProps' in path_data):

                    # Get from and to principal names
                    if ('name' in path_data['FromPrincipalProps']):
                        from_principal = path_data['FromPrincipalProps']['name']
                    else:
                        from_principal = path_data['FromPrincipal']
                    if ('name' in path_data['ToPrincipalProps']):
                        to_principal = path_data['ToPrincipalProps']['name']
                    else:
                        to_principal = path_data['ToPrincipal']

                    principals = {
                        'Non Tier Zero Principal': from_principal,
                        'Tier Zero Principal': to_principal
                    }
                else:
                    principals = {
                        'User': path_data['Props']['name']
                    }
                path.impacted_principals.append(principals)
                path.principal_count = payload['count']
        else:
            path.principal_count = 0

        return path

    def get_posture(self, from_timestamp, to_timestamp) -> list:
        response = self._request('GET', '/api/v2/posture-stats?from=' + from_timestamp + '&to=' + to_timestamp)
        payload = response.json()
        return payload["data"]

    def get_severity(self, exposure) -> str:
        severity = 'Low'
        if exposure > 40: severity = 'Moderate'
        if exposure > 80: severity = 'High'
        if exposure > 95: severity = 'Critical'
        return severity
