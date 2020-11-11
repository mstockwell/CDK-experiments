from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_secretsmanager as sm,
    aws_ssm as ssm,
    aws_rds as rds,
) 

class DatabaseStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, secret_param, db_param, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        secret = rds.DatabaseSecret(self,id="MasterUserSecret",username='xxxxxxxx')
        ssm.StringParameter(self, "Secrete_Parameter", parameter_name=secret_param, string_value= secret.secret_arn)

        dbSubnetGroup = rds.CfnDBSubnetGroup (self, 'AuroraSubnetGroup',
        	db_subnet_group_description = 'Subnet group to access aurora',
        	subnet_ids = vpc.subnet_list,
        	db_subnet_group_name = 'aurora-subnet-group'
        	)

        self.aurora_serverless = rds.CfnDBCluster(self, 'Serverless DB',
            master_username=secret.secret_value_from_json("username").to_string(),
            master_user_password=secret.secret_value_from_json("password").to_string(),
        	engine = 'aurora',
            engine_mode = 'serverless',
            enable_http_endpoint = True,
            db_subnet_group_name = dbSubnetGroup.db_subnet_group_name,
            port = 3306,
            vpc_security_group_ids = [vpc.security_group.security_group_id],
            scaling_configuration=rds.CfnDBCluster.ScalingConfigurationProperty(
                auto_pause=True,
                min_capacity=1,
                max_capacity=2,
                seconds_until_auto_pause=300
            )
        )
        self.aurora_serverless.node.add_dependency(dbSubnetGroup)
        self.aurora_serverless.node.add_dependency(vpc.security_group)

        secret_attached = sm.CfnSecretTargetAttachment(
            self,
            id="secret_attachment",
            secret_id=secret.secret_arn,
            target_id=self.aurora_serverless.ref,
            target_type="AWS::RDS::DBCluster",
        )
        secret_attached.node.add_dependency(self.aurora_serverless)

        cluster_arn= "arn:aws:rds:{}:{}:cluster:{}".format(self.region,self.account,self.aurora_serverless.ref)
        ssm.StringParameter(self, "Database_Parameter", parameter_name=db_param, string_value= cluster_arn)