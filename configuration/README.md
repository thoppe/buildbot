# Deploy notes
For an AWS instance


### Prerequisites

Locally, install the AWS CLI interface

     sudo apt-get install ec2-api-tools

From the AWS.IAM create an access key for yourself. Set the enviroment variables with the information from the keys:

     AWS_ACCESS_KEY="XXXXXXXXXXXXXXXXXXXX"
     AWS_SECRET_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
     AWS_VPC="XXXXXXXXXXXXXXXXXX"
     AWS_SUBNET="XXXXXXXXXXXXXXXXXX"
     
The `AWS_VPC` and `AWS_SUBNET` keys must be setup in the console for now.

### Setting up an instance

You should only need to do this once, or when you want to completely start over. First, build a valid keypair:

    fab create_keypair

This generates a file `AWS_buildbot.pem`, which should **not** be checked into the repo. Now create a security group and enable SSH permissions

    fab create_security_group

This creates a file named `buildbot_instance.group`, which tracks the security group name created. Spin up a EC2 instance by running  

     fab launch_EC2_instance

### Deploying BuildBot

