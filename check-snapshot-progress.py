import boto3
from time import sleep
import time
import argparse
from botocore.exceptions import ClientError
import ec2_metadata


def logToCloudWatch(CloudWatchLogsClient, aLogGroupName, aLogStreamName, aMessage):
	# cloudwatchlogs expects unix time * 1000, otherwise throws TooOldLogEventsException
	intTime = int(time.time()) * 1000

	try:
		strInstanceId = ec2_metadata.instance_id
	except Exception:
		strInstanceId = "testing_non_ec2"
		pass

	# get the next token from CloudWatch so that we can put event in the log stream
	describe_log_streams_response = CloudWatchLogsClient.describe_log_streams(
		logGroupName='rds-snapshot-automation-logs'
	)

	# log to CloudWatch
	strMessage = strInstanceId + ': ' + aMessage

	# if we get a KeyError exception, this must be the first time we are logging to this log stream
	try:
		strNextToken = describe_log_streams_response['logStreams'][0]['uploadSequenceToken']
		print("using token=" + strNextToken)

		put_log_events_response = CloudWatchLogsClient.put_log_events(
			logGroupName=aLogGroupName,
			logStreamName=aLogStreamName,
			logEvents=[
				{
					'timestamp': intTime,
					'message': strMessage
				},
			],

			sequenceToken=strNextToken
		)

	except KeyError:
		put_log_events_response = CloudWatchLogsClient.put_log_events(
			logGroupName=aLogGroupName,
			logStreamName=aLogStreamName,
			logEvents=[
				{
					'timestamp': intTime,
					'message': strMessage
				}
			]
		)

	return (put_log_events_response)


def main():
	parser = argparse.ArgumentParser(
		description='Takes a snapshot of a given RDS instance and logs progress to a Cloudwatch stream called rds-snapshot-automation. The resulting snapshot-id will be a comination of the RDS Instance name and the current time (Unix epoch)')
	parser.add_argument('RdsDbInstanceId', help='The RDS instance to snapshot')
	args = parser.parse_args()

	strEpoch = str(int(time.time()))
	strDbInstanceId = args.RdsDbInstanceId
	strSnapshotId = strDbInstanceId + '-' + strEpoch
	strLogGroupName = "rds-snapshot-automation-logs"
	strLogStreamName = strDbInstanceId

	rds_client = boto3.client('rds')
	cloudwatch_client = boto3.client('logs')

	jsonResponseCreateDBSnapshot = ""

	print("Taking snapshot of instance: " + strDbInstanceId)
	print("Snapshot ID will be " + strSnapshotId)

	strMessage = "Taking snapshot of instance: " + strDbInstanceId + ", " + "Snapshot ID will be " + strSnapshotId
	logToCloudWatch(cloudwatch_client, strLogGroupName, strLogStreamName, strMessage)

	try:
		jsonResponseCreateDBSnapshot = rds_client.create_db_snapshot(DBInstanceIdentifier=strDbInstanceId,
																	 DBSnapshotIdentifier=strSnapshotId)
	except ClientError as e:
		print(e.response['Error']['Message'])

		exit(1)

	print(jsonResponseCreateDBSnapshot)

	jsonDescribeDBSnapshots = rds_client.describe_db_snapshots(DBSnapshotIdentifier=strSnapshotId)
	strStatus = jsonDescribeDBSnapshots['DBSnapshots'][0]['Status']
	intPercentProgress = jsonDescribeDBSnapshots['DBSnapshots'][0]['PercentProgress']

	print("Snapshot status: " + strStatus)

	# poll the rds API for progress every 10 seconds while the status is 'creating'
	# status will return 'available' when the snapshot is finished
	while (strStatus == 'creating'):
		jsonDescribeDBSnapshots = rds_client.describe_db_snapshots(DBSnapshotIdentifier=strSnapshotId)

		strMessage="Snapshot " + strSnapshotId + " - " + strStatus + ", progress: " + str(intPercentProgress)
		print(strMessage)
		logToCloudWatch(cloudwatch_client, strLogGroupName, strLogStreamName, strMessage)

		intPercentProgress = jsonDescribeDBSnapshots['DBSnapshots'][0]['PercentProgress']
		strStatus = jsonDescribeDBSnapshots['DBSnapshots'][0]['Status']

		sleep(10)

	# print a final message on completion
	strMessage="Snapshot " + strSnapshotId + " - " + strStatus + ", progress: " + str(intPercentProgress)
	print(strMessage)
	logToCloudWatch(cloudwatch_client, strLogGroupName, strLogStreamName, strMessage)

	# terminate the instance we're running on
	try:
		strInstanceId = ec2_metadata.instance_id
	except Exception:
		strInstanceId = "testing_non_ec2"
		pass

	Ec2Client = boto3.client('ec2', region_name='us-east-1')

	terminationResponse = Ec2Client.terminate_instances(
		InstanceIds=[
			strInstanceId,
		],
		DryRun=False
	)

	print(terminationResponse)

	strMessage="Terminated instance " + strInstanceId
	print(strMessage)
	logToCloudWatch(cloudwatch_client, strLogGroupName, strLogStreamName, strMessage)



main()
