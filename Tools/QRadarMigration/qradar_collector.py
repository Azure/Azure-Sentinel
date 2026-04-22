#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QRadar Data Collector — collects, transforms, and exports QRadar
rule and log-source metadata for migration analysis.

Usage:
    python qradar_collector.py --help
"""
from __future__ import absolute_import, print_function, unicode_literals, division

VERSION = '0.3.2'

import argparse
import base64
import csv
from collections import defaultdict
import io
import getpass
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

PY2 = sys.version_info[0] == 2

if PY2:
    from urllib2 import HTTPError  # noqa: F401  — used by QRadarClientBase
    string_types = (str, unicode)  # noqa: F821
    text_type = unicode  # noqa: F821
else:
    import ssl
    import urllib.request  # noqa: F401
    from urllib.error import HTTPError  # noqa: F401
    string_types = (str,)
    text_type = str

_BadZipFile = getattr(zipfile, 'BadZipFile', None) or zipfile.BadZipfile
_TimeoutExpired = getattr(subprocess, 'TimeoutExpired', None)


# ---------------------------------------------------------------------------
#  Module-Level Constants
# ---------------------------------------------------------------------------

RETRYABLE_HTTP_STATUSES = (429, 500, 502, 503, 504)

UCM_REPORT_COLUMNS = ('N', 'GR', 'RC', 'T', 'RO', 'EN', 'RE', 'R',
                       'NO', 'A', 'AD', 'OT', 'RED', 'LLC', 'E',
                       'ED', 'TD', 'NI')

REFERENCE_DATA_ENDPOINTS = [
    ('high_level_categories', '/api/data_classification/high_level_categories', 1000),
    ('low_level_categories', '/api/data_classification/low_level_categories', 1000),
    ('qid_records', '/api/data_classification/qid_records', 100000),
    ('dsm_event_mappings', '/api/data_classification/dsm_event_mappings', 100000),
    ('log_source_types', '/api/config/event_sources/log_source_management/log_source_types', 1000),
    ('log_sources', '/api/config/event_sources/log_source_management/log_sources', 1000),
    ('log_source_groups', '/api/config/event_sources/log_source_management/log_source_groups', 1000, False),
    ('reference_sets', '/api/reference_data/sets', 1000),
    ('reference_maps', '/api/reference_data/maps', 1000),
    ('reference_map_of_sets', '/api/reference_data/map_of_sets', 1000),
    ('extensions', '/api/config/extension_management/extensions', 1000),
    ('rule_groups', '/api/analytics/rule_groups', 1000),
    ('regex_properties', '/api/config/event_sources/custom_properties/regex_properties', 1000, False),
    ('property_expressions', '/api/config/event_sources/custom_properties/property_expressions', 1000, False),
    ('property_leef_expressions', '/api/config/event_sources/custom_properties/property_leef_expressions', 1000, False),
    ('property_cef_expressions', '/api/config/event_sources/custom_properties/property_cef_expressions', 1000, False),
    ('property_json_expressions', '/api/config/event_sources/custom_properties/property_json_expressions', 1000, False),
    ('property_xml_expressions', '/api/config/event_sources/custom_properties/property_xml_expressions', 1000, False),
    ('property_nvp_expressions', '/api/config/event_sources/custom_properties/property_nvp_expressions', 1000, False),
    ('property_genericlist_expressions', '/api/config/event_sources/custom_properties/property_genericlist_expressions', 1000, False),
    ('property_aql_expressions', '/api/config/event_sources/custom_properties/property_aql_expressions', 1000, False),
    ('property_calculated_expressions', '/api/config/event_sources/custom_properties/property_calculated_expressions', 1000, False),
]

UCM_REPORT_TIMEOUT = 600
EXPORT_TASK_TIMEOUT = 1800
UCM_POLL_INTERVAL = 2
EXPORT_POLL_INTERVAL = 3
EXPORT_PROGRESS_LOG_INTERVAL = 30

# Per-request socket-level timeouts
CONNECT_TIMEOUT = 30       # TCP + TLS handshake (curl --connect-timeout)
REQUEST_TIMEOUT = 300      # 5 min — normal API JSON requests
DOWNLOAD_TIMEOUT = 600     # 10 min — large file downloads (ZIPs, CSVs)

# Column names for the 18 calculated columns (order matters)
CALCULATED_COLUMNS = [
    'Log Source Types',
    'Log Source Status',
    'Log Source Count',
    'Log Source Groups',
    'Reference Sets',
    'Map of Sets',
    'Reference Maps',
    'QID Events',
    'Event Categories',
    'Custom Properties',
    'Rule References',
    'Content extension name',
    'Content category',
    'Extensions',
    'MITRE Tactics',
    'MITRE Techniques',
    'QRadar Version',
    'Version',
]

# Log sources report columns (order matters)
LOG_SOURCE_REPORT_COLUMNS = [
    'ls_id', 'ls_name', 'ls_description', 'ls_enabled',
    'ls_average_eps', 'ls_group_ids', 'ls_group_names', 'ls_status',
    'ls_last_event_time', 'lst_id', 'lst_name',
    'ext_name', 'ext_author', 'ext_version',
]

# Content type ID for custom rules in extensions
EXTENSION_CONTENT_TYPE_RULE = 3

# Streaming threshold for large JSON files (50 MB)
STREAMING_THRESHOLD_BYTES = 50 * 1024 * 1024


# ---------------------------------------------------------------------------
#  Exceptions
# ---------------------------------------------------------------------------

class CriticalPhaseError(Exception):
    """Raised when a phase fails irrecoverably. Aborts pipeline."""

    def __init__(self, phase, message, cause=None):
        self.phase = phase
        self.message = message
        self.cause = cause
        full = '[{0}] {1}'.format(phase, message)
        if cause:
            full = '{0} (caused by: {1})'.format(full, cause)
        Exception.__init__(self, full)


# ---------------------------------------------------------------------------
#  ErrorCounter
# ---------------------------------------------------------------------------

class ErrorCounter(object):
    """Track non-critical errors for summary reporting."""
    __slots__ = ('_errors',)

    def __init__(self):
        self._errors = []

    def increment(self, phase, message):
        """Record a non-critical error."""
        self._errors.append((phase, message))

    @property
    def count(self):
        """int: Number of recorded errors."""
        return len(self._errors)

    @property
    def errors(self):
        """list: Copy of (phase, message) tuples."""
        return list(self._errors)

    @property
    def has_errors(self):
        """bool: True if any errors recorded."""
        return len(self._errors) > 0


# ---------------------------------------------------------------------------
#  PipelineContext
# ---------------------------------------------------------------------------

class PipelineContext(object):
    """Shared state container for the pipeline run.

    All inter-phase data flows through this object.  All slots default
    to ``None`` and are populated by the framework or phase handlers.
    """
    __slots__ = (
        # Framework attributes (set during init)
        'host',
        'token',
        'api_version',
        'skip_ssl',
        'use_curl',
        'batch_size',
        'debug',
        'cache_dir',
        'output_dir',
        'temp_dir',
        'log_path',
        'timestamp',
        'error_counter',
        # Phase handler attributes (populated during pipeline execution)
        'api_client',
        'ucm_app_id',
        'ucm_csv_path',
        'mitre_data',
        'reference_data',
        'rule_ids',
        'export_zips',
        'decoded_rules',
        'rule_references',
        'parsed_rules',
        'expanded_rules',
        'enriched_csv',
        'log_sources',
        'active_days',
        'log_sources_flag',
        'log_sources_csv',
    )

    def __init__(self, **kwargs):
        """Initialize all slots to None, then apply kwargs."""
        for slot in self.__slots__:
            object.__setattr__(self, slot, None)
        for key, value in kwargs.items():
            if key in self.__slots__:
                object.__setattr__(self, key, value)

    def require(self, *attrs):
        """
        Validate that required attributes are set (not None).

        Args:
            *attrs: Attribute names to check.

        Raises:
            CriticalPhaseError: If any attribute is None.
        """
        missing = [a for a in attrs if getattr(self, a, None) is None]
        if missing:
            raise CriticalPhaseError(
                'CONTEXT',
                'Missing required context attributes: {0}'.format(
                    ', '.join(missing)
                )
            )

    def clear_credentials(self):
        """Remove API token and client from memory after API phases."""
        if self.api_client is not None:
            self.api_client.token = None
            self.api_client = None
        self.token = None


# ---------------------------------------------------------------------------
#  Utility Functions
# ---------------------------------------------------------------------------

def _create_ssl_context(skip_ssl):
    """
    Create an SSL context for HTTPS connections.

    Args:
        skip_ssl: If True, disable certificate verification.

    Returns:
        ssl.SSLContext: Configured SSL context.
    """
    logger = logging.getLogger(__name__)

    ctx = ssl.create_default_context()
    if skip_ssl:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        logger.warning('SSL certificate verification is disabled')
    else:
        logger.debug('SSL context created via create_default_context()')
    return ctx


def validate_json_response(body, endpoint):
    """
    Validate that an API response body is JSON, not HTML.

    Args:
        body:     Response body string.
        endpoint: API endpoint path (for error messages).

    Returns:
        Parsed JSON (dict or list).

    Raises:
        CriticalPhaseError: If response is HTML or unparseable JSON.
    """
    lower = body[:200].lower().lstrip() if body else ''
    if lower.startswith(('<!doctype', '<html', '<head')):
        raise CriticalPhaseError(
            'API',
            'Expected JSON from {0} but received an HTML page '
            '(possible web UI redirect or load balancer)'.format(
                endpoint
            )
        )
    try:
        return json.loads(body)
    except (ValueError, TypeError) as exc:
        raise CriticalPhaseError(
            'API',
            'Invalid JSON from {0}: {1}'.format(endpoint, exc)
        )


def _safe_parse_xml(source):
    """Parse an XML file with XXE and Billion Laughs protection.

    Args:
        source: str — file path to the XML document.

    Returns:
        xml.etree.ElementTree.ElementTree

    Raises:
        ET.ParseError: On malformed XML or entity declarations.
    """
    import xml.parsers.expat as expat

    _CHUNK = 65536  # 64 KiB read chunks for streaming scan

    # Pass 1: stream-scan with raw expat for entity declarations.
    scanner = expat.ParserCreate()

    def _reject_entity_decl(*args):
        raise ET.ParseError(
            'XML entity declarations are disabled for security'
        )

    scanner.EntityDeclHandler = _reject_entity_decl
    scanner.ExternalEntityRefHandler = lambda *a: False

    is_path = not hasattr(source, 'read')
    try:
        if is_path:
            with open(source, 'rb') as f:
                while True:
                    chunk = f.read(_CHUNK)
                    if not chunk:
                        scanner.Parse(b'', True)
                        break
                    scanner.Parse(chunk, False)
        else:
            while True:
                chunk = source.read(_CHUNK)
                if not chunk:
                    scanner.Parse(b'', True)
                    break
                scanner.Parse(chunk, False)
    except expat.ExpatError as exc:
        raise ET.ParseError(str(exc))

    # Pass 2: no entity declarations found — safe to parse (streaming).
    if is_path:
        return ET.parse(source)

    source.seek(0)
    return ET.parse(source)


def retry_with_backoff(func, max_retries=3, base_delay=2):
    """
    Call func() with exponential backoff retry on transient failures.

    Retries on HTTP status codes in RETRYABLE_HTTP_STATUSES and
    connection errors (IOError, URLError). Does NOT retry on
    HTTP 401, 403, 404, JSON parse errors, or file I/O errors.

    Args:
        func:        Callable with no arguments.
        max_retries: Maximum retry count (default 3).
        base_delay:  Initial delay in seconds (default 2).

    Returns:
        The return value of func() on success.

    Raises:
        The last exception after all retries exhausted.
    """
    logger = logging.getLogger(__name__)
    last_exc = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except CriticalPhaseError:
            raise
        except Exception as exc:
            last_exc = exc
            status = getattr(exc, 'code', None)

            # Do not retry on non-retryable HTTP statuses
            if status is not None and status not in RETRYABLE_HTTP_STATUSES:
                raise

            if attempt == max_retries:
                raise

            delay = base_delay * (2 ** attempt)
            logger.debug(
                'Retry {0}/{1} in {2}s: {3}'.format(
                    attempt + 1, max_retries, delay, exc
                )
            )
            time.sleep(delay)

    if last_exc is None:
        raise RuntimeError('retry_with_backoff: no attempts executed')
    raise last_exc


def save_json(data, filepath):
    """
    Write data as pretty-printed JSON with UTF-8 encoding.

    Creates parent directories if needed.

    Args:
        data:     Data to serialize (dict, list, etc.).
        filepath: Absolute path to output file.

    Raises:
        IOError: If file cannot be written.
    """
    logger = logging.getLogger(__name__)

    parent = os.path.dirname(filepath)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)

    content = json.dumps(data, indent=2, ensure_ascii=False)
    if PY2:
        content = content.encode('utf-8')
        with open(filepath, 'wb') as f:
            f.write(content)
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    size = os.path.getsize(filepath)
    logger.debug('Saved {0} ({1} bytes)'.format(filepath, size))


def iter_json_array(filepath, chunk_size=65536):
    """Iterate over objects in a JSON array file without loading it all.

    Malformed objects are skipped; truncated trailing objects are discarded.

    Args:
        filepath:   Absolute path to a JSON file containing a top-level
                    array of objects (``[ {…}, {…}, … ]``).
        chunk_size: Read buffer size in bytes (default 64 KB).

    Yields:
        dict: Each parsed object from the array.

    Raises:
        IOError: If the file cannot be opened.
    """
    logger = logging.getLogger(__name__)
    with io.open(filepath, 'r', encoding='utf-8') as f:
        buf = ''
        scan_pos = 0
        depth = 0
        in_string = False
        escape = False
        obj_start = -1

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            buf += chunk

            while scan_pos < len(buf):
                ch = buf[scan_pos]

                if escape:
                    escape = False
                    scan_pos += 1
                    continue

                if ch == '\\' and in_string:
                    escape = True
                    scan_pos += 1
                    continue

                if ch == '"':
                    in_string = not in_string
                    scan_pos += 1
                    continue

                if in_string:
                    scan_pos += 1
                    continue

                if ch == '{':
                    if depth == 0:
                        obj_start = scan_pos
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0 and obj_start >= 0:
                        obj_str = buf[obj_start:scan_pos + 1]
                        try:
                            yield json.loads(obj_str)
                        except (ValueError, TypeError):
                            logger.debug('Skipping malformed JSON object in %s', filepath)
                        obj_start = -1

                scan_pos += 1

            # Trim consumed data from the buffer.
            if obj_start >= 0:
                buf = buf[obj_start:]
                scan_pos -= obj_start
                obj_start = 0
            else:
                buf = ''
                scan_pos = 0

        # Detect truncated file (EOF with incomplete object).
        if depth > 0:
            logger.warning(
                'Possible file truncation in %s: EOF reached with '
                'incomplete JSON object (depth=%d)', filepath, depth)


def _extract_field(data, *candidates):
    """
    Extract a value from a dict by trying multiple field names.

    Args:
        data:       Dict to extract from.
        *candidates: Field names to try, in priority order.

    Returns:
        The value of the first matching key.

    Raises:
        KeyError: If none of the candidates are found.
    """
    for key in candidates:
        if key in data:
            return data[key]
    raise KeyError('None of {0} found in response'.format(candidates))


# ---------------------------------------------------------------------------
#  Transport Abstraction
# ---------------------------------------------------------------------------

class QRadarClientBase(object):
    """Abstract base for QRadar API transports."""
    __slots__ = ('host', 'token', 'api_version', 'skip_ssl', '_logger')

    def __init__(self, host, token, api_version=None, skip_ssl=False):
        self.host = host
        self.token = token
        self.api_version = api_version
        self.skip_ssl = skip_ssl
        self._logger = logging.getLogger(__name__)

    def _build_url(self, endpoint):
        """Build full URL: https://{host}{endpoint}."""
        return 'https://{0}{1}'.format(self.host, endpoint)

    def _build_headers(self, extra_headers=None):
        """Build default headers dict.

        To suppress a default header, pass it as None in extra_headers.
        """
        headers = {
            'SEC': self.token,
            'Version': self.api_version,
            'Accept': 'application/json',
        }
        if extra_headers:
            headers.update(extra_headers)
        return {k: v for k, v in headers.items() if v is not None}

    def _raw_request(self, method, url, headers, body=None):
        """Execute raw HTTP request (text only). Returns (status_code, body_text).

        Response body is decoded to str. Not for binary content;
        subclasses MUST override download_file() for binary safety.
        """
        raise NotImplementedError

    def get_json(self, endpoint, headers=None):
        """
        GET an endpoint and return parsed JSON.

        HTTP 401/403/SSL errors produce CriticalPhaseError with
        actionable guidance.

        Args:
            endpoint: API path (e.g., '/api/system/about').
            headers:  Optional extra headers (e.g., Range).

        Returns:
            dict or list: Parsed JSON response.

        Raises:
            CriticalPhaseError: On non-retryable HTTP errors or non-JSON.
        """
        url = self._build_url(endpoint)
        all_headers = self._build_headers(headers)

        def _do_request():
            status, body = self._raw_request('GET', url, all_headers)
            self._check_http_status(status, body, endpoint)
            return body

        body = retry_with_backoff(_do_request)
        return validate_json_response(body, endpoint)

    def post_json(self, endpoint, body=None, headers=None):
        """
        POST to an endpoint with optional JSON body, return parsed JSON.

        Args:
            endpoint: API path.
            body:     Dict to serialize as JSON body (or None).
            headers:  Optional extra headers.

        Returns:
            dict or list: Parsed JSON response.

        Raises:
            CriticalPhaseError: On non-retryable HTTP errors.
        """
        url = self._build_url(endpoint)
        extra = {'Content-Type': 'application/json'}
        if headers:
            extra.update(headers)
        all_headers = self._build_headers(extra)
        json_body = json.dumps(body) if body is not None else None

        def _do_request():
            status, resp_body = self._raw_request(
                'POST', url, all_headers, json_body
            )
            self._check_http_status(status, resp_body, endpoint)
            return resp_body

        resp_body = retry_with_backoff(_do_request)
        return validate_json_response(resp_body, endpoint)

    def download_file(self, endpoint, dest_path, headers=None):
        """
        GET an endpoint and write binary response to a file.

        Does NOT validate JSON. Writes directly to disk.

        Args:
            endpoint:  API path.
            dest_path: Local file path to write.
            headers:   Optional extra headers.

        Raises:
            CriticalPhaseError: On HTTP error or write failure.
        """
        url = self._build_url(endpoint)
        all_headers = self._build_headers(headers)

        def _do_request():
            status, body = self._raw_request('GET', url, all_headers)
            self._check_http_status(status, body, endpoint)
            return body

        body = retry_with_backoff(_do_request)

        if isinstance(body, str):
            body = body.encode('utf-8')
        with open(dest_path, 'wb') as f:
            f.write(body)

        self._logger.debug(
            'Downloaded {0} ({1} bytes)'.format(
                dest_path, os.path.getsize(dest_path)
            )
        )

    def _check_http_status(self, status, body, endpoint):
        """Check HTTP status and raise CriticalPhaseError for auth/perm errors."""
        if status == 401:
            raise CriticalPhaseError(
                'API',
                'HTTP 401 Unauthorized from {0}. '
                'Verify your API token is correct and not expired.'.format(
                    endpoint
                )
            )
        if status == 403:
            raise CriticalPhaseError(
                'API',
                'HTTP 403 Forbidden from {0}. '
                'The API token lacks required permissions.'.format(endpoint)
            )
        if status >= 400:
            err = HTTPError(
                self._build_url(endpoint), status,
                'HTTP {0} from {1}'.format(status, endpoint),
                {}, None
            )
            err.code = status
            err.read = lambda: ''
            raise err


class UrllibClient(QRadarClientBase):
    """
    HTTP transport using Python 3 stdlib urllib.

    Python 3 only — Python 2 always uses CurlClient.
    """
    __slots__ = ('_ssl_context',)

    def __init__(self, host, token, api_version=None, skip_ssl=False):
        QRadarClientBase.__init__(self, host, token, api_version, skip_ssl)
        self._ssl_context = _create_ssl_context(skip_ssl)

    def _raw_request(self, method, url, headers, body=None):
        """
        Execute HTTP request via urllib.request (Python 3).

        Returns:
            tuple: (status_code: int, response_body: str)
        """
        if body is not None and isinstance(body, str):
            body = body.encode('utf-8')
        req = urllib.request.Request(
            url, data=body, headers=headers, method=method
        )
        try:
            resp = urllib.request.urlopen(
                req, context=self._ssl_context,
                timeout=REQUEST_TIMEOUT
            )
            body_bytes = resp.read()
            return (resp.getcode(), body_bytes.decode('utf-8', 'replace'))
        except HTTPError as exc:
            body_bytes = exc.read()
            return (exc.code, body_bytes.decode('utf-8', 'replace'))

    def download_file(self, endpoint, dest_path, headers=None):
        """
        GET an endpoint and write the raw binary response to a file.

        Args:
            endpoint:  API path.
            dest_path: Local file path to write.
            headers:   Optional extra headers.

        Raises:
            CriticalPhaseError: On HTTP error or write failure.
        """
        url = self._build_url(endpoint)
        all_headers = self._build_headers(headers)

        def _do_download():
            req = urllib.request.Request(
                url, headers=all_headers, method='GET'
            )
            try:
                resp = urllib.request.urlopen(
                    req, context=self._ssl_context,
                    timeout=DOWNLOAD_TIMEOUT
                )
                status = resp.getcode()
                body_bytes = resp.read()
            except HTTPError as exc:
                status = exc.code
                body_bytes = exc.read()
                text_body = body_bytes.decode('utf-8', 'replace')
                self._check_http_status(status, text_body, endpoint)
                return body_bytes

            self._check_http_status(
                status, body_bytes.decode('utf-8', 'replace'), endpoint
            )
            return body_bytes

        body_bytes = retry_with_backoff(_do_download)

        with open(dest_path, 'wb') as f:
            f.write(body_bytes)

        self._logger.debug(
            'Downloaded {0} ({1} bytes)'.format(
                dest_path, os.path.getsize(dest_path)
            )
        )


