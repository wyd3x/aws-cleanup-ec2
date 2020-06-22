import argparse
import boto3
from botocore.exceptions import ClientError

import config

from utils import met_shutdown_condition, get_cpu_usage, get_instance_name

parser = argparse.ArgumentParser(description='Kill unused ec2 instances.')
parser.add_argument('--period', metavar='period', type=int, nargs=1,
                    help='an integer for the period in seconds of inactive instance')
args = parser.parse_args()


PERIOD = args.period if args.period is not None else 3600  # default value, 1h

ec2 = boto3.client('ec2',
                   aws_access_key_id=config.ACCESS_KEY,
                   aws_secret_access_key=config.SECRET_KEY,
                   region_name=config.REGION)

cw = boto3.client('cloudwatch',
                  aws_access_key_id=config.ACCESS_KEY,
                  aws_secret_access_key=config.SECRET_KEY,
                  region_name=config.REGION)

deleted = []
stayed = []

response = ec2.describe_instances()
for reservation in response.get('Reservations'):
    for instance in reservation.get('Instances'):
        if met_shutdown_condition('Sleep', instance.get('Tags')):
            cpu_usage = get_cpu_usage(cw, instance['InstanceId'], PERIOD)
            if cpu_usage.get('Datapoints')[0].get('Average') < 30:
                deleted.append(instance)
            else:
                stayed.append(instance)
        else:
            stayed.append(instance)

print("Stopping instances:")
for delete in deleted:
    try:
        print(f"Instance {get_instance_name(delete)}({delete['InstanceId']}) should stop")
        # ec2.stop_instances(InstanceIds=[delete['InstanceId']], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' in str(e):
            # ec2.stop_instances(InstanceIds=[delete['InstanceId']], DryRun=False)
            print("Stopping", get_instance_name(delete), delete['InstanceId'])


print("Not stopping instances:")
for stay in stayed:
    print(get_instance_name(stay), stay['InstanceId'])
