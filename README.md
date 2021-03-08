# EC2 instances scheduled termination

This CloudFormation template creates Lambda function for scheduled terminating EC2 instances in the "stopped" state for
more than 30 days and for notifying in 7, 2, 1 days before termination via email with a warning message.

* Deployment of CloudFormation stack:

```
bash stack_mngmt.sh create
```

* Updating the stack:

```
bash stack_mngmt.sh update
```

* Uploading updated python lambda:

```
bash stack_mngmt.sh upload_python
```

* Deleting the stack:

```
bash stack_mngmt.sh delete
```

* Resources created by the stack:
    * Lambda function `ec2_termination_lambda_function` for scheduled terminating.
    * IAM role with appropriate policies for lambda function.
    * CloudWatch log group for `ec2_termination_lambda_function` function.
    * SNS Topic for warning emails sending. It is possible to add subscriptions by CF (there is example
      in `ec2_termination.yaml`), or they can be added manually in AWS console.
    * The scheduled event and invoke lambda permission for triggering `ec2_termination_lambda_function`
      every day at 10:00am.


* The termination counter can be reset by removing the `TerminateDate` tag of the EC2 instance in AWS Console.