class CurlClient(QRadarClientBase):
    """
    HTTP transport using curl subprocess.

    Fallback for Python 2.7.5 systems where ssl module lacks
    TLS 1.2 support.
    """
    __slots__ = ()

    def _raw_request(self, method, url, headers, body=None):
        """
        Execute HTTP request via curl subprocess.

        The SEC header is passed via stdin to avoid credential
        leakage in the process command line.

        Returns:
            tuple: (status_code: int, response_body: str)
        """
        cmd = ['curl', '-s', '-S', '-w', '\\n%{http_code}',
               '--connect-timeout', str(CONNECT_TIMEOUT),
               '--max-time', str(REQUEST_TIMEOUT)]
        if self.skip_ssl:
            cmd.append('-k')
        cmd.extend(['-X', method])
        # Separate SEC token from non-sensitive headers (Principle X)
        sec_value = None
        for key, value in headers.items():
            if key == 'SEC':
                sec_value = value
            else:
                cmd.extend(['-H', '{0}: {1}'.format(key, value)])
        if body:
            cmd.extend(['-d', body])
        cmd.append(url)

        # Pipe SEC header via stdin to keep it out of /proc/<pid>/cmdline
        stdin_data = None
        if sec_value is not None:
            cmd[1:1] = ['--config', '-']
            stdin_data = 'header = "SEC: {0}"\n'.format(sec_value).encode('utf-8')

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin_data is not None else None
            )
        except OSError as exc:
            raise CriticalPhaseError(
                'API',
                'curl binary not found. Install curl or remove --use-curl. '
                'Error: {0}'.format(exc)
            )

        communicate_kwargs = {'input': stdin_data}
        if not PY2:
            communicate_kwargs['timeout'] = REQUEST_TIMEOUT + 10
        try:
            stdout, stderr = proc.communicate(**communicate_kwargs)
        except Exception as exc:
            if _TimeoutExpired is not None and isinstance(exc, _TimeoutExpired):
                proc.kill()
                proc.communicate()
                raise CriticalPhaseError(
                    'API',
                    'curl process timed out after {0}s'.format(
                        REQUEST_TIMEOUT + 10
                    )
                )
            raise

        if proc.returncode != 0:
            raise CriticalPhaseError(
                'API',
                'curl exited with code {0}: {1}'.format(
                    proc.returncode,
                    stderr.decode('utf-8', 'replace').strip()
                )
            )

        output = stdout.decode('utf-8', 'replace')
        lines = output.rsplit('\n', 1)
        if len(lines) == 2:
            resp_body = lines[0]
            try:
                status_code = int(lines[1].strip())
            except ValueError:
                status_code = 0
        else:
            resp_body = output
            status_code = 0

        return (status_code, resp_body)

    def download_file(self, endpoint, dest_path, headers=None):
        """
        Download a file via curl to disk.

        Retries transient failures with exponential backoff.

        Args:
            endpoint:  API path.
            dest_path: Local file path to write.
            headers:   Optional extra headers.
        """
        url = self._build_url(endpoint)
        all_headers = self._build_headers(headers)

        # Transient curl exit codes that warrant a retry
        _TRANSIENT_CURL_EXITS = frozenset((
            6,   # Could not resolve host
            7,   # Failed to connect
            28,  # Operation timed out
            35,  # SSL connect error
            47,  # Too many redirects
            52,  # Server returned nothing
            55,  # Failed sending network data
            56,  # Failure in receiving network data
        ))

        def _do_download():
            cmd = ['curl', '-s', '-S', '-o', dest_path, '-w', '%{http_code}',
                   '--connect-timeout', str(CONNECT_TIMEOUT),
                   '--max-time', str(DOWNLOAD_TIMEOUT)]
            if self.skip_ssl:
                cmd.append('-k')
            cmd.extend(['-X', 'GET'])
            # Separate SEC token from non-sensitive headers (Principle X)
            sec_value = None
            for key, value in all_headers.items():
                if key == 'SEC':
                    sec_value = value
                else:
                    cmd.extend(['-H', '{0}: {1}'.format(key, value)])
            cmd.append(url)

            # Pipe SEC header via stdin to keep it out of /proc/<pid>/cmdline
            stdin_data = None
            if sec_value is not None:
                cmd[1:1] = ['--config', '-']
                stdin_data = 'header = "SEC: {0}"\n'.format(
                    sec_value
                ).encode('utf-8')

            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE if stdin_data is not None else None
                )
            except OSError as exc:
                raise CriticalPhaseError(
                    'API',
                    'curl binary not found: {0}'.format(exc)
                )

            communicate_kwargs = {'input': stdin_data}
            if not PY2:
                communicate_kwargs['timeout'] = DOWNLOAD_TIMEOUT + 10
            try:
                stdout, stderr = proc.communicate(**communicate_kwargs)
            except Exception as exc:
                if _TimeoutExpired is not None and isinstance(exc, _TimeoutExpired):
                    proc.kill()
                    proc.communicate()
                    raise CriticalPhaseError(
                        'API',
                        'curl download timed out after {0}s'.format(
                            DOWNLOAD_TIMEOUT + 10
                        )
                    )
                raise

            if proc.returncode != 0:
                msg = 'curl download failed (exit {0}): {1}'.format(
                    proc.returncode,
                    stderr.decode('utf-8', 'replace').strip()
                )
                if proc.returncode in _TRANSIENT_CURL_EXITS:
                    raise IOError(msg)
                raise CriticalPhaseError('API', msg)

            status_str = stdout.decode('utf-8', 'replace').strip()
            try:
                status_code = int(status_str)
            except ValueError:
                status_code = 0

            if status_code >= 400:
                self._check_http_status(status_code, '', endpoint)

        retry_with_backoff(_do_download)

        self._logger.debug(
            'Downloaded {0} ({1} bytes)'.format(
                dest_path, os.path.getsize(dest_path)
            )
        )


def create_api_client(context):
    """
    Create the appropriate API client based on Python version and flags.

    Python 2 always uses CurlClient (urllib2 lacks reliable TLS).
    Python 3 uses UrllibClient unless --use-curl is specified.

    Args:
        context: PipelineContext with host, token, api_version,
                 skip_ssl, use_curl.

    Returns:
        QRadarClientBase: UrllibClient or CurlClient instance.
    """
    logger = logging.getLogger(__name__)

    if PY2 or context.use_curl:
        if PY2:
            logger.info('Python 2 detected — using curl transport')
        else:
            logger.info('Using curl transport (--use-curl)')
        return CurlClient(
            context.host, context.token,
            context.api_version, context.skip_ssl
        )
    else:
        logger.info('Using urllib transport')
        return UrllibClient(
            context.host, context.token,
            context.api_version, context.skip_ssl
        )


# ---------------------------------------------------------------------------
#  Shared Endpoint Utilities
# ---------------------------------------------------------------------------

def paginate_endpoint(client, endpoint, page_size=1000):
    """
    Paginate a QRadar API endpoint using Range headers.

    Yields lists of items per page. Stops when response is empty
    or contains fewer items than page_size.

    Args:
        client:    QRadarClientBase instance.
        endpoint:  API path.
        page_size: Number of items per page (default 1000).

    Yields:
        list: Each page of items.
    """
    logger = logging.getLogger(__name__)
    offset = 0
    page_count = 0
    total_items = 0

    while True:
        headers = {
            'Range': 'items={0}-{1}'.format(offset, offset + page_size - 1)
        }
        page = client.get_json(endpoint, headers=headers)

        if not page:
            break

        page_count += 1
        total_items += len(page)
        logger.debug(
            'Page {0}: {1} items (total: {2})'.format(
                page_count, len(page), total_items
            )
        )
        yield page

        if len(page) < page_size:
            break
        offset += page_size


def poll_status(client, endpoint, interval=2, timeout=600,
                success_status='COMPLETED',
                failure_statuses=('FAILED', 'CANCELLED', 'ERROR'),
                progress_log_interval=30,
                extra_headers=None):
    """
    Poll a status endpoint until completion, failure, or timeout.

    Args:
        client:                QRadarClientBase instance.
        endpoint:              Full API path to poll.
        interval:              Seconds between polls (default 2).
        timeout:               Maximum seconds to wait (default 600).
        success_status:        Status string indicating success.
        failure_statuses:      Tuple of status strings indicating failure.
        progress_log_interval: Log progress every N seconds.
        extra_headers:         Optional dict of extra/override headers
                               (pass ``{'Version': None}`` to suppress).

    Returns:
        dict: Final status response when success_status reached.

    Raises:
        CriticalPhaseError: If failure status received or timeout.
    """
    logger = logging.getLogger(__name__)
    start = time.time()
    last_log = start

    while True:
        elapsed = time.time() - start
        if elapsed >= timeout:
            raise CriticalPhaseError(
                'API',
                'Timeout after {0}s waiting for {1}'.format(
                    int(elapsed), endpoint
                )
            )

        response = client.get_json(endpoint, headers=extra_headers)
        status = response.get('status', 'UNKNOWN')

        if status == success_status:
            logger.debug(
                'Status {0} reached after {1:.1f}s'.format(
                    success_status, elapsed
                )
            )
            return response

        if status in failure_statuses:
            raise CriticalPhaseError(
                'API',
                'Task failed with status {0}: {1}'.format(
                    status,
                    response.get('message', 'no details')
                )
            )

        now = time.time()
        if now - last_log >= progress_log_interval:
            logger.info(
                'Still waiting... status={0} elapsed={1:.0f}s'.format(
                    status, elapsed
                )
            )
            last_log = now

        time.sleep(interval)


# ---------------------------------------------------------------------------
#  Utility — XML Declaration Stripping
# ---------------------------------------------------------------------------

def _strip_xml_declaration(text):
    """Remove ``<?xml ...?>`` declaration from the start of *text*.

    Args:
        text: Unicode string (Py2 ``unicode`` / Py3 ``str``).

    Returns:
        Text with leading XML declaration removed.
        Returns original text unchanged if no declaration is found.
    """
    stripped = text.lstrip()
    if stripped.startswith('<?xml'):
        end = stripped.find('?>')
        if end != -1:
            stripped = stripped[end + 2:].lstrip()
    return stripped


# ---------------------------------------------------------------------------
#  BaseHandler
# ---------------------------------------------------------------------------

class BaseHandler(object):
    """
    Base class for pipeline phase handlers.

    Subclasses MUST override execute(context).
    Subclasses MUST document input/output context attributes in docstring.
    """
    __slots__ = ('name', 'phase_number')

    def __init__(self, name, phase_number):
        self.name = name
        self.phase_number = phase_number

    def execute(self, context):
        """Execute the phase logic. Subclasses MUST override."""
        raise NotImplementedError(
            '{0}.execute() must be implemented'.format(
                self.__class__.__name__
            )
        )


# ---------------------------------------------------------------------------
#  Phase Handlers
# ---------------------------------------------------------------------------

class CredentialCleanupHandler(BaseHandler):
    """Clear API credentials from memory after the last API phase."""
    __slots__ = ()

    def execute(self, context):
        context.clear_credentials()


class InitHandler(BaseHandler):
    """
    Initialize QRadar connection and verify API connectivity (Phase 0).

    Input:
        context.host, context.token, context.temp_dir,
        context.api_version, context.skip_ssl, context.use_curl

    Output:
        context.api_client (QRadarClientBase instance)

    Files produced:
        {temp_dir}/qradar_version.json

    Failure mode: CRITICAL — aborts pipeline.
    """
    __slots__ = ()

    def execute(self, context):
        context.require('host', 'token', 'temp_dir')
        logger = logging.getLogger(__name__)

        # Create API client
        client = create_api_client(context)

        # Test connectivity
        try:
            client.get_json('/api/help/versions')
            logger.info('QRadar API connection successful')
        except CriticalPhaseError:
            raise
        except Exception as exc:
            err_msg = text_type(exc).lower()
            if 'ssl' in err_msg or 'certificate' in err_msg:
                raise CriticalPhaseError(
                    'Initialization',
                    'SSL error connecting to {0}. '
                    'Try --skip-ssl-verify or --use-curl.'.format(
                        context.host
                    ),
                    cause=exc
                )
            raise CriticalPhaseError(
                'Initialization',
                'Cannot connect to {0}. '
                'Check the hostname/IP address is correct.'.format(
                    context.host
                ),
                cause=exc
            )

        # Fetch version
        try:
            about = client.get_json('/api/system/about')
            version = about.get('external_version', 'Unknown')
            logger.info('QRadar Version: {0}'.format(version))
            save_json(
                about,
                os.path.join(context.temp_dir, 'qradar_version.json')
            )
        except Exception as exc:
            logger.warning(
                'Could not retrieve QRadar version: {0}'.format(exc)
            )

        context.api_client = client


def _discover_ucm_app_id(client):
    """
    Discover the UCM application ID from installed QRadar applications.

    Args:
        client: QRadarClientBase instance.

    Returns:
        int or None: UCM application ID, or None if not found.
    """
    apps = client.get_json('/api/gui_app_framework/applications')
    for app_id_str, app_data in (
        apps.items() if isinstance(apps, dict) else
        [(text_type(i), a) for i, a in enumerate(apps)]
    ):
        manifest = app_data.get('manifest', {})
        app_name = manifest.get('name', '')
        if 'use case manager' in app_name.lower():
            try:
                return int(app_data.get('application_state', {})
                           .get('application_id', app_id_str))
            except (ValueError, TypeError):
                return int(app_id_str)
    return None


class UCMBaselineHandler(BaseHandler):
    """
    Export UCM baseline CSV report (Phase 1).

    Input:
        context.api_client, context.temp_dir

    Output:
        context.ucm_app_id (int), context.ucm_csv_path (str)

    Files produced:
        {temp_dir}/qradar_rules_ucm_export.csv

    Failure mode: CRITICAL — aborts pipeline.
    """
    __slots__ = ()

    def execute(self, context):
        if context.cache_dir:
            csv_path = os.path.join(
                context.cache_dir, 'qradar_rules_ucm_export.csv'
            )
            if not os.path.exists(csv_path):
                raise CriticalPhaseError(
                    'UCM Baseline',
                    'Cache file not found: {0}'.format(csv_path)
                )
            context.ucm_csv_path = csv_path
            return

        context.require('api_client', 'temp_dir')
        logger = logging.getLogger(__name__)
        client = context.api_client

        try:
            # Step 1: Discover UCM app ID
            ucm_app_id = _discover_ucm_app_id(client)

            if ucm_app_id is None:
                raise CriticalPhaseError(
                    'UCM Baseline',
                    'Use Case Manager application not found on this '
                    'QRadar console.'
                )

            logger.info('UCM application found (ID: {0})'.format(ucm_app_id))
            context.ucm_app_id = ucm_app_id

            base = '/console/plugins/{0}/app_proxy/api'.format(ucm_app_id)

            # UCM proxy endpoints do NOT accept the Version header.
            # Contract specifies only SEC, Content-Type, Accept.
            no_ver = {'Version': None}

            # Step 2: Create report
            columns_str = ','.join(UCM_REPORT_COLUMNS)
            report_resp = client.post_json(
                '{0}/use_case_explorer'.format(base),
                {'columns': list(UCM_REPORT_COLUMNS), 'filters': []},
                headers=no_ver
            )
            report_id = _extract_field(
                report_resp, 'report_id', 'reportId', 'id'
            )
            logger.info('Report created, polling for completion...')

            # Step 3: Poll report status
            poll_status(
                client,
                '{0}/use_case_explorer/{1}/status'.format(base, report_id),
                interval=UCM_POLL_INTERVAL,
                timeout=UCM_REPORT_TIMEOUT,
                extra_headers=no_ver
            )

            # Step 4: Create CSV download job
            csv_resp = client.post_json(
                '{0}/use_case_explorer/{1}/download_csv'.format(
                    base, report_id
                ),
                {'columns': columns_str},
                headers=no_ver
            )
            job_id = _extract_field(csv_resp, 'job_id', 'jobId')

            # Step 5: Poll CSV job status
            poll_status(
                client,
                '{0}/use_case_explorer/download_csv/{1}/status'.format(
                    base, job_id
                ),
                interval=UCM_POLL_INTERVAL,
                timeout=UCM_REPORT_TIMEOUT,
                extra_headers=no_ver
            )

            # Step 6: Download CSV
            csv_name = 'qradar_rules_ucm_export.csv'
            csv_path = os.path.join(context.temp_dir, csv_name)
            client.download_file(
                '{0}/use_case_explorer/download_csv/{1}/result'
                '?csvName={2}'.format(base, job_id, csv_name),
                csv_path,
                headers=no_ver
            )
            logger.info('Report completed, downloaded CSV')
            context.ucm_csv_path = csv_path

        except CriticalPhaseError:
            raise
        except Exception as exc:
            raise CriticalPhaseError(
                'UCM Baseline',
                'UCM Baseline Export failed: {0}'.format(exc),
                cause=exc
            )


class MitreMappingHandler(BaseHandler):
    """
    Export MITRE ATT&CK mappings from UCM application (Phase 2).

    Input:
        context.api_client, context.temp_dir, context.ucm_app_id

    Output:
        context.mitre_data (dict)

    Files produced:
        {temp_dir}/mitre_mappings.json

    Failure mode: NON-CRITICAL — creates stub on failure.
    """
    __slots__ = ()

    def execute(self, context):
        if context.cache_dir:
            cache_path = os.path.join(
                context.cache_dir, 'mitre_mappings.json'
            )
            if os.path.exists(cache_path):
                with io.open(cache_path, 'r', encoding='utf-8') as f:
                    context.mitre_data = json.load(f)
                return
            # No cached file — create stub
            context.mitre_data = {'error': 'No cached file', 'mappings': {}}
            return

        context.require('api_client', 'temp_dir')
        logger = logging.getLogger(__name__)
        client = context.api_client

        # Determine UCM app ID
        ucm_app_id = context.ucm_app_id
        if ucm_app_id is None:
            # Fallback: try discovering UCM via shared utility
            try:
                ucm_app_id = _discover_ucm_app_id(client)
            except Exception as exc:
                logger.warning(
                    'UCM app discovery failed for MITRE: {0}'.format(exc)
                )

        if ucm_app_id is None:
            logger.warning(
                'UCM application not found — creating MITRE stub'
            )
            stub = {
                'error': 'UCM application not found',
                'mappings': {}
            }
            save_json(
                stub,
                os.path.join(context.temp_dir, 'mitre_mappings.json')
            )
            context.mitre_data = stub
            if context.error_counter:
                context.error_counter.increment(
                    'MITRE Mappings', 'UCM application not found'
                )
            return

        # Fetch MITRE mappings
        endpoint = '/console/plugins/{0}/app_proxy/api/mappings'.format(
            ucm_app_id
        )
        try:
            data = client.get_json(endpoint)
            save_json(
                data,
                os.path.join(context.temp_dir, 'mitre_mappings.json')
            )
            context.mitre_data = data
            logger.info('MITRE mappings collected')
        except Exception as exc:
            logger.warning(
                'MITRE mappings fetch failed: {0}'.format(exc)
            )
            stub = {
                'error': 'MITRE mappings fetch failed: {0}'.format(exc),
                'mappings': {}
            }
            save_json(
                stub,
                os.path.join(context.temp_dir, 'mitre_mappings.json')
            )
            context.mitre_data = stub
            if context.error_counter:
                context.error_counter.increment(
                    'MITRE Mappings', text_type(exc)
                )


class ReferenceDataHandler(BaseHandler):
    """
    Collect reference data from QRadar API endpoints (Phase 3).

    Input:
        context.api_client, context.temp_dir

    Output:
        context.reference_data (dict mapping name -> list of records)

    Files produced:
        One JSON file per endpoint in {temp_dir}/

    Failure mode: CRITICAL — aborts pipeline on any endpoint failure.
    """
    __slots__ = ()

    def execute(self, context):
        if context.cache_dir:
            reference_data = {}
            for entry in REFERENCE_DATA_ENDPOINTS:
                if len(entry) == 4:
                    name, _, _, critical = entry
                else:
                    name = entry[0]
                    critical = True
                cache_path = os.path.join(
                    context.cache_dir, '{0}.json'.format(name)
                )
                if os.path.exists(cache_path):
                    with io.open(cache_path, 'r', encoding='utf-8') as f:
                        reference_data[name] = json.load(f)
                elif not critical:
                    logging.getLogger(__name__).warning(
                        'Cache file not found (non-critical): {0}'.format(
                            cache_path)
                    )
                    reference_data[name] = []
                else:
                    raise CriticalPhaseError(
                        'Reference Data',
                        'Cache file not found: {0}'.format(cache_path)
                    )
            context.reference_data = reference_data
            return

        context.require('api_client', 'temp_dir')
        logger = logging.getLogger(__name__)
        client = context.api_client
        total = len(REFERENCE_DATA_ENDPOINTS)
        reference_data = {}

        for i, entry in enumerate(REFERENCE_DATA_ENDPOINTS, 1):
            if len(entry) == 4:
                name, endpoint, page_size, critical = entry
            else:
                name, endpoint, page_size = entry
                critical = True

            logger.info(
                'Collecting {0} ({1}/{2})'.format(name, i, total)
            )
            all_items = []
            try:
                for page in paginate_endpoint(client, endpoint, page_size):
                    all_items.extend(page)
            except Exception as exc:
                if critical:
                    raise CriticalPhaseError(
                        'Reference Data',
                        'Failed to collect {0}: {1}'.format(name, exc),
                        cause=exc
                    )
                else:
                    logger.warning(
                        'Non-critical endpoint {0} failed: {1}'.format(
                            name, exc)
                    )
                    reference_data[name] = []
                    continue

            save_json(
                all_items,
                os.path.join(context.temp_dir, '{0}.json'.format(name))
            )
            logger.info(
                '{0}: {1} records collected'.format(name, len(all_items))
            )
            reference_data[name] = all_items

        context.reference_data = reference_data


class RuleIdHandler(BaseHandler):
    """
    Fetch rule and building block IDs (Phase 4).

    Input:
        context.api_client, context.temp_dir

    Output:
        context.rule_ids (dict with 'rules' and 'building_blocks')

    Files produced:
        {temp_dir}/rule_ids.json, {temp_dir}/building_block_ids.json

    Failure mode: CRITICAL — aborts pipeline.
    """
    __slots__ = ()

    def execute(self, context):
        if context.cache_dir:
            with io.open(os.path.join(
                context.cache_dir, 'rule_ids.json'
            ), 'r', encoding='utf-8') as f:
                rule_ids = json.load(f)
            with io.open(os.path.join(
                context.cache_dir, 'building_block_ids.json'
            ), 'r', encoding='utf-8') as f:
                bb_ids = json.load(f)
            context.rule_ids = {
                'rules': rule_ids,
                'building_blocks': bb_ids
            }
            return

        context.require('api_client', 'temp_dir')
        logger = logging.getLogger(__name__)
        client = context.api_client

        try:
            # Fetch rule IDs
            rule_ids = []
            for page in paginate_endpoint(
                client, '/api/analytics/rules', page_size=1000
            ):
                rule_ids.extend(record['id'] for record in page)
            save_json(
                rule_ids,
                os.path.join(context.temp_dir, 'rule_ids.json')
            )

            # Fetch building block IDs
            bb_ids = []
            for page in paginate_endpoint(
                client, '/api/analytics/building_blocks', page_size=1000
            ):
                bb_ids.extend(record['id'] for record in page)
            save_json(
                bb_ids,
                os.path.join(context.temp_dir, 'building_block_ids.json')
            )
        except CriticalPhaseError:
            raise
        except Exception as exc:
            raise CriticalPhaseError(
                'Fetch Rule IDs',
                'Failed to fetch rule/building block IDs: {0}'.format(exc),
                cause=exc
            )

        context.rule_ids = {
            'rules': rule_ids,
            'building_blocks': bb_ids
        }
        logger.info(
            'Found {0} rules and {1} building blocks'.format(
                len(rule_ids), len(bb_ids)
            )
        )


