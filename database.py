import boto3

db_name = 'kctc_db'
db_cluster_param = 'kctc_db_cluster_arn'
db_secret_param = 'kctc_db_secret_arn'

ssm_client = boto3.client('ssm')
cluster_arn = ssm_client.get_parameter(Name=db_cluster_param)
secret_arn = ssm_client.get_parameter(Name=db_secret_param)

rdsData = boto3.client('rds-data')
response = rdsData.execute_statement(
    resourceArn = cluster_arn['Parameter']['Value'], 
    secretArn = secret_arn['Parameter']['Value'],
    database = db_name, 
    sql = 'CREATE TABLE Customer (id INT, loyalty_number INT);')

