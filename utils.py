from datetime import datetime, timedelta
from typing import List

from botocore.client import BaseClient


def get_cpu_usage(client: BaseClient, instance_id: str, period: int):
    return client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        StartTime=(datetime.now() - timedelta(seconds=period)).timestamp(),
        EndTime=datetime.now().timestamp(),
        Period=period,
        Statistics=[
            'Average',
        ],
        Unit='Percent'
    )


def met_shutdown_condition(expected_key: str, tags: List[dict]) -> bool:
    values_to_shutdown_server = ["True", "true", "yes", "Yes"]

    for tag in tags:
        if tag['Key'] == expected_key and tag['Value'] in values_to_shutdown_server:
            return True

    return False


def get_instance_name(instance) -> str:
    for tag in instance['Tags']:
        if tag['Key'] == 'Name':
            return tag['Value']

    return None