class RuleExportHandler(BaseHandler):
    """
    Export rules in batches to ZIP archives (Phase 5).

    Input:
        context.api_client, context.temp_dir, context.rule_ids,
        context.batch_size

    Output:
        context.export_zips (list of str)

    Files produced:
        {temp_dir}/export_batch_1.zip, export_batch_2.zip, ...

    Failure mode: MIXED — per-batch non-critical.
    """
    __slots__ = ()

    def execute(self, context):
        if context.cache_dir:
            import glob
            pattern = os.path.join(context.cache_dir, 'export_batch_*.zip')
            context.export_zips = sorted(glob.glob(pattern))
            return

        context.require('api_client', 'temp_dir', 'rule_ids', 'batch_size')
        logger = logging.getLogger(__name__)
        client = context.api_client

        all_ids = (
            context.rule_ids['rules'] +
            context.rule_ids['building_blocks']
        )

        # Divide into batches
        batch_size = context.batch_size
        batches = []
        for i in range(0, len(all_ids), batch_size):
            batches.append(all_ids[i:i + batch_size])

        total = len(batches)
        successful_zips = []
        failed_count = 0

        for n, batch in enumerate(batches, 1):
            logger.info(
                'Exporting batch {0}/{1} ({2} items)...'.format(
                    n, total, len(batch)
                )
            )
            try:
                # Create export task
                task_resp = client.post_json(
                    '/api/config/extension_management/extension_export_tasks',
                    {
                        'export_contents': [{
                            'content_type': 'CUSTOM_RULES',
                            'content_item_ids': [
                                text_type(rid) for rid in batch
                            ],
                            'related_content': []
                        }]
                    }
                )
                task_id = _extract_field(task_resp, 'task_id', 'id')

                # Poll task status
                poll_status(
                    client,
                    '/api/config/extension_management/'
                    'extensions_task_status/{0}'.format(task_id),
                    interval=EXPORT_POLL_INTERVAL,
                    timeout=EXPORT_TASK_TIMEOUT,
                    progress_log_interval=EXPORT_PROGRESS_LOG_INTERVAL
                )

                # Download ZIP
                zip_path = os.path.join(
                    context.temp_dir,
                    'export_batch_{0}.zip'.format(n)
                )
                client.download_file(
                    '/api/config/extension_management/'
                    'extension_export_tasks/{0}/extension_export'.format(
                        task_id
                    ),
                    zip_path,
                    headers={'Accept': 'application/zip'}
                )
                successful_zips.append(zip_path)

            except Exception as exc:
                logger.error(
                    'Batch {0}/{1} failed: {2}'.format(n, total, exc)
                )
                if context.error_counter:
                    context.error_counter.increment(
                        'Rule Export',
                        'Batch {0} failed: {1}'.format(n, exc)
                    )
                failed_count += 1

        context.export_zips = successful_zips

        if total > 0 and len(successful_zips) == 0:
            logger.warning(
                'ALL {0} export batches failed — no rule data exported'.format(
                    total
                )
            )
        else:
            logger.info(
                '{0} of {1} batches exported successfully'.format(
                    len(successful_zips), total
                )
            )


# ---------------------------------------------------------------------------
#  Phase 6: XML Decode Handler
# ---------------------------------------------------------------------------

class XmlDecodeHandler(BaseHandler):
    """
    Extract and decode XML from ZIP exports (Phase 6).

    Input:
        context.temp_dir      - Workspace folder path
        context.export_zips   - List of ZIP file paths (set by Phase 5)
        context.error_counter - Shared ErrorCounter instance

    Output:
        context.decoded_rules - Path to decoded_rules.xml file

    Files produced:
        {temp_dir}/decoded_rules.xml

    Failure mode: CRITICAL if zero rules decoded;
                  NON-CRITICAL for individual skip/error (ErrorCounter).
    """
    __slots__ = ()

    def execute(self, context):
        context.require('temp_dir', 'export_zips')
        logger = logging.getLogger(__name__)
        start_time = time.time()

        zip_paths = context.export_zips
        if not zip_paths:
            raise CriticalPhaseError(
                'XML Decode',
                'No export ZIP files in context'
            )

        output_path = os.path.join(context.temp_dir, 'decoded_rules.xml')
        processed_uuids = set()
        total_rules = 0
        total_duplicates = 0
        total_skipped = 0
        total_zips_ok = 0
        total_zips_skipped = 0
        num_zips = len(zip_paths)

        try:
            out_f = io.open(output_path, 'w', encoding='utf-8')
        except (IOError, OSError) as exc:
            raise CriticalPhaseError(
                'XML Decode',
                'Cannot create output file {0}: {1}'.format(
                    output_path, exc
                )
            )
        try:
            out_f.write(u'<?xml version="1.0" encoding="UTF-8"?>\n')
            out_f.write(u'<content source="multiple_batch_exports">\n')

            for zip_idx, zip_path in enumerate(zip_paths, 1):
                zip_name = os.path.basename(zip_path)
                logger.info(
                    'Processing ZIP {0} of {1}: {2}'.format(
                        zip_idx, num_zips, zip_name
                    )
                )

                extract_dir = tempfile.mkdtemp(
                    dir=context.temp_dir, prefix='temp_extract_'
                )
                try:
                    # --- Extract ZIP ---
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zf:
                            # Integrity check (Finding 9)
                            bad_member = zf.testzip()
                            if bad_member is not None:
                                msg = ('Corrupt ZIP member: '
                                       '{0}'.format(bad_member))
                                logger.warning(
                                    'Skipping ZIP {0}: '
                                    '{1}'.format(zip_name, msg)
                                )
                                if context.error_counter:
                                    context.error_counter.increment(
                                        'XML Decode', msg)
                                total_zips_skipped += 1
                                continue
                            # Validate member paths to prevent Zip Slip
                            # (CVE-2007-4559) on Python < 3.12
                            real_dest = os.path.realpath(extract_dir)
                            for member in zf.namelist():
                                member_path = os.path.realpath(
                                    os.path.join(extract_dir, member)
                                )
                                if not (member_path == real_dest
                                        or member_path.startswith(
                                            real_dest + os.sep)):
                                    raise CriticalPhaseError(
                                        'XML Decode',
                                        'Zip Slip detected in {0}: member '
                                        '{1} escapes extract '
                                        'directory'.format(zip_name, member)
                                    )
                            zf.extractall(extract_dir)
                    except (_BadZipFile, IOError, OSError) as exc:
                        msg = 'Corrupt or unreadable ZIP: {0}'.format(exc)
                        logger.warning(
                            'Skipping ZIP {0}: {1}'.format(zip_name, msg)
                        )
                        logger.debug(
                            'ZIP extraction failed — file={0}, '
                            'error_type={1}, error={2}, '
                            'stage=extraction'.format(
                                zip_name,
                                type(exc).__name__,
                                exc,
                            )
                        )
                        if context.error_counter:
                            context.error_counter.increment(
                                'XML Decode', msg
                            )
                        total_zips_skipped += 1
                        continue

                    # --- Locate custom_rule*.xml ---
                    xml_file = None
                    for fname in os.listdir(extract_dir):
                        if (fname.startswith('custom_rule')
                                and fname.endswith('.xml')):
                            xml_file = fname
                            break

                    if xml_file is None:
                        msg = 'No custom_rule*.xml found in ZIP'
                        logger.warning(
                            'Skipping ZIP {0}: {1}'.format(zip_name, msg)
                        )
                        logger.debug(
                            'XML discovery failed — file={0}, '
                            'contents={1}, '
                            'stage=xml_discovery'.format(
                                zip_name,
                                os.listdir(extract_dir),
                            )
                        )
                        if context.error_counter:
                            context.error_counter.increment(
                                'XML Decode', msg
                            )
                        total_zips_skipped += 1
                        continue

                    xml_path = os.path.join(extract_dir, xml_file)

                    # --- Parse XML ---
                    try:
                        tree = _safe_parse_xml(xml_path)
                    except ET.ParseError as exc:
                        msg = 'Malformed XML in {0}: {1}'.format(
                            xml_file, exc
                        )
                        logger.warning(
                            'Skipping ZIP {0}: {1}'.format(zip_name, msg)
                        )
                        logger.debug(
                            'XML parsing failed — file={0}, '
                            'xml_file={1}, error_type={2}, '
                            'error={3}, stage=xml_parsing'.format(
                                zip_name, xml_file,
                                type(exc).__name__, exc,
                            )
                        )
                        if context.error_counter:
                            context.error_counter.increment(
                                'XML Decode', msg
                            )
                        total_zips_skipped += 1
                        continue

                    root = tree.getroot()

                    # --- Process each <custom_rule> ---
                    for cr_elem in root.findall('.//custom_rule'):
                        # Extract metadata
                        id_elem = cr_elem.find('id')
                        uuid_elem = cr_elem.find('uuid')
                        origin_elem = cr_elem.find('origin')

                        rule_id = (id_elem.text
                                   if id_elem is not None else '')
                        uuid_val = (uuid_elem.text
                                    if uuid_elem is not None else None)
                        origin_val = (origin_elem.text
                                      if origin_elem is not None else '')

                        # Deduplication
                        if uuid_val and uuid_val in processed_uuids:
                            logger.debug(
                                'Duplicate UUID {0} — skipping '
                                '(source ZIP: {1})'.format(
                                    uuid_val, zip_name
                                )
                            )
                            total_duplicates += 1
                            continue
                        if uuid_val:
                            processed_uuids.add(uuid_val)
                        else:
                            logger.warning(
                                'Rule (id={0}) has no UUID '
                                '— cannot deduplicate'.format(rule_id)
                            )

                        # Read rule_data
                        rd_elem = cr_elem.find('rule_data')
                        raw_text = (rd_elem.text
                                    if rd_elem is not None else None)
                        if not raw_text or not raw_text.strip():
                            msg = ('Empty or missing rule_data '
                                   '(id={0})'.format(rule_id))
                            logger.warning(
                                'Skipping rule (id={0}): '
                                'empty rule_data'.format(rule_id)
                            )
                            logger.debug(
                                'Rule data empty — file={0}, '
                                'rule_id={1}, uuid={2}, '
                                'stage=rule_data_read'.format(
                                    zip_name, rule_id, uuid_val,
                                )
                            )
                            if context.error_counter:
                                context.error_counter.increment(
                                    'XML Decode', msg
                                )
                            total_skipped += 1
                            continue

                        # Base64 decode
                        try:
                            decoded_bytes = base64.b64decode(
                                raw_text.strip()
                            )
                            decoded_str = decoded_bytes.decode('utf-8')
                        except Exception as exc:
                            msg = ('Base64 decode failed for rule '
                                   'id={0}: {1}'.format(rule_id, exc))
                            logger.warning(
                                'Skipping rule (id={0}): '
                                'base64 decode failed'.format(rule_id)
                            )
                            logger.debug(
                                'Base64 decode error — file={0}, '
                                'rule_id={1}, uuid={2}, '
                                'error_type={3}, error={4}, '
                                'stage=base64_decode'.format(
                                    zip_name, rule_id, uuid_val,
                                    type(exc).__name__, exc,
                                )
                            )
                            if context.error_counter:
                                context.error_counter.increment(
                                    'XML Decode', msg
                                )
                            total_skipped += 1
                            continue

                        # Strip nested XML declaration
                        decoded_str = _strip_xml_declaration(decoded_str)

                        # Write to output — streaming
                        uuid_attr = uuid_val if uuid_val else ''
                        out_f.write(
                            u'    <custom_rule id="{0}" uuid="{1}" '
                            u'origin="{2}">\n'.format(
                                rule_id, uuid_attr, origin_val
                            )
                        )
                        for line in decoded_str.splitlines():
                            out_f.write(
                                u'        {0}\n'.format(line)
                            )
                        out_f.write(u'    </custom_rule>\n')
                        total_rules += 1

                    total_zips_ok += 1

                finally:
                    shutil.rmtree(extract_dir, ignore_errors=True)

            out_f.write(u'</content>\n')
        except (IOError, OSError) as exc:
            raise CriticalPhaseError(
                'XML Decode',
                'I/O error writing {0}: {1}'.format(output_path, exc)
            )
        finally:
            out_f.close()

        if total_rules == 0:
            raise CriticalPhaseError(
                'XML Decode',
                'Decoded zero rules from {0} ZIP files'.format(num_zips)
            )

        context.decoded_rules = output_path

        elapsed = time.time() - start_time
        logger.info(
            'Decoded {0} rules from {1} ZIPs. '
            'Duplicates skipped: {2}. '
            'Rules skipped (errors): {3}. '
            'ZIPs skipped (errors): {4}. '
            'Elapsed: {5:.1f}s.'.format(
                total_rules, total_zips_ok,
                total_duplicates, total_skipped,
                total_zips_skipped, elapsed,
            )
        )


# ---------------------------------------------------------------------------
#  Phase 7: Reference Extraction Helper Functions
# ---------------------------------------------------------------------------

def _classify_dependency(method_attr, test_name):
    """
    Classify a parameter's dependency type based on method attribute or test name.
    
    Args:
        method_attr: String from <userOptions method="..."> (may be empty)
        test_name: String from <test name="..."> (may be empty)
    
    Returns:
        str or None: Field name from DEPENDENCY_TYPES, or None if
        unrecognized.
    """
    if not method_attr:
        method_attr = ''
    
    method_lower = method_attr.lower()
    
    # === Primary Classifier: Method Substring Match ===
    
    # Rule/Building Block references
    if ('geteventrules' in method_lower or
        'getcommonrules' in method_lower or
        'getflowrules' in method_lower):
        return 'rule_uuid_refs'
    
    # Reference data
    if 'getreferencesets' in method_lower:
        return 'reference_sets'
    if 'getreferencemaps' in method_lower:
        return 'reference_maps'
    if ('getreferencemapofsets' in method_lower or
        'getreferencedatamapsofsets' in method_lower):
        return 'reference_map_of_sets'
    
    # Event classification
    if 'getqidsbylowlevelcategory' in method_lower:
        return 'qids'
    if 'getcategories' in method_lower:
        return 'event_categories'
    
    # Log source classification
    if ('getdevices' in method_lower or
        'getlogsourcesbydevicetypeids' in method_lower):
        return 'device_ids'
    if 'getdevicetypedescs' in method_lower:
        return 'device_type_ids'
    if 'getsensordevicestreeroot' in method_lower:
        return 'device_group_ids'
    
    # Event properties (custom property references)
    if 'geteventdatabasefields' in method_lower:
        return 'event_properties'
    
    # === Fallback Classifier: Test Name Exact Match ===
    
    if test_name == 'QID_Test':
        return 'qids'
    if test_name == 'DeviceID_Test':
        return 'device_ids'
    if test_name == 'DeviceGroupID_Test':
        return 'device_group_ids'
    if test_name == 'DeviceTypeID_Test':
        return 'device_type_ids'
    if test_name == 'EventCategory_Test':
        return 'event_categories'
    
    # === Unrecognized (Forward Compatibility) ===
    return None  # Caller will silently skip


def _parse_comma_separated(text):
    """
    Parse comma-separated text into list of non-empty stripped values.
    
    Args:
        text: String from <userSelection> (may contain commas, whitespace)
    
    Returns:
        List of non-empty strings (after strip)
    
    Examples:
        "a, b, c"     → ['a', 'b', 'c']
        "a,b,c"       → ['a', 'b', 'c']
        ",,,  , "     → []
        "  a  ,  b  " → ['a', 'b']
        ""            → []
    """
    if not text:
        return []
    
    result = []
    for value in text.split(','):
        stripped = value.strip()
        if stripped:  # Non-empty after stripping
            result.append(stripped)
    
    return result


# LST-relevant dependency types (subset of the 9 types from _classify_dependency)
_LST_DEP_TYPES = frozenset([
    'device_type_ids', 'event_categories', 'qids',
    'event_properties', 'device_group_ids', 'device_ids',
])

# Test types where getEventDatabaseFields is used operationally, not for LST filtering.
# These specify WHICH FIELD TO OPERATE ON (lookup key, grouping field), not which LSTs apply.
# Without this blacklist, operational parameters create false empty-set LST tests
# (system property → None → negation → empty set → false 'disjoint' status).
_NON_LST_FILTER_TESTS = frozenset([
    'ReferenceSetTest',      # Parameter 2: lookup field (which field to check in reference sets)
    'ReferenceDataTest',     # Parameters 2,4: key/value lookup fields (reference map lookup)
    'MatchCount',            # Parameters 3,4: grouping keys (same X, different Y aggregation)
    'TriggerMatchCount',     # Similar aggregation grouping
    'TriggerTimeout',        # Correlation field (operational)
])

# ArielFilter key-to-dependency-type mapping (7 standard keys)
_ARIEL_FILTER_KEY_MAP = {
    'device': 'device_ids',
    'deviceType': 'device_type_ids',
    'deviceGroup': 'device_group_ids',
    'qidNumber': 'qids',
    'category': 'event_categories',
    'highLevelCategory': 'event_categories',
    'creEventList': 'cre_event_list',
}

# Valid ArielFilter operators and negation subset
_ARIEL_FILTER_OPERATORS = frozenset(['EQ', 'NEQ', 'EQany', 'NEQany'])
_ARIEL_FILTER_NEGATE_OPS = frozenset(['NEQ', 'NEQany'])


def _parse_ariel_filter(user_selection_text, known_property_names,
                        rule_uuid=''):
    """Parse an ArielFilter <userSelection> string into dependencies and LST entries.

    Splits on U+E000 to produce triplets (key, operator, value), then
    classifies each triplet via _ARIEL_FILTER_KEY_MAP.  Multi-value entries
    (U+FFFD-separated) are split.  Same-key same-polarity triplets are
    merged into single LST test entries.

    Args:
        user_selection_text: Raw text from <userSelection> element.
        known_property_names: set of custom property names from API data.
        rule_uuid: UUID of the rule being processed (for log messages).

    Returns:
        tuple: (deps, lst_entries, cre_ids)
            deps       — dict {dep_type: [values]} for positive standard keys
            lst_entries — list of LST test entry dicts
            cre_ids    — list of {'id': str, 'negate': bool} for creEventList
    """
    logger = logging.getLogger(__name__)
    empty = ({}, [], [])

    if not user_selection_text or not user_selection_text.strip():
        logger.debug('ArielFilter: empty userSelection — skipping')
        return empty

    tokens = user_selection_text.split(u'\ue000')
    if len(tokens) % 3 != 0:
        logger.warning(
            'ArielFilter: token count {0} not divisible by 3 — skipping'
            ' (rule {1})'.format(len(tokens), rule_uuid)
        )
        return empty

    deps = {}
    cre_ids = []
    # Merge dict keyed by (dep_type, negate) to OR same-key same-polarity
    merge = {}

    for i in range(0, len(tokens), 3):
        key = tokens[i]
        operator = tokens[i + 1]
        raw_value = tokens[i + 2]

        # Split multi-value on U+FFFD
        values = [v for v in raw_value.split(u'\ufffd') if v]

        # Classify key FIRST — custom properties bypass operator validation
        dep_type = _ARIEL_FILTER_KEY_MAP.get(key)

        if dep_type is None:
            # Not a standard key — check custom property names.
            # For custom properties, operators are irrelevant: the
            # property name alone drives LST resolution.  Negate is
            # always False because the rule requires the property
            # regardless of how it tests the value.
            if known_property_names and key in known_property_names:
                if 'event_properties' not in deps:
                    deps['event_properties'] = []
                if key not in deps['event_properties']:
                    deps['event_properties'].append(key)

                bucket = ('event_properties', False)
                if bucket not in merge:
                    merge[bucket] = []
                if key not in merge[bucket]:
                    merge[bucket].append(key)
            else:
                logger.debug(
                    'ArielFilter: unknown key {0!r} — skipping'.format(key)
                )
            continue

        # Standard key or creEventList — validate operator strictly
        if operator not in _ARIEL_FILTER_OPERATORS:
            logger.warning(
                'ArielFilter: unrecognised operator {0!r} for key '
                '{1!r} — skipping triplet (rule {2})'
                .format(operator, key, rule_uuid)
            )
            continue

        is_negate = operator in _ARIEL_FILTER_NEGATE_OPS

        if dep_type == 'cre_event_list':
            # creEventList — accumulate as CRE ID references
            for v in values:
                cre_ids.append({'id': v, 'negate': is_negate})
        else:
            # Standard key — add to deps (positive only) and LST merge
            if not is_negate:
                if dep_type not in deps:
                    deps[dep_type] = []
                deps[dep_type].extend(values)

            if dep_type in _LST_DEP_TYPES:
                bucket = (dep_type, is_negate)
                if bucket not in merge:
                    merge[bucket] = []
                merge[bucket].extend(values)

    # Emit merged LST test entries
    lst_entries = []
    for (dt, neg), vals in sorted(merge.items()):
        lst_entries.append({
            'dep_type': dt,
            'values': vals,
            'negate': neg,
        })

    return (deps, lst_entries, cre_ids)


def _extract_lst_tests(test_definitions_elem):
    # type: (xml.etree.ElementTree.Element) -> tuple
    """Extract per-test LST constraints and BB reference groups.

    Iterates <test> elements, preserving per-test granularity and negate
    flags.  For BB-referencing tests (RuleMatch_Test, ThresholdFunction_Test)
    builds BBRefGroup dicts with any/all mode.

    Args:
        test_definitions_elem: The <testDefinitions> XML element.

    Returns:
        tuple: (lst_tests, bb_ref_groups)
            lst_tests  — list of dicts with dep_type/values/negate
            bb_ref_groups — list of dicts with uuids/mode/negate
    """
    lst_tests = []
    bb_ref_groups = []

    for test in test_definitions_elem.findall('test'):
        test_name = test.get('name', '')
        negate = test.get('negate', '').lower() == 'true'

        parameters = test.findall('parameter')
        bb_uuids = []

        for parameter in parameters:
            user_options = parameter.find('userOptions')
            method_attr = (user_options.get('method', '')
                          if user_options is not None
                          else '')

            user_selection = parameter.find('userSelection')
            if user_selection is None or not user_selection.text:
                continue

            values_text = user_selection.text.strip()
            if not values_text:
                continue

            values = _parse_comma_separated(values_text)
            if not values:
                continue

            dep_type = _classify_dependency(method_attr, test_name)
            if dep_type is None:
                continue

            if dep_type in _LST_DEP_TYPES:
                # Context-sensitive filtering for event_properties:
                # Skip operational test types that use properties for lookups/grouping
                # rather than LST filtering (prevents false 'disjoint' statuses)
                if dep_type == 'event_properties':
                    # Extract test type name (e.g., "ReferenceSetTest" from full classname)
                    test_type = test_name.split('.')[-1] if '.' in test_name else test_name
                    if test_type in _NON_LST_FILTER_TESTS:
                        continue  # Skip: property used operationally, not for LST filtering
                
                lst_tests.append({
                    'dep_type': dep_type,
                    'values': values,
                    'negate': negate,
                })
            elif dep_type == 'rule_uuid_refs':
                bb_uuids = values

        # Build BBRefGroup if this test references building blocks
        if bb_uuids:
            mode = 'any'
            # RuleMatch_Test: parameter 1 (index 0) holds the mode selector
            if 'RuleMatch' in test_name and len(parameters) > 0:
                mode_sel = parameters[0].find('userSelection')
                if mode_sel is not None and mode_sel.text:
                    mode_text = mode_sel.text.strip().lower()
                    if mode_text in ('any', 'all'):
                        mode = mode_text
            bb_ref_groups.append({
                'uuids': bb_uuids,
                'mode': mode,
                'negate': negate,
            })

    return (lst_tests, bb_ref_groups)


# ---------------------------------------------------------------------------
#  ReferenceExtractionHandler (Phase 7)
# ---------------------------------------------------------------------------

