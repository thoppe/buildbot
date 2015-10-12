# Deploy notes
For an AWS instance


### Prerequisites

Locally, install the AWS CLI interface

     sudo apt-get install ec2-api-tools

From the AWS.IAM create an access key for yourself. Set the enviroment variables with the information from the keys:

     AWS_ACCESS_KEY="XXXXXXXXXXXXXXXXXXXX"
     AWS_SECRET_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

### Setting up an instance

You should only need to do this once, or when you want to completely start over. First, build a valid keypair:

    fab create_keypair

This generates a file `AWS_buildbot.pem`, which should **not** be checked into the repo.

