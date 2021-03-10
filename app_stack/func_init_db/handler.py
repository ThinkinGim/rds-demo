import boto3
from botocore.exceptions import ClientError

import json
import os

def init(event, context):

    db_secret_name = os.environ.get('db_secret')

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        secret_response = client.get_secret_value(SecretId=db_secret_name)
    except ClientError as e:
        print(e.response)
        print(e.response['Error']['Code'])
    else:
        if 'SecretString' in secret_response:
            secret_data = json.loads(secret_response['SecretString'])
            print("##########################")
            print("host: %s"%secret_data['host'])
            print("user: %s"%secret_data['user'])

    return {
        'statusCode': 200,
    }