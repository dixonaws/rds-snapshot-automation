import boto3

def main():
	print("Logging to CloudWatchLogs...!")

	CloudWatchLogsClient=boto3.client('logs')

	response=CloudWatchLogsClient.put_log_events(
		logGroupName='rds-snapshot-automation-logs',
		logStreamName='rds-instance',
		logEvents=[
			'timestamp': 123,
			'message': 'I logged!'
		],

	sequenceToken=''


main()
