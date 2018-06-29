import boto3
import time
from ec2_metadata import ec2_metadata

def logToCloudWatch(CloudWatchLogsClient, aMessage):
    # cloudwatchlogs expects unix time * 1000, otherwise throws TooOldLogEventsException
    intTime = int(time.time()) * 1000

    try:
        strInstanceId=ec2_metadata.instance_id
    except Exception:
        strInstanceId="testing_non_ec2"
        pass

    # get the next token from CloudWatch so that we can put event in the log stream
    response = CloudWatchLogsClient.describe_log_streams(
        logGroupName='rds-snapshot-automation-logs'
    )

    strNextToken = response['logStreams'][0]['uploadSequenceToken']

    # log to CloudWatch
    strMessage = strInstanceId + ': ' + aMessage

    response = CloudWatchLogsClient.put_log_events(
        logGroupName='rds-snapshot-automation-logs',
        logStreamName='rds-instance',
        logEvents=[
            {
                'timestamp': intTime,
                'message': strMessage
            },
        ],

        sequenceToken=strNextToken
    )

    return(response)


def main():
    # todo: parse command line arguments from userdata

    print("rds-snapshot-automation, v1.0")

    CloudWatchLogsClient = boto3.client('logs', region_name='us-east-1')

    # log when we start the script
    logToCloudWatch(CloudWatchLogsClient, 'Started rds-snapshot-automation script')

    # todo: create an RDS snapshot of specified instances

    # log when we're finished
    logToCloudWatch(CloudWatchLogsClient, 'rds-snapshot-automation script ended, terminating instance...')

    # terminate the instance we're running on
    try:
        strInstanceId=ec2_metadata.instance_id
    except Exception:
        strInstanceId="testing_non_ec2"
        pass

    Ec2Client=boto3.client('ec2', region_name='us-east-1')

    terminationResponse = Ec2Client.terminate_instances(
        InstanceIds=[
            strInstanceId,
        ],
        DryRun=False
    )

    print(terminationResponse)


main()
