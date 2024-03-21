import gzip
import io
import json
from typing import List

import boto3
import botocore.client
import botocore.config


class Context:
    def __init__(self):
        self.file_downloads = 0
        self.api_calls = 0
        self.checkpoint = None

    def file_downloads_incr(self):
        self.file_downloads += 1

    def api_calls_incr(self):
        self.api_calls += 1


class S3Client:
    def __init__(self, bucket: str, access_key: str, secret_key: str, user_agent_extra: str, client: botocore.client.BaseClient = None,
                 context: Context = None):
        """
        S3Client provides a context manager for _S3Client.  Provides higher level methods for S3.

        :param bucket: S3 bucket
        :param access_key: aws access key
        :param secret_key: aws secret access key
        :param user_agent_extra: appends to user-agent
        :param client: optional boto3 client
        :param context: optional context for exporting metrics
        """
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.user_agent_extra = user_agent_extra
        self.client = client
        self.context = context

    def __enter__(self):
        self.client = _S3Client(self.bucket, self.access_key, self.secret_key, self.user_agent_extra, self.client, self.context)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        # older version of boto3 in splunk cloud doesn't have close() method.
        # self.client.client.close()


class _S3Client:
    S3_MAX_KEYS = 1000

    def __init__(self, bucket: str, access_key: str, secret_key: str, user_agent_extra: str, client, context: Context):
        self.bucket = bucket
        self.context = context or Context()
        if client is not None:
            self.client = client
        else:
            config = botocore.config.Config(user_agent_extra=user_agent_extra)
            self.client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, config=config)

    def fetch_common_prefixes(self, prefix: str) -> List[str]:
        """
        A generator function that yields common prefix found after the given prefix.

        :param prefix: s3 bucket key prefix
        """
        if not prefix.endswith('/'):
            prefix += '/'
        self.context.api_calls_incr()
        obj = self.client.list_objects_v2(
            Bucket=self.bucket,
            Delimiter="/",
            Prefix=prefix,
            MaxKeys=self.S3_MAX_KEYS
        )
        common_prefixes = obj.get('CommonPrefixes') or []
        for prefix in common_prefixes:
            yield prefix.get('Prefix')

        while obj.get('IsTruncated'):
            self.context.api_calls_incr()
            obj = self.client.list_objects_v2(
                Bucket=self.bucket,
                Delimiter="/",
                Prefix=prefix,
                ContinuationToken=obj.get('NextContinuationToken'),
                MaxKeys=self.S3_MAX_KEYS
            )
            common_prefixes = obj.get('CommonPrefixes') or []
            for prefix in common_prefixes:
                yield prefix.get('Prefix')

    def fetch_file_objects(self, prefix: str) -> List:
        """
        A generator method that yields file objects found after the given key prefix.

        :param prefix: s3 bucket key prefix
        """
        self.context.api_calls_incr()
        obj = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix,
            MaxKeys=self.S3_MAX_KEYS
        )
        contents = obj.get('Contents') or []
        for item in contents:
            yield item

        while obj.get('IsTruncated'):
            self.context.api_calls_incr()
            obj = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                ContinuationToken=obj.get('NextContinuationToken'),
                MaxKeys=self.S3_MAX_KEYS
            )
            contents = obj.get('Contents') or []
            for item in contents:
                yield item

    def fetch_gzipped_json_lines_file(self, key: str) -> List[dict]:
        """
        Downloads a gzipped file of `JSON Lines` format and converts it to Python.

        :param key: s3 key to a gzipped JSON Lines file
        :returns Contents of the file converted to Python
        """
        self.context.file_downloads_incr()
        datagz = io.BytesIO()
        self.client.download_fileobj(Bucket=self.bucket, Key=key, Fileobj=datagz)
        data = gzip.decompress(datagz.getvalue())
        return [json.loads(line) for line in data.splitlines(False)]
