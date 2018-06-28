import boto3
import time
from ec2_metadata import ec2_metadata

def logToCloudWatch(CloudWatchLogsClient, aMessage):
    # cloudwatchlogs expects unix time * 1000, otherwise throws TooOldLogEventsException
    intTime = int(time.time()) * 1000

    try:
        strInstanceId=ec2_metadata.instance_id
    except TimeoutError:
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
    print("Logging to CloudWatchLogs...")

    CloudWatchLogsClient = boto3.client('logs', region_name='us-east-1')

    response=logToCloudWatch(CloudWatchLogsClient, 'Started rds-snapshot-automation script')

    print(response)


main()
