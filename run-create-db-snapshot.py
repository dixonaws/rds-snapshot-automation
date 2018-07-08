import boto3

def lambda_handler():
	ec2_client=boto3.client('ec2')

	str_user_data='''#!/bin/bash
	# install dependencies
	yum install -y git
	yum install -y python-pip
	yum install -y python3

	# download the latest rds-backup-automation program from github
	git clone https://github.com/dixonaws/rds-snapshot-automation /tmp/rds-snapshot-automation
	
	# install python dependencies
	pip3 install --user boto3
	pip3 install --user ec2_metadata

	# run the program (terminates the instance when finished)
	python3 /tmp/rds-snapshot-automation/create-db-snapshot.py hmi-poc		
	'''

	run_instances_response=ec2_client.run_instances(
		ImageId='ami-b70554c8',
		InstanceType='t2.micro',
		KeyName='dixonaws',
		SecurityGroupIds=[
			'sg-28fe8e63'
		],
		SubnetId='subnet-e8e4718d',
		UserData=str_user_data,
		IamInstanceProfile={
			'Name': 'EC2Role_AdministratorAccess'
		},
		TagSpecifications=[
			{
				'ResourceType': 'instance',
				'Tags': [
					{
						'Key': 'Name',
						'Value': 'rds-snapshot-automation'
					}
				]
			}
		],
		MaxCount=1,
		MinCount=1,
		DryRun=False
	)

	print(run_instances_response)

lambda_handler()