class ReferenceExtractionHandler(BaseHandler):
    """
    Parse decoded rule XML and extract all dependencies (Phase 7).

    Input (from context):
        context.decoded_rules - Path to decoded_rules.xml (from Phase 6)
        context.temp_dir      - Workspace folder path
        context.error_counter - Shared ErrorCounter instance

    Output (to context):
        context.rule_references - Path to rule_references.json

    Files produced:
        {temp_dir}/rule_references.json

    Failure mode: CRITICAL if decoded_rules.xml missing or zero rules;
                  NON-CRITICAL for individual rule skip/error (ErrorCounter).
    """
    __slots__ = ()
    
    def execute(self, context):
        context.require('decoded_rules', 'temp_dir')
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        logger.info('Reference Extraction: Starting')
        
        # === Validate Input ===
        decoded_rules_path = context.decoded_rules
        if not os.path.exists(decoded_rules_path):
            raise CriticalPhaseError(
                'Reference Extraction',
                'decoded_rules.xml not found at {0}'.format(decoded_rules_path)
            )
        
        # === Initialize State ===
        results = {}  # UUID → rule_record
        
        total_rules = 0
        rules_with_deps = 0
        skipped_no_uuid = 0
        skipped_no_rule = 0
        enabled_count = 0
        disabled_count = 0
        building_block_count = 0
        custom_rule_count = 0
        
        # === Parse XML ===
        try:
            tree = _safe_parse_xml(decoded_rules_path)
            root = tree.getroot()
        except (ET.ParseError, IOError) as e:
            raise CriticalPhaseError(
                'Reference Extraction',
                'Failed to parse decoded_rules.xml: {0}'.format(e)
            )
        
        # === Load Known Custom Property Names ===
        known_property_names = set()
        data_dir = context.cache_dir or context.temp_dir
        props_path = os.path.join(data_dir, 'regex_properties.json')
        if os.path.exists(props_path):
            try:
                with io.open(props_path, 'r', encoding='utf-8') as f:
                    props_data = json.load(f)
                for prop in props_data:
                    pname = prop.get('name', '')
                    if pname:
                        known_property_names.add(pname)
                logger.debug(
                    'Loaded {0} custom property names for ArielFilter '
                    'key validation'.format(len(known_property_names))
                )
            except (ValueError, IOError) as e:
                logger.debug(
                    'Could not load regex_properties.json for ArielFilter '
                    'key validation: {0}'.format(e)
                )
        
        # === Process Each Rule ===
        for custom_rule in root.findall('custom_rule'):
            total_rules += 1
            
            # --- Extract Metadata ---
            rule_id = custom_rule.get('id', '')
            uuid = custom_rule.get('uuid')
            origin = custom_rule.get('origin', '')
            
            # Validate UUID
            if not uuid:
                msg_id = 'ID={0}'.format(rule_id) if rule_id else 'position={0}'.format(total_rules)
                logger.warning(
                    'Skipped rule (no UUID): {0}'.format(msg_id)
                )
                skipped_no_uuid += 1
                if context.error_counter:
                    context.error_counter.increment(
                        'Reference Extraction',
                        'Skipped rule: no UUID'
                    )
                continue  # Skip this rule
            
            # Find <rule> element
            rule_elem = custom_rule.find('rule')
            if rule_elem is None:
                logger.warning(
                    'Skipped rule (no <rule>): UUID={0}'.format(uuid)
                )
                skipped_no_rule += 1
                if context.error_counter:
                    context.error_counter.increment(
                        'Reference Extraction',
                        'Skipped rule: no <rule> element'
                    )
                continue  # Skip this rule
            
            # Extract rule attributes
            building_block_attr = rule_elem.get('buildingBlock', 'false')
            enabled_attr = rule_elem.get('enabled', 'true')
            
            building_block = (building_block_attr.lower() == 'true')
            enabled = (enabled_attr.lower() == 'true')
            
            # Extract name
            name_elem = rule_elem.find('name')
            name = (name_elem.text.strip()
                    if (name_elem is not None and name_elem.text)
                    else '')
            
            # Update counters
            if enabled:
                enabled_count += 1
            else:
                disabled_count += 1
            
            if building_block:
                building_block_count += 1
            else:
                custom_rule_count += 1
            
            # --- Initialize Dependency Sets ---
            rule_uuid_refs = set()
            reference_sets = set()
            reference_map_of_sets = set()
            reference_maps = set()
            qids = set()
            device_ids = set()
            device_type_ids = set()
            event_categories = set()
            event_properties = set()
            device_group_ids = set()
            ariel_lst_entries = []
            cre_event_list = []
            
            # --- Extract Dependencies ---
            test_definitions = rule_elem.find('testDefinitions')
            if test_definitions is not None:
                for test in test_definitions.findall('test'):
                    test_name = test.get('name', '')
                    
                    for parameter in test.findall('parameter'):
                        # Get method attribute
                        user_options = parameter.find('userOptions')
                        method_attr = (user_options.get('method', '')
                                       if user_options is not None
                                       else '')
                        
                        # ArielFilter detection
                        source_attr = (user_options.get('source', '')
                                       if user_options is not None
                                       else '')
                        if source_attr == 'arielFilter':
                            user_selection = parameter.find('userSelection')
                            sel_text = ''
                            if user_selection is not None and user_selection.text:
                                sel_text = user_selection.text
                            af_deps, af_lst, af_cre = _parse_ariel_filter(
                                sel_text, known_property_names,
                                rule_uuid=uuid)
                            # Merge deps into union sets
                            for dep_t, vals in af_deps.items():
                                if dep_t == 'device_ids':
                                    device_ids.update(vals)
                                elif dep_t == 'device_type_ids':
                                    device_type_ids.update(vals)
                                elif dep_t == 'device_group_ids':
                                    device_group_ids.update(vals)
                                elif dep_t == 'qids':
                                    qids.update(vals)
                                elif dep_t == 'event_categories':
                                    event_categories.update(vals)
                                elif dep_t == 'event_properties':
                                    event_properties.update(vals)
                            ariel_lst_entries.extend(af_lst)
                            cre_event_list.extend(af_cre)
                            continue
                        
                        # Get values
                        user_selection = parameter.find('userSelection')
                        if user_selection is None or not user_selection.text:
                            continue  # Silently skip empty userSelection
                        
                        values_text = user_selection.text.strip()
                        if not values_text:
                            continue  # Silently skip whitespace-only
                        
                        # Parse comma-separated values
                        values = _parse_comma_separated(values_text)
                        if not values:
                            continue  # Empty list after parsing
                        
                        # Classify dependency type
                        dep_type = _classify_dependency(method_attr, test_name)
                        if dep_type is None:
                            continue  # Silently skip unrecognized (forward compatibility)
                        
                        # Add to appropriate set
                        if dep_type == 'rule_uuid_refs':
                            rule_uuid_refs.update(values)
                        elif dep_type == 'reference_sets':
                            reference_sets.update(values)
                        elif dep_type == 'reference_map_of_sets':
                            reference_map_of_sets.update(values)
                        elif dep_type == 'reference_maps':
                            reference_maps.update(values)
                        elif dep_type == 'qids':
                            qids.update(values)
                        elif dep_type == 'device_ids':
                            device_ids.update(values)
                        elif dep_type == 'device_type_ids':
                            device_type_ids.update(values)
                        elif dep_type == 'event_categories':
                            event_categories.update(values)
                        elif dep_type == 'event_properties':
                            event_properties.update(values)
                        elif dep_type == 'device_group_ids':
                            device_group_ids.update(values)
            
            # --- Extract Structured LST Data ---
            lst_tests = []
            bb_ref_groups = []
            if test_definitions is not None:
                lst_tests, bb_ref_groups = _extract_lst_tests(
                    test_definitions)
            # Append ArielFilter-sourced LST entries
            lst_tests.extend(ariel_lst_entries)
            
            # --- Convert Sets to Sorted Lists ---
            rule_record = {
                'id': rule_id,
                'uuid': uuid,
                'name': name,
                'origin': origin,
                'buildingBlock': building_block,
                'enabled': enabled,
                'rule_uuid_refs': sorted(list(rule_uuid_refs)),
                'reference_sets': sorted(list(reference_sets)),
                'reference_map_of_sets': sorted(list(reference_map_of_sets)),
                'reference_maps': sorted(list(reference_maps)),
                'qids': sorted(list(qids)),
                'device_ids': sorted(list(device_ids)),
                'device_type_ids': sorted(list(device_type_ids)),
                'event_categories': sorted(list(event_categories)),
                'event_properties': sorted(list(event_properties)),
                'device_group_ids': sorted(list(device_group_ids)),
                'lst_tests': lst_tests,
                'bb_ref_groups': bb_ref_groups,
                'cre_event_list': cre_event_list,
            }
            
            # Check if rule has dependencies
            has_deps = any(len(arr) > 0 for arr in [
                rule_record['rule_uuid_refs'],
                rule_record['reference_sets'],
                rule_record['reference_map_of_sets'],
                rule_record['reference_maps'],
                rule_record['qids'],
                rule_record['device_ids'],
                rule_record['device_type_ids'],
                rule_record['event_categories'],
                rule_record['event_properties'],
                rule_record['device_group_ids'],
            ])
            if has_deps:
                rules_with_deps += 1
            
            # --- Store Result ---
            results[uuid] = rule_record
        
        # === Validate Output ===
        if total_rules == 0 or len(results) == 0:
            raise CriticalPhaseError(
                'Reference Extraction',
                'Zero rules extracted (total_rules={0}, results={1})'.format(
                    total_rules, len(results)
                )
            )
        
        # === Write JSON Output ===
        output_path = os.path.join(context.temp_dir, 'rule_references.json')
        
        try:
            with io.open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, sort_keys=True, ensure_ascii=False)
        except IOError as e:
            raise CriticalPhaseError(
                'Reference Extraction',
                'Failed to write rule_references.json: {0}'.format(e)
            )
        
        # === Update Context ===
        context.rule_references = output_path
        
        # === Log Completion Summary ===
        elapsed = time.time() - start_time
        
        logger.info('Reference extraction complete')
        logger.debug('  Total rules parsed: {0}'.format(total_rules))
        logger.debug('  Rules with dependencies: {0}'.format(rules_with_deps))
        logger.debug('  Rules skipped (no UUID): {0}'.format(skipped_no_uuid))
        logger.debug('  Rules skipped (no <rule>): {0}'.format(skipped_no_rule))
        logger.debug('  Enabled rules: {0} | Disabled rules: {1}'.format(
            enabled_count, disabled_count
        ))
        logger.debug('  Building blocks: {0} | Custom rules: {1}'.format(
            building_block_count, custom_rule_count
        ))
        logger.debug('  Elapsed time: {0:.1f}s'.format(elapsed))
        logger.debug('  Output: {0}'.format(output_path))


# ---------------------------------------------------------------------------
#  DependencyExpansionHandler (Phase 8)
# ---------------------------------------------------------------------------


def _resolve_cre_event_list(rule_dict):
    """Resolve cre_event_list numeric IDs to UUIDs and merge into rule refs.

    Args:
        rule_dict: {uuid: rule_record} — mutated in place.

    Returns:
        tuple: (resolved_count, unresolved_count) for summary logging.
    """
    logger = logging.getLogger(__name__)
    id_to_uuid = {}
    for uuid, r in rule_dict.items():
        rid = r.get('id', '')
        if rid:
            id_to_uuid[rid] = uuid

    resolved_count = 0
    unresolved_count = 0

    for uuid, rule in rule_dict.items():
        cre_entries = rule.get('cre_event_list', [])
        if not cre_entries:
            continue
        for entry in cre_entries:
            target_id = entry.get('id', '')
            is_negate = entry.get('negate', False)
            target_uuid = id_to_uuid.get(target_id)
            if target_uuid:
                if target_uuid not in rule['rule_uuid_refs']:
                    rule['rule_uuid_refs'].append(target_uuid)
                rule['bb_ref_groups'].append({
                    'uuids': [target_uuid],
                    'mode': 'any',
                    'negate': is_negate,
                })
                resolved_count += 1
            else:
                logger.warning(
                    'CRE event list: unresolved ID {0} in rule '
                    '{1!r}'.format(target_id, rule.get('name', uuid))
                )
                unresolved_count += 1

    return (resolved_count, unresolved_count)


# Dependency types extracted from rule XML parameters by _classify_dependency()
DEPENDENCY_TYPES = [
    'rule_uuid_refs',
    'reference_sets',
    'reference_map_of_sets',
    'reference_maps',
    'qids',
    'device_ids',
    'device_type_ids',
    'event_categories',
    'event_properties',
    'device_group_ids',
]


class DependencyExpansionHandler(BaseHandler):
    """
    Expand rule dependencies into resolved inventories (Phase 8).

    Input (from context):
        context.rule_references - Path to rule_references.json (Phase 7)
        context.temp_dir        - Workspace folder with reference data (Phase 3)
        context.error_counter   - Shared ErrorCounter instance

    Output (to context):
        context.expanded_rules  - Path to expanded_dependencies.json

    Files produced:
        {temp_dir}/expanded_dependencies.json

    Failure mode: CRITICAL if rule_references.json missing or unparseable,
                  or output write failure.
                  NON-CRITICAL for missing reference data files.
    """
    __slots__ = ()

    def execute(self, context):
        """Execute Phase 8: Dependency Expansion."""
        logger = logging.getLogger(__name__)
        logger.info('Dependency Expansion starting')
        start_time = time.time()

        # 1. Validate inputs
        context.require('rule_references', 'temp_dir')

        # 2. Load input data
        rule_dict = self._load_rule_references(context.rule_references)

        # 2a. Resolve cre_event_list numeric IDs to UUIDs
        cre_resolved, cre_unresolved = _resolve_cre_event_list(rule_dict)
        if cre_resolved or cre_unresolved:
            logger.debug(
                'CRE event list resolution: {0} resolved, '
                '{1} unresolved'.format(cre_resolved, cre_unresolved)
            )

        # 3. Build lookup tables
        # Reference data files live in cache_dir (offline) or temp_dir (API)
        data_dir = context.cache_dir or context.temp_dir
        lookups = self._build_all_lookups(data_dir)

        # 4. Process each rule
        results = {}
        rules_count = 0
        bb_count = 0

        for uuid, rule in rule_dict.items():
            # 4a. Resolve building block chain
            chain_uuids = self._resolve_building_block_chain(uuid, rule_dict)

            # 4b. Aggregate dependencies
            aggregated = self._aggregate_dependencies(rule, chain_uuids,
                                                      rule_dict)

            # 4c. Build expanded rule
            expanded_rule = self._build_expanded_rule(
                rule, aggregated, chain_uuids, rule_dict, lookups
            )

            results[uuid] = expanded_rule

            if not rule.get('buildingBlock', False):
                rules_count += 1
            bb_count += len(chain_uuids)

        # 5. Write output
        output_path = os.path.join(context.temp_dir,
                                   'expanded_dependencies.json')
        self._write_output(results, output_path)
        context.expanded_rules = output_path

        # 6. Log completion summary
        elapsed = time.time() - start_time
        logger.info('Dependency expansion complete')
        logger.debug('  Total items: {0}'.format(len(results)))
        logger.debug('  Custom rules: {0}'.format(rules_count))
        logger.debug('  Building blocks referenced: {0}'.format(
            bb_count
        ))
        logger.debug('  Elapsed time: {0:.1f}s'.format(elapsed))
        logger.debug('  Output: {0}'.format(output_path))

    def _load_rule_references(self, filepath):
        """Load rule references from Phase 7 output.

        Args:
            filepath: Absolute path to rule_references.json.

        Returns:
            dict: UUID-keyed rule dictionary.

        Raises:
            RuntimeError: If file missing, unparseable, or not a dict.
        """
        logger = logging.getLogger(__name__)

        if not os.path.exists(filepath):
            raise RuntimeError('Input file missing: {0}'.format(filepath))

        try:
            with io.open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise RuntimeError(
                    'Expected dictionary, got {0}'.format(type(data).__name__)
                )

            logger.debug(
                'Loaded {0} items from rule_references.json'.format(
                    len(data)
                )
            )
            return data

        except (ValueError, IOError) as e:
            raise RuntimeError(
                'Failed to parse {0}: {1}'.format(filepath, e)
            )

    def _build_regex_properties_lookup(self, data_dir):
        """Build name.lower() -> record lookup from regex_properties.json.

        Args:
            data_dir: Path to workspace directory with reference files.

        Returns:
            dict: {name_lower: record_dict} mapping. Empty dict if
                  file is missing or unparseable.
        """
        logger = logging.getLogger(__name__)
        filepath = os.path.join(data_dir, 'regex_properties.json')

        if not os.path.exists(filepath):
            logger.warning(
                'regex_properties.json not found in {0}'.format(data_dir)
            )
            return {}

        try:
            with io.open(filepath, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except (ValueError, IOError) as e:
            logger.warning(
                'Failed to parse regex_properties.json: {0}'.format(e)
            )
            return {}

        lookup = {}
        for record in records:
            name = record.get('name', '')
            key = name.lower()
            if key in lookup:
                logger.warning(
                    'Duplicate regex property name: {0}'.format(name)
                )
            lookup[key] = record

        logger.debug(
            'Built regex_properties lookup with {0} entries'.format(
                len(lookup)
            )
        )
        return lookup

    def _build_all_lookups(self, temp_dir):
        """Build all lookup tables from reference data.

        Args:
            temp_dir: Path to workspace directory with reference files.

        Returns:
            dict: Lookup tables keyed by name.
        """
        logger = logging.getLogger(__name__)
        logger.debug('Building lookup tables from reference data')

        lookups = {}

        # Direct lookups (6 tables)
        lookups['reference_sets'] = self._build_lookup_table(
            os.path.join(temp_dir, 'reference_sets.json'),
            'collection_id', 'name'
        )
        lookups['reference_maps'] = self._build_lookup_table(
            os.path.join(temp_dir, 'reference_maps.json'),
            'collection_id', 'name'
        )
        lookups['reference_map_of_sets'] = self._build_lookup_table(
            os.path.join(temp_dir, 'reference_map_of_sets.json'),
            'collection_id', 'name'
        )
        lookups['qids'] = self._build_lookup_table(
            os.path.join(temp_dir, 'qid_records.json'), 'qid', 'name'
        )
        lookups['log_source_types'] = self._build_lookup_table(
            os.path.join(temp_dir, 'log_source_types.json'), 'id', 'name'
        )
        lookups['high_level_categories'] = self._build_lookup_table(
            os.path.join(temp_dir, 'high_level_categories.json'), 'id', 'name'
        )

        # Special lookups
        lookups['categories'] = self._build_category_lookup(
            os.path.join(temp_dir, 'high_level_categories.json'),
            os.path.join(temp_dir, 'low_level_categories.json')
        )

        lookups['log_sources_device'], lookups['log_sources_type'] = \
            self._build_log_sources_lookups(
                os.path.join(temp_dir, 'log_sources.json')
            )

        lookups['rule_groups'] = self._build_rule_groups_lookup(
            os.path.join(temp_dir, 'rule_groups.json')
        )

        lookups['regex_properties'] = \
            self._build_regex_properties_lookup(temp_dir)

        lookups['log_source_groups'] = self._build_lookup_table(
            os.path.join(temp_dir, 'log_source_groups.json'), 'id', 'name'
        )

        logger.debug('Built {0} lookup tables'.format(len(lookups)))
        return lookups

    def _build_lookup_table(self, filepath, id_field, name_field):
        """Build ID-to-name lookup from a JSON array of records.

        Args:
            filepath: Path to JSON file containing array of records.
            id_field: Key name for the ID field (e.g., 'qid', 'id').
            name_field: Key name for the name field (e.g., 'name').

        Returns:
            dict: {id_string: name_string} mapping. Empty dict if
                  file is missing or unparseable.
        """
        logger = logging.getLogger(__name__)

        if not os.path.exists(filepath):
            logger.warning(
                'Missing reference file: {0}'.format(filepath)
            )
            return {}

        file_size = os.path.getsize(filepath)
        lookup = {}

        # Streaming threshold: 50MB
        if file_size > 50 * 1024 * 1024:
            logger.debug(
                'Streaming large file: {0} ({1:.1f} MB)'.format(
                    filepath, file_size / (1024.0 * 1024.0)
                )
            )

            try:
                for item in iter_json_array(filepath):
                    try:
                        lookup[str(item[id_field])] = item[name_field]
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed record in %s', filepath)
                        continue
            except IOError as e:
                logger.warning(
                    'Failed to stream {0}: {1}'.format(filepath, e)
                )
                return {}
        else:
            # Standard parse (entire file)
            try:
                with io.open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if not isinstance(data, list):
                    logger.warning(
                        'Expected array in {0}, got {1}'.format(
                            filepath, type(data).__name__
                        )
                    )
                    return {}

                for item in data:
                    try:
                        lookup[str(item[id_field])] = item[name_field]
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed record in %s', filepath)
                        continue

            except (ValueError, IOError) as e:
                logger.warning(
                    'Failed to parse {0}: {1}'.format(filepath, e)
                )
                return {}

        logger.debug('Built lookup: {0} with {1} entries'.format(
            os.path.basename(filepath), len(lookup)
        ))
        return lookup

    def _build_category_lookup(self, high_cats_file, low_cats_file):
        """Build hierarchical event category lookup.

        Produces 'HighLevel.LowLevel' format for categories that have
        both levels, standalone name otherwise.

        Args:
            high_cats_file: Path to high_level_categories.json.
            low_cats_file: Path to low_level_categories.json.

        Returns:
            dict: {category_id: 'HighLevel.LowLevel' or 'HighLevel'}.
        """
        logger = logging.getLogger(__name__)

        # Load high-level categories
        high_lookup = self._build_lookup_table(high_cats_file, 'id', 'name')

        categories = {}

        # Load low-level categories
        try:
            with io.open(low_cats_file, 'r', encoding='utf-8') as f:
                low_cats = json.load(f)

            for low_cat in low_cats:
                try:
                    cat_id = str(low_cat['id'])
                    high_id = str(low_cat.get('high_level_category_id', ''))
                    low_name = low_cat['name']
                except (KeyError, TypeError):
                    logger.debug('Skipped malformed low-level category record')
                    continue

                if high_id in high_lookup:
                    categories[cat_id] = '{0}.{1}'.format(
                        high_lookup[high_id], low_name
                    )
                else:
                    categories[cat_id] = low_name

        except (IOError, ValueError) as e:
            logger.warning(
                'Failed to parse low-level categories: {0}'.format(e)
            )

        # Add standalone high-level categories
        categories.update(high_lookup)

        return categories

    def _build_log_sources_lookups(self, log_sources_file):
        """Build device name and device-to-type lookups from log_sources.json.

        Args:
            log_sources_file: Path to log_sources.json.

        Returns:
            tuple: (device_lookup, type_lookup)
                - device_lookup: {device_id: name}
                - type_lookup: {device_id: type_id}
        """
        logger = logging.getLogger(__name__)
        device_lookup = {}
        type_lookup = {}

        if not os.path.exists(log_sources_file):
            logger.warning('Missing log_sources.json')
            return device_lookup, type_lookup

        try:
            with io.open(log_sources_file, 'r', encoding='utf-8') as f:
                log_sources = json.load(f)

            for source in log_sources:
                try:
                    device_id = str(source['id'])
                    device_lookup[device_id] = source['name']
                    type_lookup[device_id] = source['type_id']
                except (KeyError, TypeError):
                    logger.debug('Skipped malformed log source record')
                    continue

        except (IOError, ValueError) as e:
            logger.warning(
                'Failed to parse log_sources.json: {0}'.format(e)
            )

        return device_lookup, type_lookup

    def _build_rule_groups_lookup(self, rule_groups_file):
        """Build inverted rule groups lookup (rule_id to group names).

        Args:
            rule_groups_file: Path to rule_groups.json.

        Returns:
            dict: {rule_id: [group_name_1, group_name_2, ...]} sorted names.
        """
        logger = logging.getLogger(__name__)
        groups_by_rule = defaultdict(list)

        if not os.path.exists(rule_groups_file):
            logger.warning('Missing rule_groups.json')
            return dict(groups_by_rule)

        try:
            with io.open(rule_groups_file, 'r', encoding='utf-8') as f:
                groups = json.load(f)

            for group in groups:
                try:
                    group_name = group['name']
                    for rule_id in group.get('child_items', []):
                        groups_by_rule[str(rule_id)].append(group_name)
                except (KeyError, TypeError):
                    logger.debug('Skipped malformed rule group record')
                    continue

        except (IOError, ValueError) as e:
            logger.warning(
                'Failed to parse rule_groups.json: {0}'.format(e)
            )

        # Sort group names for deterministic output
        for rule_id in groups_by_rule:
            groups_by_rule[rule_id] = sorted(groups_by_rule[rule_id])

        return dict(groups_by_rule)

    def _resolve_building_block_chain(self, rule_uuid, rule_dict,
                                      visited=None):
        """Resolve building block dependency chain recursively.

        Exclude disabled building blocks and their descendants.

        Args:
            rule_uuid: UUID of the rule to resolve.
            rule_dict: Full {uuid: rule_record} dictionary.
            visited: Set of already-visited UUIDs (cycle prevention).

        Returns:
            list: Flattened list of BB UUIDs in dependency chain.
        """
        logger = logging.getLogger(__name__)

        if visited is None:
            visited = set()

        # Cycle detection
        if rule_uuid in visited:
            return []

        # Missing UUID
        if rule_uuid not in rule_dict:
            logger.debug(
                'UUID not found in dictionary: {0}'.format(
                    rule_uuid
                )
            )
            return []

        visited.add(rule_uuid)
        rule = rule_dict[rule_uuid]

        # Exclude disabled building blocks
        if not rule.get('enabled', True):
            logger.debug(
                'Disabled BB excluded: {0}'.format(
                    rule.get('name', rule_uuid)
                )
            )
            return []

        chain = []
        for ref_uuid in rule.get('rule_uuid_refs', []):
            if ref_uuid not in visited:
                chain.append(ref_uuid)
                child_chain = self._resolve_building_block_chain(
                    ref_uuid, rule_dict, visited
                )
                chain.extend(child_chain)

        return chain

    def _aggregate_dependencies(self, rule, chain_uuids, rule_dict):
        """Aggregate dependencies from rule and all BBs in resolved chain.

        Args:
            rule: Top-level rule record dict.
            chain_uuids: List of BB UUIDs in resolved chain.
            rule_dict: Full {uuid: rule_record} dictionary.

        Returns:
            dict: {dep_type: set_of_ids} for each DEPENDENCY_TYPES entry.
        """
        aggregated = {dep_type: set() for dep_type in DEPENDENCY_TYPES}

        # Aggregate from each BB in chain
        for bb_uuid in chain_uuids:
            if bb_uuid not in rule_dict:
                continue
            bb = rule_dict[bb_uuid]
            for dep_type in DEPENDENCY_TYPES:
                aggregated[dep_type].update(bb.get(dep_type, []))

        # Merge rule's own dependencies
        for dep_type in DEPENDENCY_TYPES:
            aggregated[dep_type].update(rule.get(dep_type, []))

        return aggregated

    def _build_expanded_rule(self, rule, aggregated, chain_uuids,
                             rule_dict, lookups):
        """Build expanded rule object with human-readable dependency names.

        Args:
            rule: Original rule record dict.
            aggregated: {dep_type: set_of_ids} from aggregation.
            chain_uuids: BB UUIDs in resolved chain.
            rule_dict: Full {uuid: rule_record} dictionary.
            lookups: Dict of lookup tables (keyed by reference-data type).

        Returns:
            dict: Expanded rule object.
        """
        expanded = {}

        # Metadata (6 fields - pass-through)
        expanded['id'] = rule['id']
        expanded['uuid'] = rule['uuid']
        expanded['name'] = rule['name']
        expanded['origin'] = rule['origin']
        expanded['buildingBlock'] = rule['buildingBlock']
        expanded['enabled'] = rule['enabled']

        # Enrichment (1 field - rule groups)
        expanded['rule_groups'] = lookups['rule_groups'].get(
            rule['id'], []
        )

        # Per-rule LST data — passed through without aggregation
        expanded['lst_tests'] = rule.get('lst_tests', [])
        expanded['bb_ref_groups'] = rule.get('bb_ref_groups', [])

        # Expanded dependencies — unpaired arrays (sorted alphabetically)
        expanded['rule_references'] = self._resolve_bb_references(
            chain_uuids, rule_dict
        )
        expanded['expanded_reference_sets'] = self._resolve_ids_to_names(
            aggregated['reference_sets'], lookups['reference_sets'],
            'reference set'
        )
        expanded['expanded_reference_map_of_sets'] = \
            self._resolve_ids_to_names(
                aggregated['reference_map_of_sets'],
                lookups['reference_map_of_sets'], 'map of sets'
            )
        expanded['expanded_reference_maps'] = self._resolve_ids_to_names(
            aggregated['reference_maps'], lookups['reference_maps'],
            'reference map'
        )
        expanded['expanded_device_ids'] = self._resolve_ids_to_names(
            aggregated['device_ids'], lookups['log_sources_device'], 'device'
        )
        expanded['expanded_device_group_ids'] = self._resolve_ids_to_names(
            aggregated['device_group_ids'], lookups['log_source_groups'],
            'log source group'
        )
        expanded['device_group_ids'] = sorted(list(aggregated['device_group_ids']))

        # Expanded dependencies — paired arrays (sorted by numeric ID)
        qid_ids, expanded_qids = self._resolve_paired_ids_to_names(
            aggregated['qids'], lookups['qids'], 'QID'
        )
        expanded['expanded_qids'] = expanded_qids
        expanded['qid_ids'] = qid_ids

        cat_ids, expanded_cats = self._resolve_paired_ids_to_names(
            aggregated['event_categories'], lookups['categories'],
            'event category'
        )
        expanded['expanded_event_categories'] = expanded_cats
        expanded['event_category_ids'] = cat_ids

        # Device types (direct + inferred from device_ids) — paired
        device_type_id_ids, expanded_device_types = \
            self._resolve_device_types(
                aggregated['device_type_ids'],
                aggregated['device_ids'],
                lookups['log_sources_type'],
                lookups['log_source_types']
            )
        expanded['expanded_device_type_ids'] = expanded_device_types
        expanded['device_type_id_ids'] = device_type_id_ids

        # Custom property classification (event_properties)
        regex_props = lookups.get('regex_properties', {})
        all_props = aggregated.get('event_properties', set())
        custom_properties = []
        for prop_name in all_props:
            if prop_name.lower() in regex_props:
                custom_properties.append(prop_name)
        expanded['expanded_custom_properties'] = sorted(custom_properties)

        return expanded

    def _resolve_bb_references(self, chain_uuids, rule_dict):
        """Resolve BB UUIDs to formatted names with 'BB: ' prefix.

        Args:
            chain_uuids: List of BB UUIDs in resolved chain.
            rule_dict: Full {uuid: rule_record} dictionary.

        Returns:
            list: Alphabetically sorted BB names with 'BB: ' prefix.
        """
        bb_names = []

        for bb_uuid in chain_uuids:
            if bb_uuid in rule_dict:
                name = rule_dict[bb_uuid].get('name', bb_uuid)
                bb_names.append('BB: {0}'.format(name))
            else:
                bb_names.append('BB: UNRESOLVED: {0}'.format(bb_uuid))

        return sorted(bb_names)

    def _resolve_ids_to_names(self, id_set, lookup_table, id_type):
        """Resolve IDs to names for unpaired arrays (alphabetical sort).

        IDs not found in the lookup are marked as 'UNRESOLVED: {id}'.
        Unresolved count is logged at debug level.

        Args:
            id_set: Set of ID integers/strings.
            lookup_table: {id: name} lookup dict.
            id_type: Type name for logging (e.g., 'reference set').

        Returns:
            list: Alphabetically sorted name strings.
        """
        logger = logging.getLogger(__name__)
        names = []
        unresolved_count = 0

        for id_val in id_set:
            id_str = str(id_val)
            name = lookup_table.get(id_str)

            if name:
                names.append(name)
            else:
                names.append('UNRESOLVED: {0}'.format(id_str))
                unresolved_count += 1

        if unresolved_count > 0:
            logger.debug('{0} unresolved {1}(s)'.format(
                unresolved_count, id_type
            ))

        return sorted(names)

    def _resolve_paired_ids_to_names(self, id_set, lookup_table, id_type):
        """Resolve IDs to names for paired arrays (sorted by numeric ID).

        Returns parallel arrays sorted by numeric ID value,
        preserving 1:1 alignment between IDs and names.

        Args:
            id_set: Set of ID integers/strings.
            lookup_table: {id: name} lookup dict.
            id_type: Type name for logging (e.g., 'QID').

        Returns:
            tuple: (sorted_id_strings, sorted_names) in parallel.
        """
        logger = logging.getLogger(__name__)
        pairs = []
        unresolved_count = 0

        for id_val in id_set:
            id_str = str(id_val)
            name = lookup_table.get(id_str)

            if name:
                pairs.append((id_str, name))
            else:
                pairs.append((id_str, 'UNRESOLVED: {0}'.format(id_str)))
                unresolved_count += 1

        if unresolved_count > 0:
            logger.debug('{0} unresolved {1}(s)'.format(
                unresolved_count, id_type
            ))

        # Sort by numeric ID value
        pairs.sort(key=lambda p: (0, int(p[0])) if p[0].isdigit() else (1, p[0]))

        sorted_ids = [p[0] for p in pairs]
        sorted_names = [p[1] for p in pairs]

        return sorted_ids, sorted_names

    def _resolve_device_types(self, device_type_ids, device_ids,
                              log_sources_type_lookup,
                              log_source_types_lookup):
        """Resolve device types from direct IDs plus inferred from devices.

        Args:
            device_type_ids: Set of direct device type IDs.
            device_ids: Set of device (log source) IDs.
            log_sources_type_lookup: {device_id: type_id} mapping.
            log_source_types_lookup: {type_id: type_name} mapping.

        Returns:
            tuple: (sorted_type_id_strings, sorted_type_names) in parallel,
                   sorted by numeric type ID.
        """
        type_pairs = {}  # {type_id_str: type_name} — deduplicated

        # Direct device_type_ids
        for type_id in device_type_ids:
            type_id_str = str(type_id)
            type_name = log_source_types_lookup.get(type_id_str)
            if type_name:
                type_pairs[type_id_str] = type_name
            else:
                type_pairs[type_id_str] = 'UNRESOLVED: {0}'.format(type_id)

        # Inferred from device_ids (two-step)
        for device_id in device_ids:
            device_id_str = str(device_id)

            # Step 1: device_id -> type_id
            type_id = log_sources_type_lookup.get(device_id_str)
            if not type_id:
                continue

            # Step 2: type_id -> type_name (if not already resolved)
            type_id_str = str(type_id)
            if type_id_str not in type_pairs:
                type_name = log_source_types_lookup.get(type_id_str)
                if type_name:
                    type_pairs[type_id_str] = type_name

        # Sort by numeric type ID
        sorted_items = sorted(
            type_pairs.items(),
            key=lambda p: (0, int(p[0])) if p[0].isdigit() else (1, p[0])
        )

        sorted_ids = [item[0] for item in sorted_items]
        sorted_names = [item[1] for item in sorted_items]

        return sorted_ids, sorted_names

    def _write_output(self, results_dict, output_path):
        """Write results as deterministic UUID-sorted JSON array.

        Args:
            results_dict: {uuid: expanded_rule_object} dictionary.
            output_path: Path to expanded_dependencies.json.

        Raises:
            RuntimeError: If file write fails.
        """
        logger = logging.getLogger(__name__)

        # Sort by UUID (deterministic)
        sorted_items = sorted(results_dict.items(), key=lambda item: item[0])
        output_array = [rule_obj for uuid, rule_obj in sorted_items]

        try:
            with io.open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    output_array,
                    f,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False
                )

            logger.debug('Wrote {0} items to {1}'.format(
                len(output_array), output_path
            ))

        except IOError as e:
            raise RuntimeError('Failed to write output: {0}'.format(e))


