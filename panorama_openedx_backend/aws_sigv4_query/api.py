import os
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests


def get(access_key: str, secret_key: str, host: str, canonical_uri: str, region: str = 'us-east-1', params: dict = {}):

    service = 'execute-api'
    method = "GET"
    url = f'https://{host}{canonical_uri}'

    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    request = AWSRequest(
        method,
        url,
        headers={'Host': host},
        params=params
    )

    SigV4Auth(session.get_credentials(), service, region).add_auth(request)

    response = requests.request(method, url, headers=dict(request.headers), data={}, timeout=5, params=params)
    response.raise_for_status()

    return response
