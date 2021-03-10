import os
import json
import mysql.connector
import boto3
from botocore.exceptions import ClientError

os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

# https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html
def init(event, context):
    db_secret_name = os.environ.get('db_secret')
    db_user = os.environ.get('db_user')

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

            rds_client = session.client('rds')
            token = rds_client.generate_db_auth_token(
                DBHostname=secret_data['host'], 
                Port=secret_data['port'], 
                DBUsername=db_user, 
                Region='ap-northeast-2'
            ) 
            
            print("Connecting [%s] with user(%s) using iam auth"%(secret_data['dbInstanceIdentifier'],db_user))
            print("host: %s"%secret_data['host'])
            print("port: %s"%secret_data['port'])
            print("token: %s"%token)

            conn =  mysql.connector.connect(
                host=secret_data['host'], 
                user=db_user, 
                passwd=token, 
                port=secret_data['port'],
                database='mysql')

            cursor = conn.cursor()
            cursor.execute("show grants;")
            result = cursor.fetchall()
            print(result)

    return {
        'statusCode': 200,
        'body': result
    }
