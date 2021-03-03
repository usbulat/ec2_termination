# EC2 instances scheduled termination
This CloudFormation template creates Lambda function for scheduled terminating EC2 instances in the "stopped" state for more than 30 days and for notifying in 7, 2, 1 days before termination via email with a warning message.

* Deployment of CloudFormation stack:
```
bash stack_mngmt.sh create
```
* Updating the stack:
```
bash stack_mngmt.sh update
```
* Deleting the stack:
```
bash stack_mngmt.sh delete
```

* Resources created by stack:
  * Lambda function for scheduled terminating `ec2_termination_lambda_function`.
  * IAM role with appropriate policies for lambda function.
  * SNS Topic will for warning emails sending. It is possible to add subscriptions by CF (there is example in `ec2_termination.yaml`) or they can be added manually in AWS console.
  * Scheduled event and invoke lambda permission will be created for triggering `ec2_termination_lambda_function` every day at 10:00am.