"""
Make signed v4 requests to AWS.
"""
import logging

import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger(__name__)


class SigV4Request:
    """
    Class to make Signed V4 requests to AWS API gateways.
    """

    def __init__(self, access_key: str, secret_key: str, region: str = 'us-east-1'):
        """
        Initialize with AWS credentials.
        """

        self.region = region

        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

    def get(self, host: str, uri: str, **params):
        """
        Make a signed-v4 request to a host.
        """
        method = "GET"
        service = 'execute-api'

        url = f'https://{host}/{uri}'

        aws_request = AWSRequest(
            method,
            url,
            headers={'Host': host},
            params=params
        )

        SigV4Auth(self.session.get_credentials(), service, self.region).add_auth(aws_request)

        response = requests.request(method, url, headers=dict(aws_request.headers), data={}, timeout=60, params=params)
        response.raise_for_status()

        return response
