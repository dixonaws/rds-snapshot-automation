### rds-snapshot-automation
rds-snapshot-automation is a program that is designed to automate manual snapshots of AWS
RDS instances. This program is meant to be run from a disposable EC2 instance, perhaps 
by launching an instance with userdata from a scheduled Lambda function. The program takes the
RDS instances to backup as its only argument. 

files:<br>
<b>run-create-db-snapshot.py</b>: Python3 program that uses the Boto SDK to launch a new t2.micro instance
with userdata that follows the steps outlined below


userdata:
- install dependencies, minimally git
- clone rds-snapshot-automation repo
- install dependencies from requirements.txt
- run the rds-snapshot-automation 

The instance terminates automatically once the script ends.

<b>pre-requisities</b><br>
You'll need to create the following in order for this program to run properly in EC2:
- a log group and log stream in order to capture the output of the program
- an EC2 instance role that has permissions to ther RDS instance you want to snapshot, log to cloudwatch, and shutdown EC2 instances