"""
Script to randomly stop an instance within a particular VPC
If the instance has the proper tags
Restarts the instances after specific duration
"""
import argparse
import logging
import boto3
import random
import time

from pythonjsonlogger import jsonlogger


def setup_logging(log_level):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    json_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    json_handler.setFormatter(formatter)
    logger.addHandler(json_handler)


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Script to randomly stop instance in AZ filtered by tag',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--log-level', type=str, default='INFO',
                        help='Python log level. INFO, DEBUG, etc.')
    parser.add_argument('--region', type=str, required=True,
                        help='The AWS region of choice')
    parser.add_argument('--az-name', type=str, default='eu-west-3a',
                        help='The name of the availability zone to blackout')
    parser.add_argument('--tag', type=str, default='SSMTag:chaos-ready',
                        help='Filter instances by tag name:value')
    parser.add_argument('--duration', type=int,
                        help='Duration, in seconds, before restarting the instance')
    parser.add_argument('--profile', type=str, default='default',
                        help='AWS credential profile to use')

    return parser.parse_args()


def stop_random_instance(ec2_client, az_name, tag):
    logger = logging.getLogger(__name__)
    paginator = ec2_client.get_paginator('describe_instances')
    pages = paginator.paginate(
        Filters=[
            {
                "Name": "availability-zone",
                "Values": [
                    az_name
                ]
            },
            {
                "Name": "tag:" + tag.split(':')[0],
                "Values": [
                    tag.split(':')[1]
                ]
            },
            {
                "Name": "instance-state-name",
                "Values": [
                    "running"
                ]
            }
        ]
    )
    instance_list = []
    for page in pages:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                instance_list.append(instance['InstanceId'])
    logger.info("Going to stop ANY of these instance %s ", instance_list)
    if len(instance_list) > 0:
        selected_instance = random.choice(instance_list)
        logger.info("Randomly selected %s", selected_instance)
        ec2_client.stop_instances(
            InstanceIds=[selected_instance]
        )
        return selected_instance
    else:
        logger.info(
            "No instance in running state in %s with tag %s",
            az_name, tag)


def rollback(ec2_client, instance_id):
    logger = logging.getLogger(__name__)
    logger.info('Restarting the instance %s', instance_id)
    ec2_client.start_instances(
            InstanceIds=[instance_id]
    )


<<<<<<< HEAD
def run(region, az_name, tag_name, tag_value, duration, log_level='INFO', profile='default'):
=======
def run(region, az_name, tag, duration, log_level='INFO'):
>>>>>>> upstream/master
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info('Setting up ec2 client for region %s ', region)
    session = boto3.Session(profile_name=profile)
    ec2_client = session.client('ec2', region_name=region)
    instance_id = stop_random_instance(
        ec2_client, az_name, tag)

    if instance_id and duration:
        time.sleep(duration)
    else:
        input("Press Enter to rollback...")
    rollback(ec2_client, instance_id)


def entry_point():
    args = get_arguments()
    run(
        args.region,
        args.az_name,
        args.tag,
        args.duration,
        args.log_level,
        args.profile
    )


if __name__ == '__main__':
    entry_point()
