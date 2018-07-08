import boto3
from time import sleep


def main():
	
	strSnapshotId='jul72018'
	strDbInstanceId='hmi-poc'

	rds_client = boto3.client('rds')

	jsonResponseCreateDBSnapshot = ''

	try:
		jsonResponseCreateDBSnapshot = rds_client.create_db_snapshot(DBInstanceIdentifier=strDbInstanceId,
																	 DBSnapshotIdentifier=strSnapshotId)
	except Exception:
		print("Snapshot already exists, deleting... ")
		jsonDeleteDBSnapshot = rds_client.delete_db_snapshot(DBSnapshotIdentifier=strSnapshotId)

	print(jsonResponseCreateDBSnapshot)

	jsonDescribeDBSnapshots = rds_client.describe_db_snapshots(DBSnapshotIdentifier=strSnapshotId)
	strStatus = jsonDescribeDBSnapshots['DBSnapshots'][0]['Status']
	intPercentProgress = jsonDescribeDBSnapshots['DBSnapshots'][0]['PercentProgress']

	print("Snapshot status: " + strStatus)

	# poll the rds API for progress every 10 seconds
	while (intPercentProgress < 100 and strStatus == 'creating'):
		jsonDescribeDBSnapshots = rds_client.describe_db_snapshots(DBSnapshotIdentifier=strSnapshotId)

		print("Progress: " + str(intPercentProgress))

		intPercentProgress = jsonDescribeDBSnapshots['DBSnapshots'][0]['PercentProgress']
		strStatus = jsonDescribeDBSnapshots['DBSnapshots'][0]['Status']

		sleep(10)


main()