# ---------------------------------------------------------------------------
#  UCM CSV Extension — Formatting Helpers (Phase 9)
# ---------------------------------------------------------------------------

def format_bracket_list(items):
    """Format a pre-sorted list as '[item1, item2, ...]' or '[]'.

    Args:
        items: list of str or int values, pre-sorted by the caller.

    Returns:
        str: Bracket-formatted string with comma-space separators.
    """
    if not items:
        return '[]'
    return '[{0}]'.format(', '.join(str(i) for i in items))


def format_sorted_bracket_list(items, sort_key=None):
    """Sort items and format as bracket list.

    Args:
        items: list of values to sort and format.
        sort_key: optional key function for sorting.
                  If None, uses default sorted() behaviour.

    Returns:
        str: '[sorted_item1, sorted_item2]' or '[]'.
    """
    if not items:
        return '[]'
    if sort_key is not None:
        sorted_items = sorted(items, key=sort_key)
    else:
        sorted_items = sorted(items)
    return format_bracket_list(sorted_items)


# ---------------------------------------------------------------------------
#  UCM CSV Extension — Calculator Functions (Phase 9)
# ---------------------------------------------------------------------------

def calc_log_source_types(row, context):
    """Return active log source type names matched to this rule.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context from _build_enrichment_context().

    Returns:
        str: '[Type1, Type2]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    type_ids = context.get('uuid_to_log_source_types', {}).get(uuid, set())
    if not type_ids:
        return '[]'
    type_id_to_name = context.get('type_id_to_name', {})
    names = []
    for tid in type_ids:
        name = type_id_to_name.get(str(tid), '')
        if name:
            names.append(name)
    return format_sorted_bracket_list(names)


def calc_log_source_type_status(row, context):
    """Return log source type resolution status for this rule.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context from _build_enrichment_context().

    Returns:
        str: One of 'matched', 'no_tests', 'lst_inactive', 'disjoint',
             'unknown', or '' (empty string if UUID not found).
    """
    uuid = row.get('uuid', '')
    return context.get('uuid_to_lst_status', {}).get(uuid, '')


def calc_log_source_count(row, context):
    """Return total active log source instances across matched types.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: Non-negative integer as decimal string (e.g., '3', '0').
    """
    uuid = row.get('uuid', '')
    type_ids = context.get('uuid_to_log_source_types', {}).get(uuid, set())
    if not type_ids:
        return '0'
    type_id_to_instances = context.get('type_id_to_instances', {})
    total = 0
    for tid in type_ids:
        instances = type_id_to_instances.get(str(tid), [])
        total += len(instances)
    return str(total)


def calc_reference_sets(row, context):
    """Extract reference set names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[SetName1, SetName2]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('expanded_reference_sets', [])
    return format_sorted_bracket_list(items)


def calc_map_of_sets(row, context):
    """Extract reference map-of-sets names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[MapOfSet1]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('expanded_reference_map_of_sets', [])
    return format_sorted_bracket_list(items)


def calc_reference_maps(row, context):
    """Extract reference map names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[MapName1, MapName2]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('expanded_reference_maps', [])
    return format_sorted_bracket_list(items)


def calc_qid_events(row, context):
    """Extract QID event names from expanded dependencies.

    The expanded_qids array contains resolved name strings (e.g.
    'User Login Success') already sorted by numeric QID ID in Phase 8.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[User Login Success, SSH: Auth Failure]' pre-sorted, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('expanded_qids', [])
    return format_bracket_list(items)


def calc_event_categories(row, context):
    """Extract event category names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[Authentication.Host Login Succeeded, Firewall.Deny]'
             pre-sorted by Phase 8, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('expanded_event_categories', [])
    if not items:
        return '[]'
    return format_bracket_list(items)


def calc_rule_references(row, context):
    """Extract referenced rule/building block names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[BB: Auth Failure Pattern, BB: Threshold Detector]' sorted, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    items = expanded.get('rule_references', [])
    return format_sorted_bracket_list(items)


def calc_extensions(row, context):
    """Look up extension packages providing this rule.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: JSON array string (e.g., '[{"name": "Auth Pack", "version": "1.0"}]')
             or '[]'.
    """
    uuid = row.get('uuid', '')
    ext_list = context.get('uuid_to_extensions', {}).get(uuid, [])
    if not ext_list:
        return '[]'
    return json.dumps(ext_list)


def calc_content_extension_name(row, context):
    """Name of the most recently installed extension providing this rule.

    Looks up the pre-computed uuid_to_extension_name mapping built by
    _build_uuid_to_extensions (single-pass, highest install_time wins).

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: Extension name (e.g., 'Auth Pack v2') or ''.
    """
    uuid = row.get('uuid', '')
    return context.get('uuid_to_extension_name', {}).get(uuid, '')


def calc_content_category(row, context):
    """Content category placeholder for backward compatibility.

    This column exists for backward compatibility with the SIEM Migration
    UI which expects this header. The value is always empty.

    Args:
        row: dict — CSV row (ignored).
        context: dict — enrichment context (ignored).

    Returns:
        str: Always '' (empty string).
    """
    return ''


def calc_mitre_tactics(row, context):
    """Look up MITRE ATT&CK tactic names for this rule.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[Credential Access, Initial Access]' sorted, '[]', or 'ERROR'.
    """
    if context.get('mitre_error', False):
        return 'ERROR'
    uuid = row.get('uuid', '')
    mitre = context.get('id_to_mitre', {}).get(uuid, {})
    tactics = mitre.get('tactics', [])
    return format_sorted_bracket_list(tactics)


def calc_mitre_techniques(row, context):
    """Look up MITRE ATT&CK technique IDs for this rule.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[T1078, T1110.001]' sorted alphanumerically, '[]', or 'ERROR'.
    """
    if context.get('mitre_error', False):
        return 'ERROR'
    uuid = row.get('uuid', '')
    mitre = context.get('id_to_mitre', {}).get(uuid, {})
    techniques = mitre.get('techniques', [])
    return format_sorted_bracket_list(techniques)


def calc_qradar_version(row, context):
    """Return QRadar version string (same for all rows).

    Args:
        row: dict — CSV row (ignored).
        context: dict — enrichment context.

    Returns:
        str: Version string (e.g., '7.5.0 Update Package 7') or ''.
    """
    version = context.get('qradar_version', '')
    if version is None:
        return ''
    return str(version)


def calc_custom_properties(row, context):
    """Extract custom property names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[PropA, PropB]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    props = expanded.get('expanded_custom_properties', [])
    return format_sorted_bracket_list(props)


def calc_log_source_groups(row, context):
    """Extract log source group names from expanded dependencies.

    Args:
        row: dict — CSV row with 'uuid' key.
        context: dict — enrichment context.

    Returns:
        str: '[GroupA, GroupB]' sorted alphabetically, or '[]'.
    """
    uuid = row.get('uuid', '')
    expanded = context.get('uuid_to_expanded', {}).get(uuid, {})
    groups = expanded.get('expanded_device_group_ids', [])
    return format_sorted_bracket_list(groups)


def calc_version(row, context):
    """Return the script version string for the Version column.

    Args:
        row: dict — CSV row (unused).
        context: dict — enrichment context (unused).

    Returns:
        str: VERSION constant value.
    """
    return VERSION


# Calculator function registry (parallel to CALCULATED_COLUMNS)
COLUMN_CALCULATORS = [
    {'name': 'Log Source Types', 'calculator': calc_log_source_types, 'default': '[]'},
    {'name': 'Log Source Status', 'calculator': calc_log_source_type_status, 'default': ''},
    {'name': 'Log Source Count', 'calculator': calc_log_source_count, 'default': '0'},
    {'name': 'Log Source Groups', 'calculator': calc_log_source_groups, 'default': '[]'},
    {'name': 'Reference Sets', 'calculator': calc_reference_sets, 'default': '[]'},
    {'name': 'Map of Sets', 'calculator': calc_map_of_sets, 'default': '[]'},
    {'name': 'Reference Maps', 'calculator': calc_reference_maps, 'default': '[]'},
    {'name': 'QID Events', 'calculator': calc_qid_events, 'default': '[]'},
    {'name': 'Event Categories', 'calculator': calc_event_categories, 'default': '[]'},
    {'name': 'Custom Properties', 'calculator': calc_custom_properties, 'default': '[]'},
    {'name': 'Rule References', 'calculator': calc_rule_references, 'default': '[]'},
    {'name': 'Content extension name', 'calculator': calc_content_extension_name, 'default': ''},
    {'name': 'Content category', 'calculator': calc_content_category, 'default': ''},
    {'name': 'Extensions', 'calculator': calc_extensions, 'default': '[]'},
    {'name': 'MITRE Tactics', 'calculator': calc_mitre_tactics, 'default': '[]'},
    {'name': 'MITRE Techniques', 'calculator': calc_mitre_techniques, 'default': '[]'},
    {'name': 'QRadar Version', 'calculator': calc_qradar_version, 'default': ''},
    {'name': 'Version', 'calculator': calc_version, 'default': ''},
]


def _intersect_lst_sets(sets):
    # type: (list) -> set or None
    """Intersect a list of LST constraint sets with None-as-universal semantics.

    None entries represent universal (no constraint).
    Empty set represents impossible (no matching types).
    Empty input list returns None (no constraints = universal).

    Args:
        sets: List of set-or-None entries to intersect.

    Returns:
        set or None: Intersection result.
    """
    result = None
    for s in sets:
        if s is None:
            continue
        if result is None:
            result = set(s)
        else:
            result = result & s
        if not result:
            return set()
    return result


# ---------------------------------------------------------------------------
#  UCMCSVExtensionHandler (Phase 9)
# ---------------------------------------------------------------------------

