### rds-snapshot-automation
This program is meant to be run from a disposable EC2 instance, perhaps by launching an instance with userdata

userdata:
- install dependencies, minimally git
- clone rds-snapshot-automation repo
- install dependencies from requirements.txt
- run rds-snapshot-automation 

The instance terminates automatically once the script ends.
