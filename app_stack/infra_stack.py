from aws_cdk import (
    core,
    aws_ec2,
    aws_rds,
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