class UCMCSVExtensionHandler(BaseHandler):
    """
    Extend UCM CSV with calculated migration columns (Phase 9).

    Optionally produce a standalone active log sources inventory CSV.

    Input (from context):
        context.expanded_rules   - Path to expanded_dependencies.json (Phase 8)
        context.ucm_csv_path     - Path to UCM CSV export (Phase 1)
        context.temp_dir         - Workspace folder with reference data
        context.output_dir       - Output directory for CSV files
        context.timestamp        - Run timestamp YYYYMMDDHHMMSS
        context.active_days      - Activity window in days (int)
        context.log_sources_flag - Whether to generate log sources report (bool)
        context.error_counter    - Shared ErrorCounter instance

    Output (to context):
        context.enriched_csv     - Path to extended rules CSV
        context.log_sources_csv  - Path to log sources CSV (when generated)
    """
    __slots__ = ()

    def execute(self, context):
        """Execute Phase 9: UCM CSV Extension with Migration Enrichments."""
        logger = logging.getLogger(__name__)
        logger.info('UCM CSV Extension starting')
        start_time = time.time()

        # 1. Validate required context attributes
        context.require('expanded_rules', 'ucm_csv_path',
                        'temp_dir', 'output_dir', 'timestamp')

        # 2. Validate output directory writability
        if not os.path.isdir(context.output_dir):
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Output directory does not exist: {0}'.format(
                    context.output_dir)
            )
        test_path = os.path.join(context.output_dir, '.write_test')
        try:
            with io.open(test_path, 'w', encoding='utf-8') as f:
                f.write(text_type('test'))
            os.remove(test_path)
        except (IOError, OSError) as exc:
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Output directory not writable: {0}'.format(
                    context.output_dir),
                cause=exc
            )

        # 3. Build enrichment context
        enrichment_ctx = self._build_enrichment_context(context)

        # 4. Read UCM CSV
        rows, fieldnames = self._read_ucm_csv(context.ucm_csv_path)
        logger.info('Read {0} rows from UCM CSV'.format(len(rows)))

        # 5. Process each row through calculators
        extended_fieldnames = list(fieldnames) + list(CALCULATED_COLUMNS)
        processed_rows = []
        rules_with_sources = 0

        for idx, row in enumerate(rows):
            uuid = row.get('uuid', '')

            for calc_entry in COLUMN_CALCULATORS:
                col_name = calc_entry['name']
                calc_fn = calc_entry['calculator']
                default = calc_entry['default']
                try:
                    row[col_name] = calc_fn(row, enrichment_ctx)
                except Exception as exc:
                    logger.warning(
                        'Calculator {0} failed for row {1} '
                        '(rule {2}): {3}'.format(
                            col_name, idx + 1, uuid, exc)
                    )
                    row[col_name] = default

            # Track rules with matched log sources
            if row.get('Log Source Types', '[]') != '[]':
                rules_with_sources += 1

            # Log unmatched UUIDs at debug level
            if uuid and uuid not in enrichment_ctx.get('uuid_to_expanded', {}):
                logger.debug('Unmatched UUID in UCM CSV: {0}'.format(uuid))

            processed_rows.append(row)

            # Progress logging every 500 rows
            if (idx + 1) % 500 == 0:
                logger.info('Processed {0}/{1} rows'.format(
                    idx + 1, len(rows)))

        # 6. Write extended CSV
        output_filename = 'qradar_rules_{0}.csv'.format(context.timestamp)
        output_path = os.path.join(context.output_dir, output_filename)
        self._write_extended_csv(processed_rows, extended_fieldnames,
                                 output_path)
        context.enriched_csv = output_path
        logger.info('Extended CSV written: {0}'.format(output_path))

        # 7. Conditionally generate log sources report
        if context.log_sources_flag:
            ls_path = self._generate_log_sources_report(context,
                                                         enrichment_ctx)
            context.log_sources_csv = ls_path
            logger.info('Log sources report written: {0}'.format(ls_path))

        # 8. Log completion summary
        elapsed = time.time() - start_time
        active_type_count = len(enrichment_ctx.get('active_type_ids', set()))
        active_instance_count = sum(
            len(v) for v in enrichment_ctx.get(
                'type_id_to_instances', {}).values()
        )
        total_rules = len(processed_rows)
        pct = (100.0 * rules_with_sources / total_rules
               if total_rules > 0 else 0.0)

        logger.info('UCM CSV Extension complete')
        logger.info('  Rules processed: {0}'.format(total_rules))
        logger.info('  Active source types: {0}'.format(active_type_count))
        logger.info('  Active instances: {0}'.format(active_instance_count))
        logger.info('  Rules with sources: {0}/{1} ({2:.1f}%)'.format(
            rules_with_sources, total_rules, pct))
        logger.info('  Elapsed time: {0:.1f}s'.format(elapsed))
        logger.info('  Output: {0}'.format(output_path))

    def _build_enrichment_context(self, context):
        """Build all lookup tables and mappings once for reuse across rows.

        Args:
            context: PipelineContext instance.

        Returns:
            dict: Enrichment context with all lookup tables.

        Raises:
            CriticalPhaseError: If expanded_dependencies.json is missing
                                or unparseable.
        """
        logger = logging.getLogger(__name__)
        logger.info('Building enrichment context')

        # Load expanded dependencies (CRITICAL)
        expanded_path = context.expanded_rules
        if not os.path.exists(expanded_path):
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Missing required file: {0}'.format(expanded_path)
            )

        try:
            with io.open(expanded_path, 'r', encoding='utf-8') as f:
                expanded_data = json.load(f)
        except (ValueError, IOError) as exc:
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Failed to parse expanded dependencies',
                cause=exc
            )

        # Build uuid_to_expanded mapping
        uuid_to_expanded = {}
        if isinstance(expanded_data, list):
            for item in expanded_data:
                uuid = item.get('uuid', '')
                if uuid:
                    uuid_to_expanded[uuid] = item
        elif isinstance(expanded_data, dict):
            uuid_to_expanded = expanded_data

        logger.debug('Loaded {0} expanded rules'.format(
            len(uuid_to_expanded)))

        # Load optional reference files
        # Reference data lives in cache_dir (offline) or temp_dir (API)
        data_dir = context.cache_dir or context.temp_dir

        # Log sources
        log_sources = self._load_optional_json(
            os.path.join(data_dir, 'log_sources.json'), 'log_sources.json')

        # Log source types
        log_source_types_data = self._load_optional_json(
            os.path.join(data_dir, 'log_source_types.json'),
            'log_source_types.json')

        # QID records
        qid_records_path = os.path.join(data_dir, 'qid_records.json')

        # DSM event mappings
        dsm_mappings_path = os.path.join(data_dir, 'dsm_event_mappings.json')

        # Extensions
        extensions_data = self._load_optional_json(
            os.path.join(data_dir, 'extensions.json'), 'extensions.json')

        # MITRE mappings
        mitre_data = self._load_optional_json(
            os.path.join(data_dir, 'mitre_mappings.json'),
            'mitre_mappings.json')

        # QRadar version
        qradar_version = ''
        version_path = os.path.join(data_dir, 'qradar_version.json')
        if os.path.exists(version_path):
            try:
                with io.open(version_path, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                if isinstance(version_data, dict):
                    qradar_version = version_data.get('release_name', '')
                elif isinstance(version_data, str):
                    qradar_version = version_data
            except (ValueError, IOError) as exc:
                logger.warning(
                    'Failed to read qradar_version.json: {0}'.format(exc))
        else:
            logger.warning('Missing optional file: qradar_version.json')

        # Build active log source data
        active_days = context.active_days if context.active_days else 7
        active_type_ids, type_id_to_instances, type_id_to_name = \
            self._identify_active_log_sources(log_sources, active_days)

        # Build all_type_ids from log_source_types (all defined LSTs, not just active)
        all_type_ids = set()
        if log_source_types_data:
            for lst_item in log_source_types_data:
                tid = lst_item.get('id')
                if tid is not None:
                    all_type_ids.add(int(tid))

        # Build log source type lookup from log_source_types data
        # (for type names where we don't have active instance data)
        if log_source_types_data:
            for lst_item in log_source_types_data:
                tid = str(lst_item.get('id', ''))
                tname = lst_item.get('name', '')
                if tid and tid not in type_id_to_name:
                    type_id_to_name[tid] = tname

        # Build QID and DSM lookups for 3-pathway matching
        qid_lookup, category_lookup = self._build_qid_lookups(
            qid_records_path)
        dsm_lookup = self._build_dsm_lookup(dsm_mappings_path)

        # Build high-to-low category index for category fallback
        high_to_low_ids = self._build_high_to_low_ids(data_dir)

        # Build property-to-LST mapping for Pathway 4
        property_name_to_lst_ids = self._build_property_to_lst_mapping(
            data_dir, category_lookup, dsm_lookup, active_type_ids)

        # Load log source groups (non-critical) for Pathway 5
        log_source_groups_data = self._load_optional_json(
            os.path.join(data_dir, 'log_source_groups.json'),
            'log_source_groups.json')

        # Build group_id_to_name lookup
        group_id_to_name = {}
        if log_source_groups_data:
            for grp in log_source_groups_data:
                grp_id = grp.get('id')
                grp_name = grp.get('name', '')
                if grp_id is not None and grp_name:
                    group_id_to_name[grp_id] = grp_name

        # Build group_id_to_group lookup (full records for hierarchy traversal)
        group_id_to_group = {}
        if log_source_groups_data:
            for grp in log_source_groups_data:
                grp_id = grp.get('id')
                if grp_id is not None:
                    group_id_to_group[grp_id] = grp

        # Build UUID to log source types mapping (5-pathway)
        lst_status = {}
        uuid_to_log_source_types = self._build_uuid_to_log_source_types(
            uuid_to_expanded, qid_lookup, category_lookup,
            dsm_lookup, active_type_ids,
            property_name_to_lst_ids=property_name_to_lst_ids,
            log_sources=log_sources,
            group_map=group_id_to_group,
            high_to_low_ids=high_to_low_ids,
            lst_status_out=lst_status,
            all_type_ids=all_type_ids)

        # Build extension mapping
        uuid_to_extensions, uuid_to_extension_name = \
            self._build_uuid_to_extensions(extensions_data)

        # Build MITRE lookup
        id_to_mitre, mitre_error = self._build_mitre_lookup(mitre_data)

        # Build extension_by_id for log sources report
        extension_by_id = {}
        if extensions_data:
            for ext in extensions_data:
                ext_id = ext.get('id')
                if ext_id is not None:
                    extension_by_id[ext_id] = ext

        enrichment_ctx = {
            'uuid_to_expanded': uuid_to_expanded,
            'uuid_to_log_source_types': uuid_to_log_source_types,
            'uuid_to_lst_status': lst_status,
            'type_id_to_instances': type_id_to_instances,
            'type_id_to_name': type_id_to_name,
            'active_type_ids': active_type_ids,
            'uuid_to_extensions': uuid_to_extensions,
            'uuid_to_extension_name': uuid_to_extension_name,
            'id_to_mitre': id_to_mitre,
            'mitre_error': mitre_error,
            'qradar_version': qradar_version,
            'extension_by_id': extension_by_id,
            'group_id_to_name': group_id_to_name,
            'group_id_to_group': group_id_to_group,
            'log_sources': log_sources,
            'high_to_low_ids': high_to_low_ids,
        }

        logger.info('Enrichment context built: {0} expanded rules, '
                     '{1} active source types, {2} active instances'.format(
                         len(uuid_to_expanded), len(active_type_ids),
                         sum(len(v) for v in type_id_to_instances.values())))

        return enrichment_ctx

    def _build_high_to_low_ids(self, temp_dir):
        """Build high-level to low-level category ID index.

        Groups low_level_categories.json records by high_level_category_id
        to enable fallback expansion when event_category_ids contains a
        high-level category ID.

        Args:
            temp_dir: Path to temp directory containing reference data.

        Returns:
            dict: {high_level_id_str: [low_level_id_str, ...]}.
                  Empty dict if file is missing or unparseable.
        """
        logger = logging.getLogger(__name__)
        high_to_low = {}
        filepath = os.path.join(temp_dir, 'low_level_categories.json')

        if not os.path.exists(filepath):
            logger.warning(
                'Missing low_level_categories.json — '
                'high-level category expansion disabled')
            return high_to_low

        try:
            with io.open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for record in data:
                    high_id = record.get('high_level_category_id')
                    low_id = record.get('id')
                    if high_id is not None and low_id is not None:
                        high_str = str(high_id)
                        if high_str not in high_to_low:
                            high_to_low[high_str] = []
                        high_to_low[high_str].append(str(low_id))
        except (ValueError, IOError) as exc:
            logger.warning(
                'Failed to parse low_level_categories.json: '
                '{0}'.format(exc))

        logger.debug('High-to-low category index: {0} high-level IDs, '
                     '{1} total children'.format(
                         len(high_to_low),
                         sum(len(v) for v in high_to_low.values())))
        return high_to_low

    def _load_optional_json(self, filepath, label):
        """Load an optional JSON file, returning empty list on failure.

        Args:
            filepath: Absolute path to JSON file.
            label: Display name for logging.

        Returns:
            list or dict: Parsed JSON data, or empty list if missing/corrupt.
        """
        logger = logging.getLogger(__name__)
        if not os.path.exists(filepath):
            logger.warning('Missing optional file: {0}'.format(label))
            return []
        try:
            with io.open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (ValueError, IOError) as exc:
            logger.warning('Failed to parse {0}: {1}'.format(label, exc))
            return []

    def _identify_active_log_sources(self, log_sources, active_days):
        """Filter log source instances to active-only.

        Args:
            log_sources: list of log source dicts from log_sources.json.
            active_days: int activity window in days.

        Returns:
            tuple: (active_type_ids set, type_id_to_instances dict,
                    type_id_to_name dict).
        """
        logger = logging.getLogger(__name__)
        active_type_ids = set()
        type_id_to_instances = {}
        type_id_to_name = {}

        if not log_sources:
            return active_type_ids, type_id_to_instances, type_id_to_name

        # Calculate cutoff time (millisecond epoch)
        now_ms = int(time.time() * 1000)
        cutoff_ms = now_ms - (active_days * 86400 * 1000)

        for ls in log_sources:
            # Criterion 1: enabled
            if not ls.get('enabled', False):
                continue

            # Criterion 2: recent events
            last_event = ls.get('last_event_time', 0)
            if last_event < cutoff_ms:
                continue

            # Active — add to results
            type_id = ls.get('type_id', 0)
            type_id_str = str(type_id)
            active_type_ids.add(type_id)

            if type_id_str not in type_id_to_instances:
                type_id_to_instances[type_id_str] = []
            type_id_to_instances[type_id_str].append(ls)

            # Populate type name from type_name field if available
            type_name = ls.get('type_name', '')
            if type_name and type_id_str not in type_id_to_name:
                type_id_to_name[type_id_str] = type_name

        logger.debug('Active log sources: {0} instances across '
                      '{1} types (cutoff: {2} days)'.format(
                          sum(len(v) for v in type_id_to_instances.values()),
                          len(active_type_ids), active_days))

        return active_type_ids, type_id_to_instances, type_id_to_name

    def _build_qid_lookups(self, qid_records_path):
        """Build QID record lookups for LST resolution.

        Args:
            qid_records_path: Path to qid_records.json.

        Returns:
            tuple: (qid_lookup {qid_str: record}, category_lookup
                    {low_level_category_id_str: [record_list]}).
        """
        logger = logging.getLogger(__name__)
        qid_lookup = {}
        category_lookup = {}

        if not os.path.exists(qid_records_path):
            logger.warning('Missing optional file: qid_records.json')
            return qid_lookup, category_lookup

        file_size = os.path.getsize(qid_records_path)

        if file_size > STREAMING_THRESHOLD_BYTES:
            logger.debug('Streaming large QID records file: {0:.1f} MB'.format(
                file_size / (1024.0 * 1024.0)))
            try:
                for record in iter_json_array(qid_records_path):
                    try:
                        qid_str = str(record.get('qid', ''))
                        if qid_str:
                            qid_lookup[qid_str] = record
                        cat_str = str(record.get('low_level_category_id', ''))
                        if cat_str:
                            if cat_str not in category_lookup:
                                category_lookup[cat_str] = []
                            category_lookup[cat_str].append(record)
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed QID record')
                        continue
            except IOError as exc:
                logger.warning('Failed to stream qid_records.json: '
                               '{0}'.format(exc))
        else:
            try:
                with io.open(qid_records_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for record in data:
                        qid_str = str(record.get('qid', ''))
                        if qid_str:
                            qid_lookup[qid_str] = record
                        cat_str = str(record.get('low_level_category_id', ''))
                        if cat_str:
                            if cat_str not in category_lookup:
                                category_lookup[cat_str] = []
                            category_lookup[cat_str].append(record)
            except (ValueError, IOError) as exc:
                logger.warning('Failed to parse qid_records.json: '
                               '{0}'.format(exc))

        logger.debug('QID lookups: {0} by QID, {1} categories'.format(
            len(qid_lookup), len(category_lookup)))
        return qid_lookup, category_lookup

    def _build_dsm_lookup(self, dsm_mappings_path):
        """Build DSM event mapping lookup (qid_record_id → type_id).

        Args:
            dsm_mappings_path: Path to dsm_event_mappings.json.

        Returns:
            dict: {qid_record_id_str: log_source_type_id_int}.
        """
        logger = logging.getLogger(__name__)
        dsm_lookup = {}

        if not os.path.exists(dsm_mappings_path):
            logger.warning('Missing optional file: dsm_event_mappings.json')
            return dsm_lookup

        file_size = os.path.getsize(dsm_mappings_path)

        if file_size > STREAMING_THRESHOLD_BYTES:
            logger.debug('Streaming large DSM mappings file: '
                          '{0:.1f} MB'.format(
                              file_size / (1024.0 * 1024.0)))
            try:
                for mapping in iter_json_array(dsm_mappings_path):
                    try:
                        rec_id = str(mapping.get('qid_record_id', ''))
                        type_id = mapping.get('log_source_type_id')
                        if rec_id and type_id is not None:
                            dsm_lookup[rec_id] = type_id
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed DSM mapping record')
                        continue
            except IOError as exc:
                logger.warning('Failed to stream dsm_event_mappings.json: '
                               '{0}'.format(exc))
        else:
            try:
                with io.open(dsm_mappings_path, 'r',
                             encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for mapping in data:
                        rec_id = str(mapping.get('qid_record_id', ''))
                        type_id = mapping.get('log_source_type_id')
                        if rec_id and type_id is not None:
                            dsm_lookup[rec_id] = type_id
            except (ValueError, IOError) as exc:
                logger.warning('Failed to parse dsm_event_mappings.json: '
                               '{0}'.format(exc))

        logger.debug('DSM lookup: {0} mappings'.format(len(dsm_lookup)))
        return dsm_lookup

    def _resolve_expression_lsts(self, record, category_lookup,
                                  dsm_lookup, active_type_ids):
        """Resolve one expression record to a set of log source type IDs.

        Uses 3-tier precedence:
        1. Specific log_source_type_id (not None, not -1)
        2. Category-based reverse lookup (low_level_category_id valid)
        3. Unrestricted — all active LST IDs

        Args:
            record: Expression record dict.
            category_lookup: {cat_str: [qid_records]}.
            dsm_lookup: {qid_record_id_str: log_source_type_id}.
            active_type_ids: set of active log source type IDs.

        Returns:
            set: Resolved log source type IDs.
        """
        lst_id = record.get('log_source_type_id')
        cat_id = record.get('low_level_category_id')

        # Tier 1: Specific LST
        if lst_id is not None and lst_id != -1:
            return {lst_id}

        # Tier 2: Category-based reverse lookup
        if cat_id is not None and cat_id != -1 and cat_id != 0:
            resolved = set()
            cat_key = str(cat_id)
            qid_records = category_lookup.get(cat_key, [])
            for qid_rec in qid_records:
                rec_id = str(qid_rec.get('id', ''))
                type_id = dsm_lookup.get(rec_id)
                if type_id is not None:
                    resolved.add(type_id)
            return resolved

        # Tier 3: Unrestricted — ALL active LST IDs
        return set(active_type_ids)

    def _build_property_to_lst_mapping(self, data_dir, category_lookup,
                                        dsm_lookup, active_type_ids):
        """Build property name to log source type IDs mapping.

        Args:
            data_dir: Path to workspace directory with reference files.
            category_lookup: {cat_str: [qid_records]}.
            dsm_lookup: {qid_record_id_str: log_source_type_id}.
            active_type_ids: set of active log source type IDs.

        Returns:
            dict: {property_name: set(log_source_type_id)}.
        """
        logger = logging.getLogger(__name__)

        # 1. Load property definitions
        props_path = os.path.join(data_dir, 'regex_properties.json')
        if not os.path.exists(props_path):
            logger.warning(
                'Custom property definitions not found: '
                'regex_properties.json — skipping property LST resolution'
            )
            return {}

        try:
            with io.open(props_path, 'r', encoding='utf-8') as f:
                properties = json.load(f)
        except (ValueError, IOError) as exc:
            logger.warning(
                'Failed to parse regex_properties.json: {0}'.format(exc)
            )
            return {}

        if not properties:
            return {}

        identifier_to_name = {}
        for prop in properties:
            identifier_to_name[prop.get('identifier', '')] = \
                prop.get('name', '')

        # 2. Load all expression files and resolve LSTs
        expression_files = [
            'property_expressions',
            'property_leef_expressions',
            'property_cef_expressions',
            'property_json_expressions',
            'property_xml_expressions',
            'property_nvp_expressions',
            'property_genericlist_expressions',
            'property_aql_expressions',
            'property_calculated_expressions',
        ]

        identifier_to_lst_ids = {}

        for expr_file in expression_files:
            filepath = os.path.join(data_dir, expr_file + '.json')
            if not os.path.exists(filepath):
                logger.warning(
                    'Expression file not found: {0}.json'.format(expr_file)
                )
                continue

            try:
                with io.open(filepath, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            except (ValueError, IOError) as exc:
                logger.warning(
                    'Failed to parse {0}.json: {1}'.format(expr_file, exc)
                )
                continue

            if not isinstance(records, list):
                continue

            for record in records:
                prop_id = record.get('regex_property_identifier', '')
                if prop_id not in identifier_to_name:
                    logger.debug(
                        'Orphan expression {0}: unmatched identifier'.format(
                            prop_id)
                    )
                    continue

                lst_ids = self._resolve_expression_lsts(
                    record, category_lookup, dsm_lookup, active_type_ids
                )
                if prop_id not in identifier_to_lst_ids:
                    identifier_to_lst_ids[prop_id] = set()
                identifier_to_lst_ids[prop_id].update(lst_ids)

        # 3. Convert {identifier: set} → {name: set}
        property_name_to_lst_ids = {}
        for identifier, lst_ids in identifier_to_lst_ids.items():
            name = identifier_to_name.get(identifier, '')
            if not name:
                continue
            if name not in property_name_to_lst_ids:
                property_name_to_lst_ids[name] = set()
            property_name_to_lst_ids[name].update(lst_ids)

        logger.debug(
            'Property-to-LST mapping: {0} properties resolved'.format(
                len(property_name_to_lst_ids))
        )
        return property_name_to_lst_ids

    def _build_group_member_index(self, log_sources):
        # type: (list) -> dict
        """Build a group_id → [log_source, ...] membership index.

        Args:
            log_sources: list of log source record dicts.

        Returns:
            dict: {int(group_id): [log_source_dict, ...]}.
        """
        index = {}
        for ls in log_sources:
            try:
                groups = ls.get('group_ids', [])
                if not isinstance(groups, (list, tuple)):
                    continue
            except (AttributeError, TypeError):
                continue
            for g in groups:
                if g is None:
                    continue
                try:
                    g_int = int(g)
                except (ValueError, TypeError):
                    continue
                if g_int not in index:
                    index[g_int] = []
                index[g_int].append(ls)
        return index

    def _get_group_log_sources(self, group_id, group_map,
                               group_member_index, visited=None):
        """Recursively retrieve all log sources within a group hierarchy.

        Args:
            group_id: int — group ID to start from.
            group_map: dict — {group_id: group_record}.
            group_member_index: dict — {int(group_id): [log_source, ...]},
                pre-built by _build_group_member_index.
            visited: set — visited group IDs (for cycle detection).

        Returns:
            list: log sources belonging to this group or its descendants.
        """
        if visited is None:
            visited = set()

        if group_id in visited:
            return []

        visited.add(group_id)

        # Normalize group_id to int for type-safe comparison
        try:
            group_id_int = int(group_id)
        except (ValueError, TypeError):
            # If group_id is not numeric, fall back to original value
            group_id_int = group_id

        # Collect log sources directly in this group via pre-built index
        result = list(group_member_index.get(group_id_int, []))

        # Recursively collect from child groups
        # Use normalized group_id_int for map lookup (keys are integers from JSON)
        group = group_map.get(group_id_int, {})
        child_ids = group.get('child_group_ids')
        if child_ids and isinstance(child_ids, list):
            for child_id in child_ids:
                if child_id is not None:
                    child_log_sources = self._get_group_log_sources(
                        child_id, group_map, group_member_index, visited)
                    result.extend(child_log_sources)

        return result

    def _build_log_sources_type_lookup(self, log_sources):
        # type: (list) -> dict
        """Build device_id to log_source_type_id mapping.

        Args:
            log_sources: List of log source record dicts.

        Returns:
            dict: {str(device_id): int(type_id)}.
        """
        lookup = {}
        for ls in log_sources:
            device_id = ls.get('id')
            type_id = ls.get('type_id')
            if device_id is not None and type_id is not None:
                lookup[str(device_id)] = int(type_id)
        return lookup

    def _resolve_test_to_type_ids(self, test, lookup_tables, rule_uuid=''):
        # type: (dict, dict, str) -> set or None
        """Resolve a single LST test to a set of log source type IDs.

        Does NOT apply negate — caller handles that.

        Returns None (universal / no constraint) when an event_properties
        test references a built-in system property not present in the
        custom property lookup.

        Args:
            test: LSTTest dict with dep_type, values, negate.
            lookup_tables: Dict of all lookup tables.
            rule_uuid: UUID of the rule being processed (for log messages).

        Returns:
            set of int or None: Resolved type IDs (may be empty), or
                None if the test imposes no LST constraint (universal).
        """
        logger = logging.getLogger(__name__)
        dep_type = test['dep_type']
        values = test['values']
        result = set()

        if dep_type == 'device_type_ids':
            for v in values:
                try:
                    result.add(int(v))
                except (ValueError, TypeError):
                    pass  # skip non-numeric XML values

        elif dep_type == 'event_categories':
            category_lookup = lookup_tables.get('category_lookup', {})
            dsm_lookup = lookup_tables.get('dsm_lookup', {})
            high_to_low = lookup_tables.get('high_to_low_ids', {})
            for v in values:
                records = category_lookup.get(str(v), [])
                if not records:
                    # High-level category fallback
                    child_ids = high_to_low.get(str(v), [])
                    for child_id in child_ids:
                        records.extend(
                            category_lookup.get(child_id, []))
                for rec in records:
                    rec_id = str(rec.get('id', ''))
                    if rec_id:
                        type_id = dsm_lookup.get(rec_id)
                        if type_id is not None:
                            result.add(type_id)

        elif dep_type == 'qids':
            qid_lookup = lookup_tables.get('qid_lookup', {})
            dsm_lookup = lookup_tables.get('dsm_lookup', {})
            for v in values:
                record = qid_lookup.get(str(v), {})
                rec_id = str(record.get('id', ''))
                if rec_id:
                    type_id = dsm_lookup.get(rec_id)
                    if type_id is not None:
                        result.add(type_id)

        elif dep_type == 'event_properties':
            prop_lookup = lookup_tables.get('property_name_to_lst_ids', {})
            for v in values:
                if v not in prop_lookup:
                    # Unrecognized property — treat as built-in
                    # system property (universal, no LST constraint).
                    logger.debug(
                        'Property %r not in custom property lookup for '
                        'rule %s — assuming system property (universal)',
                        v, rule_uuid)
                    return None
                result.update(prop_lookup[v])

        elif dep_type == 'device_group_ids':
            group_map = lookup_tables.get('group_map', {})
            group_member_index = lookup_tables.get('group_member_index')
            if group_member_index is None:
                log_sources = lookup_tables.get('log_sources', [])
                group_member_index = self._build_group_member_index(
                    log_sources)
            for v in values:
                group_log_sources = self._get_group_log_sources(
                    v, group_map, group_member_index)
                for ls in group_log_sources:
                    ls_type_id = ls.get('type_id')
                    if ls_type_id is not None:
                        result.add(int(ls_type_id))

        elif dep_type == 'device_ids':
            ls_type_lookup = lookup_tables.get('log_sources_type', {})
            for v in values:
                type_id = ls_type_lookup.get(str(v))
                if type_id is not None:
                    result.add(type_id)

        else:
            logger.warning(
                'Unknown dep_type in LST test: {0} (rule {1})'.format(
                    dep_type, rule_uuid))

        logger.debug('LST test %s values=%s -> type_ids=%s',
                     dep_type, values, result)
        return result

    def _resolve_lst_for_rule(self, uuid, uuid_to_expanded, lookup_tables,
                              memo, visited):
        # type: (str, dict, dict, dict, set) -> set or None
        """Resolve LST set for a rule via own tests, negate, and BB chains.

        Args:
            uuid: UUID of the rule/BB to resolve.
            uuid_to_expanded: UUID to expanded rule record.
            lookup_tables: All lookup tables (includes 'active_type_ids').
            memo: Memoization cache {uuid: set or None}.
            visited: UUIDs in current recursion stack.

        Returns:
            set of int or None: Resolved LST IDs, or None (universal).
        """
        logger = logging.getLogger(__name__)

        if uuid in memo:
            logger.debug('LST resolve memo hit for %s', uuid)
            return memo[uuid]

        if uuid in visited:
            logger.warning('Cycle detected for UUID %s — returning empty', uuid)
            return set()

        if uuid not in uuid_to_expanded:
            logger.warning('Orphaned BB UUID %s not in expanded rules', uuid)
            return None

        visited.add(uuid)
        rule = uuid_to_expanded[uuid]

        constraints = []

        # Step 5: Resolve own tests
        for test in rule.get('lst_tests', []):
            resolved = self._resolve_test_to_type_ids(test, lookup_tables,
                                                         rule_uuid=uuid)
            if test.get('negate', False):
                if resolved is None:
                    # Negate of None (no LST info) stays None.
                    # None means "no LST-constraining data" (e.g. unsupported
                    # test type). Negating absence of info cannot produce info.
                    pass
                elif test.get('dep_type') == 'device_type_ids':
                    # Only device_type_ids negation is valid at LST level —
                    # "event did NOT come from type X" excludes that LST.
                    # All other dep_types have indirect mappings.
                    all_type_ids = lookup_tables.get('all_type_ids', set())
                    resolved = all_type_ids - resolved
                else:
                    # Non-device_type_ids negation is event-level
                    # (e.g. "category != X"). One LST can produce many
                    # categories — negation doesn't exclude the LST.
                    resolved = None
                logger.debug('LST negate applied for %s: %s', uuid, resolved)
            constraints.append(resolved)

        # Step 6: Resolve BB ref groups
        for group in rule.get('bb_ref_groups', []):
            child_results = []
            for child_uuid in group.get('uuids', []):
                child_result = self._resolve_lst_for_rule(
                    child_uuid, uuid_to_expanded, lookup_tables, memo, visited)
                child_results.append(child_result)

            if not child_results:
                continue

            mode = group.get('mode', 'any')
            if mode == 'all':
                combined = _intersect_lst_sets(child_results)
            else:
                # 'any' mode: None-aware union
                # None = no LST info (skip), not universal set (absorb)
                combined = None
                has_non_none = False
                for cr in child_results:
                    if cr is None:
                        # Skip None — it contributes no LST constraint
                        continue
                    if not has_non_none:
                        combined = set(cr)
                        has_non_none = True
                    else:
                        combined = combined | cr
                if has_non_none:
                    pass  # combined is already the union set
                # else combined stays None (all children were None)

            if combined is not None and group.get('negate', False):
                # BB group negation is always event-level exclusion.
                # BB groups are multi-condition aggregates — negation cannot
                # reliably exclude LSTs. Always produce None.
                combined = None
            elif combined is None and group.get('negate', False):
                # Negate of None (no LST info) stays None.
                pass

            if combined is not None:
                constraints.append(combined)
                logger.debug('LST BB group mode=%s negate=%s for %s: %s',
                             mode, group.get('negate', False), uuid, combined)

        result = _intersect_lst_sets(constraints)

        logger.debug('LST resolve %s: %d constraints -> %s',
                     uuid, len(constraints), result)
        visited.discard(uuid)
        memo[uuid] = result
        return result

    def _build_uuid_to_log_source_types(self, uuid_to_expanded, qid_lookup,
                                         category_lookup, dsm_lookup,
                                         active_type_ids,
                                         property_name_to_lst_ids=None,
                                         log_sources=None,
                                         group_map=None,
                                         high_to_low_ids=None,
                                         lst_status_out=None,
                                         all_type_ids=None):
        """Map rule UUID to set of matched active log source type IDs.

        Args:
            uuid_to_expanded: {uuid: expanded_rule_dict}.
            qid_lookup: {qid_str: record_dict}.
            category_lookup: {category_str: [record_list]}.
            dsm_lookup: {qid_record_id_str: log_source_type_id}.
            active_type_ids: set of active log source type IDs.
            property_name_to_lst_ids: {property_name: set(type_ids)}.
                None for backward compatibility (Pathway 4 skipped).
            log_sources: list of log source records for Pathway 5.
                None for backward compatibility (Pathway 5 skipped).
            group_map: {group_id: group_record} for Pathway 5.
                None for backward compatibility (Pathway 5 skipped).
            high_to_low_ids: {high_level_id_str: [low_level_id_str, ...]}.
                None for backward compatibility (high-level fallback skipped).
            lst_status_out: dict or None. When provided, populated with
                {uuid_str: status_str} for each rule. Status values:
                'matched', 'no_tests', 'lst_inactive', 'disjoint', 'unknown'.

        Returns:
            dict: {uuid_str: set_of_type_ids}.
        """
        logger = logging.getLogger(__name__)
        result = {}

        # Build lookup_tables dict for the new resolver
        lookup_tables = {
            'dsm_lookup': dsm_lookup,
            'category_lookup': category_lookup,
            'qid_lookup': qid_lookup,
            'property_name_to_lst_ids': property_name_to_lst_ids or {},
            'group_map': group_map or {},
            'log_sources': log_sources or [],
            'log_sources_type': (
                self._build_log_sources_type_lookup(log_sources)
                if log_sources else {}
            ),
            'group_member_index': (
                self._build_group_member_index(log_sources)
                if log_sources else {}
            ),
            'active_type_ids': active_type_ids,
            'all_type_ids': all_type_ids or active_type_ids,
            'high_to_low_ids': high_to_low_ids or {},
        }
        memo = {}

        for uuid, expanded in uuid_to_expanded.items():
            # NEW: Boolean-aware resolution when lst_tests present
            if 'lst_tests' in expanded:
                resolved = self._resolve_lst_for_rule(
                    uuid, uuid_to_expanded, lookup_tables, memo, set())
                if resolved is None:
                    status = 'no_tests'
                elif len(resolved) == 0:
                    status = 'disjoint'
                elif resolved & active_type_ids:
                    status = 'matched'
                    result[uuid] = resolved & active_type_ids
                else:
                    status = 'lst_inactive'
                if lst_status_out is not None:
                    lst_status_out[uuid] = status
                continue

            # EXISTING: Union-based fallback (backward compatibility)
            matched_types = set()

            # Pathway 1: event_category_ids → QID records → DSM → type
            event_cat_ids = expanded.get('event_category_ids', [])
            h2l = high_to_low_ids or {}
            for cat_id in event_cat_ids:
                cat_str = str(cat_id)
                records = category_lookup.get(cat_str, [])
                if not records:
                    # High-level category fallback
                    child_ids = h2l.get(cat_str, [])
                    for child_id in child_ids:
                        records.extend(
                            category_lookup.get(child_id, []))
                for rec in records:
                    rec_id = str(rec.get('id', ''))
                    if rec_id:
                        type_id = dsm_lookup.get(rec_id)
                        if type_id is not None:
                            matched_types.add(type_id)

            # Pathway 2: qid_ids → QID record → DSM → type
            qid_ids = expanded.get('qid_ids',
                                   expanded.get('expanded_qids', []))
            for qid_id in qid_ids:
                qid_str = str(qid_id)
                record = qid_lookup.get(qid_str, {})
                rec_id = str(record.get('id', ''))
                if rec_id:
                    type_id = dsm_lookup.get(rec_id)
                    if type_id is not None:
                        matched_types.add(type_id)

            # Pathway 3: device_type_id_ids → direct type ID
            device_type_ids = expanded.get('device_type_id_ids', [])
            for dt_id in device_type_ids:
                try:
                    matched_types.add(int(dt_id))
                except (ValueError, TypeError):
                    pass  # skip non-numeric XML values

            # Pathway 4: expanded_custom_properties → property LST IDs
            if property_name_to_lst_ids:
                custom_props = expanded.get(
                    'expanded_custom_properties', [])
                for prop_name in custom_props:
                    prop_lsts = property_name_to_lst_ids.get(
                        prop_name, set())
                    matched_types.update(prop_lsts)

            # Pathway 5: device_group_ids → recursive group traversal → log sources → type IDs
            if log_sources is not None and group_map is not None:
                grp_index = lookup_tables.get('group_member_index', {})
                device_grp_ids = expanded.get('device_group_ids', [])
                for grp_id in device_grp_ids:
                    group_log_sources = self._get_group_log_sources(
                        grp_id, group_map, grp_index)
                    for ls in group_log_sources:
                        ls_type_id = ls.get('type_id')
                        if ls_type_id is not None:
                            try:
                                matched_types.add(int(ls_type_id))
                            except (ValueError, TypeError):
                                pass  # skip non-numeric XML values

            # Intersect with active types
            active_matched = matched_types & active_type_ids
            if active_matched:
                result[uuid] = active_matched
                status = 'matched'
            else:
                status = 'unknown'
            if lst_status_out is not None:
                lst_status_out[uuid] = status

        logger.debug('UUID-to-log-source-types: {0} rules with matches '
                      'out of {1}'.format(len(result),
                                          len(uuid_to_expanded)))
        return result

    def _build_uuid_to_extensions(self, extensions_data):
        """Map rule UUID to extension info.

        Args:
            extensions_data: list of extension dicts from extensions.json.

        Returns:
            tuple: (uuid_to_ext dict, uuid_to_extension_name dict).
        """
        logger = logging.getLogger(__name__)
        uuid_to_ext = {}
        uuid_to_extension_name = {}
        # Track highest install_time per UUID for Content extension name
        uuid_to_best_time = {}

        if not extensions_data:
            return uuid_to_ext, uuid_to_extension_name

        for ext in extensions_data:
            ext_name = ext.get('name', '')
            ext_version = ext.get('version', '')
            ext_author = ext.get('author', '')
            ext_install_time = ext.get('install_time', 0)
            if ext_install_time is None:
                ext_install_time = 0
            contents = ext.get('contents', [])

            if not isinstance(contents, list):
                continue

            for content_item in contents:
                if not isinstance(content_item, dict):
                    continue
                if content_item.get('content_type_id') == \
                        EXTENSION_CONTENT_TYPE_RULE:
                    rule_uuid = content_item.get('identifier', '')
                    if rule_uuid:
                        ext_info = {
                            'name': ext_name,
                            'version': ext_version,
                        }
                        if ext_author:
                            ext_info['author'] = ext_author
                        if rule_uuid not in uuid_to_ext:
                            uuid_to_ext[rule_uuid] = []
                        uuid_to_ext[rule_uuid].append(ext_info)
                        # Track most recently installed extension name
                        best_time = uuid_to_best_time.get(rule_uuid, -1)
                        if ext_install_time > best_time:
                            uuid_to_best_time[rule_uuid] = ext_install_time
                            uuid_to_extension_name[rule_uuid] = ext_name

        logger.debug('UUID-to-extensions: {0} rules with extension '
                      'mappings'.format(len(uuid_to_ext)))
        return uuid_to_ext, uuid_to_extension_name

    def _build_mitre_lookup(self, mitre_data):
        """Build MITRE ATT&CK lookup mapping UUID to tactics/techniques.

        Args:
            mitre_data: list or dict from mitre_mappings.json.

        Returns:
            tuple: (id_to_mitre dict, mitre_error bool).
        """
        logger = logging.getLogger(__name__)
        id_to_mitre = {}
        mitre_error = False

        if not mitre_data:
            return id_to_mitre, mitre_error

        # Check for error key
        if isinstance(mitre_data, dict):
            if mitre_data.get('error'):
                logger.warning('MITRE data contains error flag')
                mitre_error = True
                return id_to_mitre, mitre_error

            # Single dict with rule mappings
            rules = mitre_data.get('rules', [])
            if not rules:
                # Direct mapping: keys are rule names, values contain
                # 'id' (rule UUID) and 'mapping' (tactic→technique dict).
                for rule_name, val in mitre_data.items():
                    if not isinstance(val, dict):
                        continue
                    uuid = val.get('id', rule_name)
                    if not uuid:
                        continue
                    tactics = []
                    techniques = []
                    mapping = val.get('mapping', {})
                    if isinstance(mapping, dict):
                        for tactic_name, tactic_data in mapping.items():
                            if isinstance(tactic_data, dict):
                                tactics.append(tactic_name)
                                techs = tactic_data.get('techniques', {})
                                if isinstance(techs, dict):
                                    for _t_name, t_data in techs.items():
                                        if isinstance(t_data, dict):
                                            t_id = t_data.get('id', '')
                                            if t_id:
                                                techniques.append(t_id)
                    if tactics or techniques:
                        id_to_mitre[uuid] = {
                            'tactics': sorted(set(tactics)),
                            'techniques': sorted(set(techniques)),
                        }
        elif isinstance(mitre_data, list):
            # Check for error entry
            for item in mitre_data:
                if isinstance(item, dict) and item.get('error'):
                    logger.warning('MITRE data contains error flag')
                    mitre_error = True
                    return id_to_mitre, mitre_error

            rules = mitre_data
        else:
            return id_to_mitre, mitre_error

        # Process rules array
        if not isinstance(rules, list):
            rules = []

        for rule_mapping in rules:
            if not isinstance(rule_mapping, dict):
                continue
            uuid = rule_mapping.get('uuid', rule_mapping.get('id', ''))
            if not uuid:
                continue

            tactics = []
            techniques = []

            # Handle nested tactic/technique structure
            mitre_entries = rule_mapping.get('mitre', [])
            if isinstance(mitre_entries, list):
                for entry in mitre_entries:
                    if isinstance(entry, dict):
                        tactic = entry.get('tactic', '')
                        if tactic:
                            tactics.append(tactic)
                        techs = entry.get('techniques', [])
                        if isinstance(techs, list):
                            techniques.extend(techs)

            # Handle direct tactics/techniques arrays
            direct_tactics = rule_mapping.get('tactics', [])
            if isinstance(direct_tactics, list):
                tactics.extend(direct_tactics)

            direct_techniques = rule_mapping.get('techniques', [])
            if isinstance(direct_techniques, list):
                techniques.extend(direct_techniques)

            if tactics or techniques:
                id_to_mitre[uuid] = {
                    'tactics': list(set(tactics)),
                    'techniques': list(set(techniques)),
                }

        logger.debug('MITRE lookup: {0} rules with mappings'.format(
            len(id_to_mitre)))
        return id_to_mitre, mitre_error

    def _build_lookup_table(self, filepath, id_field, name_field):
        """Build ID-to-name lookup from a JSON array of records.

        Args:
            filepath: Path to JSON file containing array of records.
            id_field: Key name for the ID field.
            name_field: Key name for the name field.

        Returns:
            dict: {id_string: name_string}. Empty dict if file missing.
        """
        logger = logging.getLogger(__name__)

        if not os.path.exists(filepath):
            logger.warning('Missing reference file: {0}'.format(filepath))
            return {}

        file_size = os.path.getsize(filepath)
        lookup = {}

        if file_size > STREAMING_THRESHOLD_BYTES:
            logger.debug('Streaming large file: {0} ({1:.1f} MB)'.format(
                filepath, file_size / (1024.0 * 1024.0)))
            try:
                for item in iter_json_array(filepath):
                    try:
                        lookup[str(item[id_field])] = item[name_field]
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed record in %s', filepath)
                        continue
            except IOError as exc:
                logger.warning('Failed to stream {0}: {1}'.format(
                    filepath, exc))
                return {}
        else:
            try:
                with io.open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    logger.warning('Expected array in {0}, got {1}'.format(
                        filepath, type(data).__name__))
                    return {}
                for item in data:
                    try:
                        lookup[str(item[id_field])] = item[name_field]
                    except (KeyError, TypeError):
                        logger.debug('Skipped malformed record in %s', filepath)
                        continue
            except (ValueError, IOError) as exc:
                logger.warning('Failed to parse {0}: {1}'.format(
                    filepath, exc))
                return {}

        logger.debug('Built lookup: {0} with {1} entries'.format(
            os.path.basename(filepath), len(lookup)))
        return lookup

    def _read_ucm_csv(self, csv_path):
        """Read UCM CSV and return rows with fieldnames.

        Args:
            csv_path: Absolute path to UCM CSV file.

        Returns:
            tuple: (rows list of dicts, fieldnames list).

        Raises:
            CriticalPhaseError: If file missing or entirely unparseable.
        """
        logger = logging.getLogger(__name__)

        if not os.path.exists(csv_path):
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'UCM CSV file not found: {0}'.format(csv_path)
            )

        rows = []
        fieldnames = []
        malformed_count = 0

        try:
            if PY2:
                # Python 2: csv module requires byte strings, not unicode.
                # Read as bytes, strip BOM, feed BytesIO to DictReader,
                # then decode values after reading.
                with open(csv_path, 'rb') as f:
                    raw = f.read()
                # Strip UTF-8 BOM
                if raw.startswith(b'\xef\xbb\xbf'):
                    raw = raw[3:]
                reader = csv.DictReader(io.BytesIO(raw))
                fieldnames = [
                    fn.decode('utf-8') if isinstance(fn, bytes) else fn
                    for fn in (reader.fieldnames or [])
                ]
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate row has expected number of fields
                        if None in row:
                            malformed_count += 1
                            logger.warning(
                                'Malformed CSV row {0}: extra fields'.format(
                                    row_num))
                            continue
                        # Decode byte keys/values to unicode
                        decoded_row = {}
                        for k, v in row.items():
                            dk = k.decode('utf-8') if isinstance(k, bytes) else k
                            dv = v.decode('utf-8') if isinstance(v, bytes) else v
                            decoded_row[dk] = dv
                        rows.append(decoded_row)
                    except Exception as exc:
                        malformed_count += 1
                        logger.warning(
                            'Malformed CSV row {0}: {1}'.format(
                                row_num, exc))
            else:
                # Python 3: utf-8-sig handles BOM transparently
                with io.open(csv_path, 'r', encoding='utf-8-sig',
                             newline='') as f:
                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames if reader.fieldnames else []
                    for row_num, row in enumerate(reader, start=2):
                        try:
                            if None in row:
                                malformed_count += 1
                                logger.warning(
                                    'Malformed CSV row {0}: extra '
                                    'fields'.format(row_num))
                                continue
                            rows.append(row)
                        except Exception as exc:
                            malformed_count += 1
                            logger.warning(
                                'Malformed CSV row {0}: {1}'.format(
                                    row_num, exc))
        except (IOError, csv.Error) as exc:
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Failed to read UCM CSV: {0}'.format(csv_path),
                cause=exc
            )

        if malformed_count > 0:
            logger.warning('Skipped {0} malformed CSV rows'.format(
                malformed_count))

        logger.debug('Read {0} rows, {1} columns from UCM CSV'.format(
            len(rows), len(fieldnames)))
        return rows, fieldnames

    def _write_extended_csv(self, rows, fieldnames, output_path):
        """Write the extended CSV to disk.

        Args:
            rows: list of enriched row dicts.
            fieldnames: ordered list of all column names.
            output_path: absolute path for output file.

        Raises:
            CriticalPhaseError: If write fails.
        """
        logger = logging.getLogger(__name__)

        try:
            if PY2:
                with open(output_path, 'wb') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=fieldnames,
                        quoting=csv.QUOTE_ALL,
                        extrasaction='ignore')
                    writer.writeheader()
                    for row in rows:
                        # Encode unicode values to bytes for Py2
                        encoded = {}
                        for k, v in row.items():
                            if isinstance(v, text_type):
                                encoded[k] = v.encode('utf-8')
                            else:
                                encoded[k] = v
                        writer.writerow(encoded)
            else:
                with io.open(output_path, 'w', encoding='utf-8',
                             newline='') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=fieldnames,
                        quoting=csv.QUOTE_ALL,
                        extrasaction='ignore')
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row)

            logger.debug('Wrote {0} rows to {1}'.format(
                len(rows), output_path))

        except (IOError, csv.Error) as exc:
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Failed to write extended CSV: {0}'.format(output_path),
                cause=exc
            )

    def _generate_log_sources_report(self, context, enrichment_ctx):
        """Generate standalone active log sources inventory CSV.

        Args:
            context: PipelineContext instance.
            enrichment_ctx: enrichment context dict.

        Returns:
            str: Absolute path to generated CSV file.
        """
        logger = logging.getLogger(__name__)

        output_filename = 'qradar_log_sources_{0}.csv'.format(
            context.timestamp)
        output_path = os.path.join(context.output_dir, output_filename)

        type_id_to_instances = enrichment_ctx.get('type_id_to_instances', {})
        type_id_to_name = enrichment_ctx.get('type_id_to_name', {})
        extension_by_id = enrichment_ctx.get('extension_by_id', {})
        group_id_to_name = enrichment_ctx.get('group_id_to_name', {})

        # Build rows
        report_rows = []
        for type_id_str, instances in type_id_to_instances.items():
            type_name = type_id_to_name.get(type_id_str, '')

            # Resolve extension for this type
            ext_name = ''
            ext_author = ''
            ext_version = ''

            # Find log source type record to get extension ID
            # We need the log source type data — iterate instances to
            # get type info or use a pre-built lookup
            for ls in instances:
                ls_ext_id = ls.get('log_source_extension_id',
                                   ls.get('type_extension_id', 0))
                if ls_ext_id and ls_ext_id != 0:
                    ext_record = extension_by_id.get(ls_ext_id, {})
                    ext_name = ext_record.get('name', '')
                    ext_author = ext_record.get('author', '')
                    ext_version = ext_record.get('version', '')
                break  # Only need first instance for extension info

            for ls in instances:
                group_names = [
                    group_id_to_name[gid] for gid in ls.get('group_ids', [])
                    if gid in group_id_to_name
                ]
                
                row = {
                    'ls_id': ls.get('id', ''),
                    'ls_name': ls.get('name', ''),
                    'ls_description': ls.get('description', ''),
                    'ls_enabled': ls.get('enabled', ''),
                    'ls_average_eps': ls.get('average_eps', ''),
                    'ls_group_ids': format_bracket_list(
                        sorted(ls.get('group_ids', []))),
                    'ls_group_names': format_sorted_bracket_list(group_names),
                    'ls_status': ls.get('status', {}).get('status', '')
                    if isinstance(ls.get('status'), dict)
                    else str(ls.get('status', '')),
                    'ls_last_event_time': ls.get('last_event_time', ''),
                    'lst_id': type_id_str,
                    'lst_name': type_name,
                    'ext_name': ext_name,
                    'ext_author': ext_author,
                    'ext_version': ext_version,
                }
                report_rows.append(row)

        # Sort by lst_name ascending, then ls_name ascending
        report_rows.sort(key=lambda r: (
            r.get('lst_name', '').lower(),
            r.get('ls_name', '').lower()
        ))

        # Write CSV
        try:
            if PY2:
                with open(output_path, 'wb') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=LOG_SOURCE_REPORT_COLUMNS,
                        quoting=csv.QUOTE_ALL,
                        extrasaction='ignore')
                    writer.writeheader()
                    for row in report_rows:
                        encoded = {}
                        for k, v in row.items():
                            if isinstance(v, text_type):
                                encoded[k] = v.encode('utf-8')
                            else:
                                encoded[k] = v
                        writer.writerow(encoded)
            else:
                with io.open(output_path, 'w', encoding='utf-8',
                             newline='') as f:
                    writer = csv.DictWriter(
                        f, fieldnames=LOG_SOURCE_REPORT_COLUMNS,
                        quoting=csv.QUOTE_ALL,
                        extrasaction='ignore')
                    writer.writeheader()
                    for row in report_rows:
                        writer.writerow(row)

            logger.info('Log sources report: {0} active instances written '
                         'to {1}'.format(len(report_rows), output_path))

        except (IOError, csv.Error) as exc:
            raise CriticalPhaseError(
                'UCM CSV Extension',
                'Failed to write log sources report: {0}'.format(
                    output_path),
                cause=exc
            )

        return output_path

