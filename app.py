#!/usr/bin/env python3

import boto3
from botocore.exceptions import ClientError
import json
from aws_cdk import (
    core
)

from pipeline_stack.cdk_pipeline_stack import CdkPipelineStack as pipeline

app = core.App()
secret_name = app.node.try_get_context("secret_name")
region = app.node.try_get_context("region")

session = boto3.session.Session()
client = session.client(service_name='secretsmanager', region_name=region)

try:
    response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    print(e.response['Error']['Code'])
else:
    pipeline_config = json.loads(response['SecretString'])
    pipeline_config['region'] = region
    pipeline_config['secret_name'] = secret_name
    pipeline_config['secret_arn'] = response['ARN']

    pipeline(app, pipeline_config['stack_name'], params=pipeline_config)

    app.synth()
