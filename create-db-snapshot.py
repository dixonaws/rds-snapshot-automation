import boto3
import time


def main():
    print("Logging to CloudWatchLogs...")

	# cloudwatchlogs expects unix time * 1000, otherwise throws TooOldLogEventsException
    intTime = int(time.time())*1000

    CloudWatchLogsClient = boto3.client('logs', region_name='us-east-1')

    # get the next token from CloudWatch so that we can put event in the log stream
    response = CloudWatchLogsClient.describe_log_streams(
        logGroupName='rds-snapshot-automation-logs'
    )

    # print(response)

    strNextToken=response['logStreams'][0]['uploadSequenceToken']
    print("Token: " + strNextToken)

    # log to CloudWatch
    response = CloudWatchLogsClient.put_log_events(
        logGroupName='rds-snapshot-automation-logs',
        logStreamName='rds-instance',
        logEvents=[
            {
                'timestamp': intTime,
                'message': 'I logged!'
            },
        ],

        sequenceToken=strNextToken
    )

    print(response)


main()