class PipelineOrchestrator(object):
    """
    Pipeline executor. No business logic—pure delegation pattern.

    Runs registered handlers in sequence, managing error classification:
      - CriticalPhaseError: abort pipeline, return 1
      - Other exceptions: log as non-critical, continue, return 0

    Prints summary banner after all handlers complete.
    """
    __slots__ = ('_handlers', '_formatter', '_context', '_logger')

    def __init__(self, context, formatter):
        """
        Initialize orchestrator with context and formatter.

        Args:
            context:   PipelineContext instance.
            formatter: PhaseFormatter instance (shared with logging).
        """
        self._context = context
        self._formatter = formatter
        self._handlers = []
        self._logger = logging.getLogger(__name__)

    def register(self, handler):
        """
        Append a handler to the execution queue.

        Args:
            handler: BaseHandler subclass instance.
        """
        self._handlers.append(handler)

    def execute(self):
        """
        Run all registered handlers in order.

        Returns:
            int: Exit code (0=success, 1=critical failure).
        """
        start_time = time.time()
        phases_run = 0

        try:
            for handler in self._handlers:
                phase_tag = 'PHASE {0}'.format(handler.phase_number)
                self._formatter.set_phase(phase_tag)

                self._logger.info('Starting {0}'.format(handler.name))
                self._logger.debug('Handler class: {0}'.format(
                    handler.__class__.__name__
                ))

                try:
                    handler.execute(self._context)
                    self._logger.info('Completed {0}'.format(handler.name))
                    phases_run += 1

                except CriticalPhaseError as exc:
                    self._logger.error(
                        'CRITICAL: {0} phase failed: {1}'.format(
                            handler.name, exc
                        )
                    )
                    elapsed = time.time() - start_time
                    self._print_summary(phases_run, elapsed, critical=True)
                    return 1

                except Exception as exc:
                    self._logger.error(
                        'Non-critical error in {0}: {1}'.format(
                            handler.name, exc
                        )
                    )
                    self._context.error_counter.increment(
                        handler.name, text_type(exc)
                    )
                    phases_run += 1

        finally:
            elapsed = time.time() - start_time

        self._print_summary(phases_run, elapsed, critical=False)
        return 0

    def _print_summary(self, phases_run, elapsed, critical=False):
        """
        Print summary banner with phase count, errors, and elapsed time.

        Args:
            phases_run: Number of phases that started execution.
            elapsed:    Elapsed time in seconds.
            critical:   True if a CriticalPhaseError occurred.
        """
        self._formatter.set_phase('SUMMARY')
        error_count = self._context.error_counter.count

        self._logger.info('=' * 60)
        self._logger.info('Pipeline Summary')
        self._logger.info('-' * 60)
        self._logger.info('Phases completed: {0}'.format(phases_run))
        self._logger.info('Non-critical errors: {0}'.format(error_count))
        self._logger.info('Elapsed time: {0:.2f}s'.format(elapsed))

        if critical:
            self._logger.info('Status: FAILED (critical error)')
        elif error_count > 0:
            self._logger.info(
                'Status: Completed with {0} non-critical error{1}'.format(
                    error_count, 's' if error_count != 1 else ''
                )
            )
        else:
            self._logger.info('Status: SUCCESS')

        # Show workspace path when retained (--debug or --cache-dir)
        if self._context.debug or self._context.cache_dir:
            self._logger.info(
                'Workspace: {0}'.format(self._context.temp_dir)
            )

        self._logger.info('=' * 60)


