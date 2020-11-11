
from aws_cdk import (
    core,
    aws_ec2 as ec2
)

class VpcStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        rds_subnet = ec2.SubnetConfiguration(name="rds", subnet_type=ec2.SubnetType.ISOLATED, cidr_mask=24)

        self.vpc = ec2.Vpc (
            self, 'CDK_VPC',
    		cidr = "10.0.0.0/16",
            subnet_configuration=[rds_subnet],
            max_azs = 3,
    		nat_gateways = 0
		)

        self.security_group = ec2.SecurityGroup(
            self, "cdk_vpc_sg",
            vpc = self.vpc,
            allow_all_outbound = False
        )

        self.security_group.add_ingress_rule (
             ec2.Peer.prefix_list('pl-5aa44133'),
             ec2.Port.tcp(80)
        )

        subnetIso = self.vpc.select_subnets(
             subnet_type=ec2.SubnetType.ISOLATED
        )
        self.subnet_list = []
        for subnet in subnetIso.subnets:
        	self.subnet_list.append (subnet.subnet_id)