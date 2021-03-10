# AWS RDS AWSAuthenticationPlugin 사용하기
## 1. RDS 설정에서 iam_authentication 활성화
RDS Instance 혹은 Cluster Configuration 에서 IAM DB authentication = Enabled 인지 확인
- [aws-document link](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Enabling.html)
- [example cdk code](https://github.com/ThinkinGim/rds-demo/blob/main/app_stack/infra_stack.py#L67)

## 2. database user 생성
MySQL 에서:
```sql
CREATE USER IF NOT EXISTS 'db_uset_user'@'%' IDENTIFIED WITH AWSAuthenticationPlugin as 'RDS';
```
- [aws-document link](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.DBAccounts.html)
- [example cdk code](https://github.com/ThinkinGim/rds-demo/blob/main/app_stack/func_init_db/handler.py#L37)


## 3. iam role 생성
- iam role name 은 #2에서 생성된 데이터베이스의 user(db_uset_user) 와 같아야 함.
- 아래 코드블럭과 같은 "rds-db:connect" 정책이 정의되어 있어야 함
- [aws-document link](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.IAMPolicy.html)
- [example cdk code](https://github.com/ThinkinGim/rds-demo/blob/main/app_stack/infra_stack.py#L102-L132)
```json
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
             "rds-db:connect"
         ],
         "Resource": [
             "*"
         ]
      }
   ]
}
```

## 3. aws rds API 를 호출하여 db 접속에 사용할 임시 토큰 발급
```python
import sys
import boto3

ENDPOINT="mysqldb.123456789012.us-east-1.rds.amazonaws.com"
PORT="3306"
USR="jane_doe"
REGION="us-east-1"
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

#gets the credentials from .aws/credentials
session = boto3.Session(profile_name='RDSCreds')
client = session.client('rds')

token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USR, Region=REGION)     
```
- [aws-document link](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html)
- [example cdk code](https://github.com/ThinkinGim/rds-demo/blob/main/app_stack/func_test_db/handler.py#L24-L25)

## 3. 발급된 token 을 password 로 사용하여 db 접속
```python
token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USR, Region=REGION)

try:
    conn =  mysql.connector.connect(host=ENDPOINT, user=USR, passwd=token, port=PORT, database=DBNAME)
    cur = conn.cursor()
    cur.execute("""SELECT now()""")
    query_results = cur.fetchall()
    print(query_results)
except Exception as e:
    print("Database connection failed due to {}".format(e))  
```
- [aws-document link](https://docs.aws.amazon.com/ko_kr/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html)
- [example cdk code](https://github.com/ThinkinGim/rds-demo/blob/main/app_stack/func_test_db/handler.py#L32-L38)
