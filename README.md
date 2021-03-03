# EC2 instances scheduled termination
This CloudFormation template creates Lambda function for terminating EC2 instances in the "stopped" state for more than 30 days and for notifying in 7, 2, 1 days before termination via email with a warning message.

It also creates Lambda function for restarting the termination counter manually.

* Deployment of CloudFormation stack:
```
bash stack_deploy.sh
```
* Updating the stack:
```
bash stack_update.sh
```
* Deleting the stack:
```
aws cloudformation delete-stack \
--stack-name ec2_termination_stack
```
* Resources created by stack:
  * Two lambda functions `ec2_termination_lambda_function` and `ec2_termination_reset_lambda_function` will be created. First is for scheduled deleting of EC2 instances stopped for 30 days (can be changed in DAYS_DELTA env variable). Second is for manual resetting the counter of stopped instance.
  * IAM roles with appropriate policies will be created for each lambda function.
  * DynamoDB stopped_instances table will be created, which stores Instance IDs and stop date of each instance.
  * SNS Topic will be created for warning emails sending. It is possible to add subscriptions by CF (there is example in `ec2_termination.yaml`) or they can be added manually in AWS console.
  * Scheduled event and invoke lambda permission will be created for triggering `ec2_termination_lambda_function` every day at 10:00am. 

* To run `ec2_termination_reset_lambda_function` function for specific instance - `instance` parameter should be passed:
```
{
  "instance": "instance-id"
}
```