# ---------------------------------------------------------------------------
#  Logging
# ---------------------------------------------------------------------------

class PhaseFormatter(logging.Formatter):
    """Formatter with dynamic [PHASE N] tag injection."""

    def __init__(self):
        logging.Formatter.__init__(self)
        self._phase = 'INIT'

    def set_phase(self, phase):
        """Update the phase tag for all subsequent log entries."""
        self._phase = phase

    def format(self, record):
        """Format: [YYYY-MM-DDTHH:MM:SS.mmm] [PHASE] [LEVEL] Message"""
        timestamp = time.strftime(
            '%Y-%m-%dT%H:%M:%S', time.localtime(record.created)
        )
        msec = '%03d' % record.msecs
        return '[{ts}.{ms}] [{phase}] [{level}] {msg}'.format(
            ts=timestamp,
            ms=msec,
            phase=self._phase,
            level=record.levelname,
            msg=record.getMessage(),
        )


def setup_logging(log_path):
    """
    Configure file and console logging with a shared PhaseFormatter.

    Args:
        log_path: Absolute path to qradar_collector.log.

    Returns:
        PhaseFormatter: Shared formatter instance.
    """
    formatter = PhaseFormatter()
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # File handler — DEBUG and above
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler — INFO and above
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return formatter


# ---------------------------------------------------------------------------
#  Workspace Management
# ---------------------------------------------------------------------------

def create_workspace(timestamp):
    """
    Create timestamped workspace folder in the system temp directory.

    Args:
        timestamp: YYYYMMDDHHMMSS string.

    Returns:
        str: Absolute path to created directory.

    Raises:
        SystemExit: Code 2 if temporary directory cannot be created.
    """
    prefix = 'qradar_collector_{0}_'.format(timestamp)
    try:
        return tempfile.mkdtemp(prefix=prefix)
    except (OSError, IOError) as exc:
        sys.stderr.write(
            'Error: cannot create workspace directory in temp location: {0}\n'.format(
                exc
            )
        )
        sys.exit(2)


def cleanup_workspace(path):
    """
    Remove workspace directory (best-effort, ignores locked files).

    Args:
        path: Directory to remove.
    """
    if path and os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def create_debug_zip(workspace_path, output_dir, timestamp):
    """
    Create ZIP archive containing workspace contents and output CSVs.

    Args:
        workspace_path: Path to workspace directory to archive.
        output_dir: Path to output directory (for ZIP destination and CSV search).
        timestamp: YYYYMMDDHHMMSS string for consistent naming.

    Returns:
        str or None: Absolute path to created ZIP file, or None if creation failed.
    """
    zip_name = 'qradar_collector_debug_{0}.zip'.format(timestamp)
    zip_path = os.path.join(output_dir, zip_name)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all workspace contents
            if os.path.isdir(workspace_path):
                workspace_basename = os.path.basename(workspace_path)
                for root, dirs, files in os.walk(workspace_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        # Preserve directory structure in ZIP
                        arcname = os.path.join(
                            workspace_basename,
                            os.path.relpath(file_path, workspace_path)
                        )
                        zf.write(file_path, arcname)

            # Add output CSV files if they exist
            csv_patterns = [
                'qradar_rules_{0}.csv'.format(timestamp),
                'qradar_log_sources_{0}.csv'.format(timestamp)
            ]
            for csv_filename in csv_patterns:
                csv_path = os.path.join(output_dir, csv_filename)
                if os.path.isfile(csv_path):
                    zf.write(csv_path, csv_filename)

        return zip_path

    except (OSError, IOError, _BadZipFile) as exc:
        # Log warning but don't fail - cleanup will still proceed
        logger = logging.getLogger(__name__)
        logger.warning(
            'Failed to create debug ZIP archive: {0}'.format(exc)
        )
        return None


_cleanup_done = False  # Guard against signal + finally double-entry


def _perform_cleanup(workspace_path, output_dir, timestamp, context,
                     use_stderr=False):
    """
    Perform cleanup for normal exit and signal handler paths.

    Guarded against double-entry (signal + finally).

    Args:
        workspace_path: Workspace directory path.
        output_dir:     Output directory path.
        timestamp:      YYYYMMDDHHMMSS string.
        context:        PipelineContext with debug/cache_dir flags.
        use_stderr:     If True, output via sys.stderr.write (signal path).
                        If False, use print() and logger (main path).
    """
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    def _out(msg):
        if use_stderr:
            sys.stderr.write('\n{0}\n'.format(msg))
        else:
            print(msg)

    if context.debug:
        if not use_stderr:
            logger = logging.getLogger(__name__)
            logger.info('Creating debug archive')
        # Flush all handlers so the log file is up-to-date on disk
        for h in logging.root.handlers:
            h.flush()
        zip_path = create_debug_zip(workspace_path, output_dir, timestamp)
        if zip_path:
            _out('Debug archive created: {0}'.format(zip_path))
            logging.shutdown()
            cleanup_workspace(workspace_path)
        else:
            _out('Warning: Failed to create debug ZIP archive')
            _out('Working directory retained: {0}'.format(workspace_path))
            logging.shutdown()

    elif context.cache_dir:
        if not use_stderr:
            logger = logging.getLogger(__name__)
            logger.debug('Working directory retained for cache mode')
        _out('Working directory retained: {0}'.format(workspace_path))

    else:
        if not use_stderr:
            logger = logging.getLogger(__name__)
            logger.debug(
                'Cleaning up working directory: {0}'.format(workspace_path)
            )
        logging.shutdown()
        cleanup_workspace(workspace_path)


def _make_signal_handler(workspace_path, output_dir, timestamp, context):
    """
    Create a signal handler that handles debug ZIP creation and cleanup.

    Args:
        workspace_path: Workspace directory path.
        output_dir: Output directory path.
        timestamp: YYYYMMDDHHMMSS string.
        context: PipelineContext with debug/cache_dir flags.

    Returns:
        callable: Signal handler function.
    """
    def handler(signum, frame):
        _perform_cleanup(workspace_path, output_dir, timestamp, context,
                         use_stderr=True)
        sys.exit(128 + signum)
    return handler


# ---------------------------------------------------------------------------
#  CLI Argument Parsing
# ---------------------------------------------------------------------------

def build_parser():
    """
    Build and return the argparse.ArgumentParser.

    Returns:
        argparse.ArgumentParser: Configured parser with all CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description='QRadar Data Collector — collects, transforms, and '
                    'exports QRadar rule and log-source metadata for '
                    'migration analysis.',
    )

    # Connection arguments
    conn = parser.add_argument_group('Connection')
    conn.add_argument(
        '--host', default=None,
        help='QRadar console hostname or IP address',
    )
    conn.add_argument(
        '--api-version', default=None,
        help='Pin a specific QRadar REST API version (e.g. 26.0). '
             'Omitted by default — QRadar uses its latest.',
    )
    conn.add_argument(
        '--skip-ssl-verify', action='store_true', default=False,
        help='Disable SSL certificate verification '
             '(use when QRadar has a self-signed certificate)',
    )
    conn.add_argument(
        '--use-curl', action='store_true', default=False,
        help='Use curl for HTTP calls (Python 3 only; Python 2 always uses curl)',
    )

    # Output arguments
    out = parser.add_argument_group('Output')
    out.add_argument(
        '--output-dir', default='.',
        help='Directory for final CSV output files (default: current directory)',
    )
    out.add_argument(
        '--cache-dir', default=None,
        help='Path to previously collected data for offline replay (read-only)',
    )
    out.add_argument(
        '--log-sources', action='store_true', default=False,
        help='Generate standalone active log sources inventory CSV',
    )
    out.add_argument(
        '--active-days', type=int, default=7,
        help='Days of inactivity before a log source is excluded (default: 7)',
    )

    # Behaviour arguments
    behav = parser.add_argument_group('Behaviour')
    behav.add_argument(
        '--debug', action='store_true', default=False,
        help='Save collection data and log files as a debug ZIP archive on exit',
    )
    behav.add_argument(
        '--batch-size', type=int, default=None,
        help='Batch size for paginated API calls (default: auto-detected)',
    )

    return parser


def validate_args(args):
    """
    Post-parse validation. Exits with code 2 on failure.

    Args:
        args: argparse.Namespace from parse_args().
    """
    # ---- Null-byte rejection (paths) ----
    for attr, flag in (('output_dir', '--output-dir'),
                       ('cache_dir', '--cache-dir')):
        val = getattr(args, attr, None)
        if val and '\x00' in val:
            sys.stderr.write(
                'Error: {0} contains null bytes\n'.format(flag)
            )
            sys.exit(2)

    # ---- Path canonicalisation ----
    if args.output_dir:
        args.output_dir = os.path.realpath(args.output_dir)
    if args.cache_dir:
        args.cache_dir = os.path.realpath(args.cache_dir)

    # ---- Host normalisation and validation ----
    if args.host:
        original = args.host
        # Strip scheme prefix (case-insensitive)
        for scheme in ('https://', 'http://'):
            if args.host.lower().startswith(scheme):
                args.host = args.host[len(scheme):]
                break
        # Strip trailing slashes
        args.host = args.host.rstrip('/')
        if original != args.host:
            # Will be visible once logging is configured
            logging.getLogger(__name__).debug(
                "Stripped scheme/slashes from --host: using %r", args.host
            )
        # Null-byte check
        if '\x00' in args.host:
            sys.stderr.write('Error: --host contains null bytes\n')
            sys.exit(2)
        # Format validation: hostname, IPv4, or host:port only
        if not re.match(
            r'^[A-Za-z0-9]([A-Za-z0-9.\-]*[A-Za-z0-9])?(:\d+)?$', args.host
        ):
            sys.stderr.write(
                'Error: --host {0!r} is not a valid hostname or IP address. '
                'Provide a bare hostname (e.g. myhost.com) or IP '
                '(e.g. 10.1.2.3), with optional :port.\n'.format(args.host)
            )
            sys.exit(2)

    # Mutual exclusion: --host and --cache-dir cannot be combined
    if args.cache_dir and args.host:
        sys.stderr.write(
            'Error: --host cannot be used with --cache-dir '
            '(offline mode does not connect to a QRadar console)\n'
        )
        sys.exit(2)

    # Conditional requirement: --host unless --cache-dir
    if not args.cache_dir:
        if not args.host:
            sys.stderr.write(
                'Error: --host required (unless --cache-dir is provided)\n'
            )
            sys.exit(2)

    # ---- --api-version format check ----
    if args.api_version is not None:
        if not re.match(r'^\d+\.\d+$', args.api_version):
            sys.stderr.write(
                'Error: --api-version {0!r} must be a major.minor numeric '
                'pattern (e.g. 17.0, 26.0)\n'.format(args.api_version)
            )
            sys.exit(2)

    # --cache-dir validation: must exist and be a readable directory
    if args.cache_dir:
        if not os.path.isdir(args.cache_dir):
            sys.stderr.write(
                'Error: --cache-dir {0!r} is not an existing directory\n'.format(
                    args.cache_dir
                )
            )
            sys.exit(2)

    # --output-dir creation
    if args.output_dir and not os.path.isdir(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as exc:
            sys.stderr.write(
                'Error: cannot create --output-dir {0!r}: {1}\n'.format(
                    args.output_dir, exc
                )
            )
            sys.exit(2)

    # --output-dir write-permission check
    if args.output_dir and os.path.isdir(args.output_dir):
        if not os.access(args.output_dir, os.W_OK):
            sys.stderr.write(
                'Error: --output-dir {0!r} is not writable\n'.format(
                    args.output_dir
                )
            )
            sys.exit(2)

    # --active-days validation (1..3650)
    if args.active_days is not None:
        if args.active_days < 1 or args.active_days > 3650:
            sys.stderr.write(
                'Error: --active-days must be between 1 and 3650\n'
            )
            sys.exit(2)

    # --batch-size range check and auto-detection
    if args.batch_size is not None:
        if args.batch_size < 1 or args.batch_size > 10000:
            sys.stderr.write(
                'Error: --batch-size must be between 1 and 10000\n'
            )
            sys.exit(2)
    else:
        args.batch_size = 50 if PY2 else 1000


def main():
    """
    Entry point for the QRadar Data Collector pipeline.

    Returns:
        int: Exit code.
    """
    # Restrict file permissions to owner-only
    os.umask(0o077)

    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    # Acquire API token interactively when API connectivity is needed
    # Security: credentials never in CLI args
    if not args.cache_dir:
        sys.stderr.write(
            '\nThis script uses the QRadar API to collect SIEM migration data.\n'
            '\n'
            'To access this API you must create an authorized service token\n'
            'with admin privileges. See IBM QRadar documentation for details\n'
            'on creating and managing authorized service tokens.\n'
            '\n')
        if args.skip_ssl_verify:
            sys.stderr.write(
                'WARNING: SSL certificate verification is DISABLED.\n'
                'Your API token may be exposed to interception.\n')
            _get_input = getattr(__builtins__, 'raw_input', input)
            answer = _get_input('Do you want to proceed? [y/N] ')
            if answer.strip().lower() != 'y':
                sys.stderr.write('Aborted by user.\n')
                return 1
            sys.stderr.write('\n')
        if sys.stdin.isatty():
            args.token = getpass.getpass(
                'Please enter your authorized service token: ')
        else:
            args.token = sys.stdin.readline().strip()
    else:
        args.token = None

    # Capture timestamp once for consistent naming
    timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())

    # Create workspace folder
    workspace_path = create_workspace(timestamp)

    # Determine output directory (absolute path)
    output_dir = os.path.abspath(args.output_dir)

    # Create log path
    log_path = os.path.join(workspace_path, 'qradar_collector.log')

    # Configure logging
    formatter = setup_logging(log_path)

    # Log startup banner
    logger = logging.getLogger(__name__)
    logger.info('QRadar Data Collector v{0} starting'.format(VERSION))
    logger.info('Working directory: {0}'.format(workspace_path))
    logger.info('Output directory: {0}'.format(output_dir))
    logger.debug('Arguments: host={0!r}, token=*****, api_version={1!r}, '
                 'skip_ssl_verify={2}, use_curl={3}, output_dir={4!r}, '
                 'cache_dir={5!r}, debug={6}, batch_size={7}'.format(
                     args.host, args.api_version, args.skip_ssl_verify,
                     args.use_curl, args.output_dir, args.cache_dir,
                     args.debug, args.batch_size))
    logger.debug('Python version: {0}'.format('2.x' if PY2 else '3.x'))

    # Log API version strategy
    if args.api_version is not None:
        logger.info('Using user-specified API version: {0}'.format(
            args.api_version))
    else:
        logger.info('Using latest API version (no version header)')

    # Initialize context early (needed for signal handlers)
    context = PipelineContext(
        host=args.host,
        token=args.token,
        api_version=args.api_version,
        skip_ssl=args.skip_ssl_verify,
        use_curl=True if PY2 else args.use_curl,
        batch_size=args.batch_size,
        debug=args.debug,
        cache_dir=args.cache_dir,
        output_dir=output_dir,
        temp_dir=workspace_path,
        log_path=log_path,
        timestamp=timestamp,
        error_counter=ErrorCounter(),
        active_days=args.active_days,
        log_sources_flag=args.log_sources,
    )

    # Register signal handlers (always, for all exit paths)
    sig_handler = _make_signal_handler(workspace_path, output_dir, timestamp, context)
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    exit_code = 0

    try:
        # Create and run orchestrator
        orchestrator = PipelineOrchestrator(context, formatter)

        # Register handlers per architecture order
        if not args.cache_dir:
            orchestrator.register(InitHandler('Initialization', 0))
        orchestrator.register(UCMBaselineHandler('UCM Baseline Export', 1))
        orchestrator.register(MitreMappingHandler('MITRE Mappings', 2))
        orchestrator.register(ReferenceDataHandler('Reference Data Collection', 3))
        orchestrator.register(RuleIdHandler('Fetch Rule IDs', 4))
        orchestrator.register(RuleExportHandler('Rule Export', 5))
        orchestrator.register(CredentialCleanupHandler('Credential Cleanup', 5))
        orchestrator.register(XmlDecodeHandler('XML Decode', 6))
        orchestrator.register(ReferenceExtractionHandler('Reference Extraction', 7))
        orchestrator.register(DependencyExpansionHandler('Dependency Expansion', 8))
        orchestrator.register(UCMCSVExtensionHandler('UCM CSV Extension', 9))

        exit_code = orchestrator.execute()

    except Exception as exc:
        logger.error('Unhandled exception: {0}'.format(exc))
        exit_code = 1

    finally:
        # Handle cleanup based on flags
        formatter.set_phase('CLEANUP')
        _perform_cleanup(workspace_path, output_dir, timestamp, context)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
