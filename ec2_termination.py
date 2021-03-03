import boto3
import os
import re
from datetime import date, datetime, timedelta

def lambda_handler(event, context):
  current_date = date.today()
  days_delta   = int(os.environ.get('DAYS_DELTA'))
  ec2          = boto3.client('ec2')
  response     = ec2.describe_instances()
  reservations = response['Reservations']
  for reservation in reservations:
    instances = reservation['Instances']
    for instance in instances:
      instance_id          = instance['InstanceId']
      instance_state       = instance['State']['Name']
      termination_date_tag = None

      for tag in instance['Tags']:
        if tag['Key'] == "TerminationDate":
          termination_date_tag = datetime.strptime(tag['Value'], '%Y-%m-%d').date()

      if instance_state == "stopped" or termination_date_tag:
        print("InstanceID: " + instance_id)
        print("Instance state: " + instance_state)
        if instance_state == "stopped":
          stopped_reason   = instance['StateTransitionReason']
          stopped_date_re  = re.findall("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", stopped_reason)[0]
          stopped_date     = datetime.strptime(stopped_date_re, '%Y-%m-%d').date()
          termination_attr = stopped_date + timedelta(days=days_delta)
          if not termination_date_tag or termination_attr >= termination_date_tag:
            termination_date = current_date + timedelta(days=days_delta)
            ec2.create_tags(
              Resources=[
                instance_id
              ],
              Tags=[
                {
                  'Key': 'TerminationDate',
                  'Value': termination_date.isoformat()
                }
              ]
            )
          else:
            termination_date = termination_date_tag
          print("Instance " + instance_id + " will be terminated on " + termination_date.isoformat())

          if current_date == termination_date - timedelta(days=1):
            send_warn_email(1, termination_date, instance_id)
          elif current_date == termination_date - timedelta(days=2):
            send_warn_email(2, termination_date, instance_id)
          elif current_date == termination_date - timedelta(days=7):
            send_warn_email(7, termination_date, instance_id)
          elif current_date >= termination_date:
            ec2.terminate_instances(
              InstanceIds=[
                instance_id
              ]
            )
            print("Instance " + instance_id + " is terminated")
        elif termination_date_tag:
          ec2.delete_tags(
            Resources=[
              instance_id
            ],
            Tags=[
              {
                'Key': 'TerminationDate'
              }
            ]
          )
          print("TerminationDate tag was removed for instance " + instance_id)
        print("\n")

def send_warn_email(days_left, termination_date, instance_id):
  sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
  sns_client    = boto3.client('sns')
  sns_client.publish(
      TopicArn = sns_topic_arn,
      Subject  = "WARNING!!! Intance " + instance_id + " will be termnated after " + str(days_left) + " day(s)",
      Message  = "Intance " + instance_id + " will be termnated after " + str(days_left) + " day(s)\n" +
                 "Termination date: " + termination_date.isoformat()
  )
  print("Warning message for instance " + instance_id + " is sent")