#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

cd $SCRIPTPATH

aws cloudformation create-stack \
--stack-name ec2_termination_stack \
--template-body file://ec2_termination.yaml \
--capabilities CAPABILITY_NAMED_IAM

zip ec2_termination.zip ec2_termination.py

aws lambda update-function-code --function-name ec2_termination_lambda_function --zip-file fileb://ec2_termination.zip

rm ec2_termination.zip

cd -