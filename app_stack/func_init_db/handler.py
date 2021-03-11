import boto3
from botocore.exceptions import ClientError
import pymysql

import json
import os

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
            
            conn = pymysql.connect(
                user=secret_data['username'],
                passwd=secret_data['password'],
                host=secret_data['host'],
                db='mysql',
                charset='utf8'
            )

            cursor = conn.cursor()
            cursor.execute("CREATE USER IF NOT EXISTS %s IDENTIFIED WITH AWSAuthenticationPlugin as 'RDS';"%db_user)
            cursor.execute("grant select on mysql.* to '%s'@'%%';"%db_user)
            conn.commit()

            cursor.execute("select concat(user, ' has created with ', plugin, '.') from mysql.user where user='%s';"%db_user)
            result = cursor.fetchall()
            print(result)

            cursor.close()

    return {
        'statusCode': 200,
        'body': result
    }