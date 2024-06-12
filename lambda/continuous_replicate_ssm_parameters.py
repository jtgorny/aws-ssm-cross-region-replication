import boto3
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
ssmSource = boto3.client('ssm')
ssmTarget = boto3.client('ssm', region_name=targetRegion)

def lambda_handler(event, context):
    # logger.info("Authored by @gornyj")
    logger.info("SSM cross-region replication initiated.")
    logger.info(event['detail'])

    if event['detail']['eventName'] == 'PutParameter':
        parameterName = event['detail']['requestParameters']['name']
        parameterType = event['detail']['requestParameters']['type']
        try:
            parameterTier = event['detail']['requestParameters']['tier']
        except KeyError:
            parameterTier = 'Standard'
        ssmLimitExceeded = False
        logger.info('Replicating SSM "{0}" to region "{1}"'.format(parameterName, targetRegion))
        parameter = ssmSource.get_parameter(
            Name=parameterName
        )
        logger.info(parameter)
        parameterValue = parameter['Parameter']['Value']
        try:
            ssmTarget.put_parameter(
                Name=parameterName,
                Value=parameterValue,
                Type=parameterType,
                Tier=parameterTier,
                Overwrite=True
            )
        except ssmTarget.exceptions.ParameterLimitExceeded:
            logger.info("SSM limit exceeded. Cleanup required.")
            ssmLimitExceeded = True
        if ssmLimitExceeded:
            raise Exception('Cannot replicate SSM, request service limit increase or cleanup unused secrets')
        else:
            logger.info('SSM {0} replicated successfully to region "{1}"'.format(parameterName, targetRegion))
    else:
        logger.info('No action necessary')
