from aws_cdk import (
    core,
    aws_ec2,
    aws_rds,
    aws_lambda,
    aws_iam,
)

class InfraStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        demo_vpc = aws_ec2.Vpc(self, "network",
            cidr="10.10.0.0/16",
            max_azs=2,
            subnet_configuration=[]
        )

        demo_subnets=[]
        demo_subnets.append(
            aws_ec2.Subnet(self, 'sbn-demo-1',
                availability_zone=demo_vpc.availability_zones[0],
                vpc_id=demo_vpc.vpc_id,
                cidr_block='10.10.0.0/25'
            )
        )
        demo_subnets.append(
            aws_ec2.Subnet(self, 'sbn-demo-2',
                availability_zone=demo_vpc.availability_zones[1],
                vpc_id=demo_vpc.vpc_id,
                cidr_block='10.10.0.128/25'
            )
        )

        demo_vpc.add_interface_endpoint('secretmanager',
            service=aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            subnets=aws_ec2.SubnetSelection(subnets=demo_subnets)
        )

        db_subnet_group = aws_rds.SubnetGroup(self, 'sbng-demo-rds',
            description='demo db subnet group',
            vpc=demo_vpc,
            removal_policy=core.RemovalPolicy.DESTROY,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=demo_subnets)
        )

        db_security_group = aws_ec2.SecurityGroup(self, 'sg-demo-rds',
            vpc=demo_vpc
        )

        db_security_group.add_ingress_rule(
            peer=aws_ec2.Peer.ipv4('10.10.0.0/16'),
            connection=aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="to allow from the vpc internal",
                from_port=3306,
                to_port=3306
            )
        )

        mysql_instance=aws_rds.DatabaseInstance(self, 'mys-demo-rds',
            engine=aws_rds.DatabaseInstanceEngine.MYSQL,
            vpc=demo_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=demo_subnets),
            security_groups=[db_security_group],
            iam_authentication=True
        )

        db_secret = mysql_instance.secret

        role_init_db = aws_iam.Role(self, 'cmd_role_init_src_db',
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com")
        )

        lambda_base_policy_statement = aws_iam.PolicyStatement(
            resources=['*'],
            actions=[
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents',
                "ec2:CreateNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
            ]
        )

        role_init_db.add_to_policy(lambda_base_policy_statement)

        role_init_db.add_to_policy(
            aws_iam.PolicyStatement(
                resources=[db_secret.secret_arn],
                actions=[
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:ListSecretVersionIds"
                ]
            )
        )

        db_user = 'db_test_user'

        func_init_db = aws_lambda.Function(self, 'func_init_db',
            function_name='demo-rds_func_init_db',
            handler='handler.init',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset('./app_stack/func_init_db'),
            role=role_init_db,
            timeout=core.Duration.seconds(10),
            allow_public_subnet=False,
            vpc=demo_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=demo_subnets),
            environment={
                'db_secret': db_secret.secret_name,
                'db_user': db_user
            }
        )

        # When the role_name specified as static value, it could be occurring with KMS related exception.
        # It's because re-created lambda function with static name of role would be refer to the role which is not exsisted.
        # https://github.com/serverless/examples/issues/279
        role_test_db = aws_iam.Role(self, 'demo_role_test_db',
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=db_user
        )
        role_test_db.add_to_policy(lambda_base_policy_statement)
        role_test_db.add_to_policy(
            aws_iam.PolicyStatement(
                resources=['*'],
                actions=[
                    "rds-db:connect",
                ]
            )
        )

        role_test_db.add_to_policy(
            aws_iam.PolicyStatement(
                resources=[db_secret.secret_arn],
                actions=[
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:ListSecretVersionIds"
                ]
            )
        )

        func_test_db = aws_lambda.Function(self, 'func_test_db',
            function_name='demo-rds_test_iam_auth',
            handler='handler.init',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            code=aws_lambda.Code.asset('./app_stack/func_test_db'),
            role=role_test_db,
            timeout=core.Duration.seconds(10),
            allow_public_subnet=False,
            vpc=demo_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=demo_subnets),
            environment={
                'db_secret': db_secret.secret_name,
                'db_user': db_user
            }
        )


