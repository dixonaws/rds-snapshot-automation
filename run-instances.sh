#!/usr/bin/env bash
aws ec2 run-instances --image-id ami-b70554c8 --count 1 --instance-type t2.micro --key-name dixonaws --security-group-ids sg-28fe8e63 --subnet-id subnet-e8e4718d --iam-instance-profile Name=EC2Role_AdministratorAccess --user-data file://userdata.txt
