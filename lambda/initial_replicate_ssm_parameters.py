import boto3
import botocore
from os import environ
import logging

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment Variables
targetRegion = environ.get('targetRegion')
if targetRegion == None:
    raise Exception('Environment variable "targetRegion" must be set')

# Boto3 Clients
ssmTarget = boto3.client('ssm', region_name=targetRegion)
ssmSource = boto3.client('ssm')
paginator = ssmSource.get_paginator('get_parameters_by_path')

def lambda_handler(event, context):
    logger.info('Full SSM cross-region replication initiated.')

    response_iterator = paginator.paginate(
        Path='/',
        Recursive=True
    )

    ssmValues = []

    for page in response_iterator:
        for entry in page['Parameters']:
            ssmValues.append(entry)

    ssmSize = len(ssmValues)
    ssmRange = range(ssmSize)
    logger.info('SSM Parameters that are being copied')
    logger.info(ssmValues)

    for x in ssmRange:
        try:
            ssmTarget.put_parameter(
                Name=ssmValues[x]['Name'],
                Type=ssmValues[x]['Type'],
                Value=ssmValues[x]['Value'],
                Overwrite=True
            )
            pass
        except botocore.exceptions.ClientError:
            ssmTarget.put_parameter(
                Name=ssmValues[x]['Name'],
                Type=ssmValues[x]['Type'],
                Value=ssmValues[x]['Value'],
                Tier='Advanced',
                Overwrite=True
            )
            pass

    logger.info('SSM Initial Transfer is Complete!')
