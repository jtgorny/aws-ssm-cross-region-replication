import argparse
import boto3
import botocore

parser = argparse.ArgumentParser(description='Copies existing SSMs from one Region to another')
parser.add_argument('-sp', '--sourceprofile', type=str, help='The AWS profile name the SSMs will be copied from.')
parser.add_argument('-tp', '--targetprofile', type=str, help='The AWS profile name the SSms will be copied to.')
parser.add_argument('-sr', '--sourceregion', type=str, help='The AWS region the SSMs will be copied from.')
parser.add_argument('-tr', '--targetregion', type=str, help='The AWS region the SSMs will be copied to.')
parser.add_argument('-p', '--path', type=str, help='The SSM path the perform a recursive copy over.')
args = parser.parse_args()

source = boto3.session.Session(region_name=args.sourceregion, profile_name=args.sourceprofile)
target = boto3.session.Session(region_name=args.targetregion, profile_name=args.targetprofile)
ssmPath = args.path

ssmSource = source.client('ssm')
ssmTarget = target.client('ssm')
paginator = ssmSource.get_paginator('get_parameters_by_path')


def main():
    print('Authored by @jtgorny')
    print('Beginning replication from "{0}" & "{1}" ~TO~ "{2}" & "{3}"'.format(
        source.profile_name, source.region_name, target.profile_name, target.region_name)
    )
    replicate()
    print('SSM Initial Transfer is Complete!')


def replicate():
    response_iterator = paginator.paginate(
        Path=ssmPath,
        Recursive=True
    )

    ssmValues = []

    for page in response_iterator:
        for entry in page['Parameters']:
            ssmValues.append(entry)

    # print(ssmValues)
    ssmSize = len(ssmValues)
    print('Copying {0} SSM parameters.'.format(ssmSize))
    ssmRange = range(ssmSize)
    # print(ssmRange)
    print('SSM Parameters that are being copied:')

    for x in ssmRange:
        print(ssmValues[x]['Name'])
        # print(ssmValues[x]['Type'])
        # print(ssmValues[x]['Value'])

        try:
            ssmTarget.put_parameter(
                Name=ssmValues[x]['Name'],
                Type=ssmValues[x]['Type'],
                Value=ssmValues[x]['Value'],
                Overwrite=True
            )
            pass
        except botocore.exceptions.ClientError:
            print('Advanced tiering required.')
            ssmTarget.put_parameter(
                Name=ssmValues[x]['Name'],
                Type=ssmValues[x]['Type'],
                Value=ssmValues[x]['Value'],
                Tier='Advanced',
                Overwrite=True
            )
            pass


main()
