import boto3
import os
import re
from datetime import date, datetime, timedelta

date_regex    = "([0-9]{4}-[0-9]{2}-[0-9]{2})"
date_format   = "%Y-%m-%d"
current_date  = date.today()
days_delta    = timedelta(days = int(os.environ.get('DAYS_DELTA')))
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
sns_client    = boto3.client('sns')
ec2           = boto3.client('ec2')


def lambda_handler(event, context):
    ec2_termination()


def ec2_termination():
    response     = ec2.describe_instances()
    reservations = response['Reservations']
    for reservation in reservations:
        instances = reservation['Instances']
        for instance in instances:
            instance_id      = instance['InstanceId']
            instance_state   = instance['State']['Name']
            termination_attr = get_termination_attr(instance)
            termination_tag  = get_termination_tag(instance)
            tag_action       = get_tag_action(instance_state, termination_tag, termination_attr)
            termination_date = get_termination_date(tag_action, termination_tag)
            days_left        = get_days_left(termination_date)
            instance_action  = get_instance_action(days_left)
        
            if tag_action or instance_action:
                print("InstanceID: " + instance_id)
                print("Instance state: " + instance_state)
                if tag_action == "add" or tag_action == "update":
                    add_tag(instance_id, termination_date)
                elif tag_action == "delete":
                    delete_tag(instance_id)
                if instance_action == "email":
                    send_email(days_left, termination_date, instance_id)
                elif instance_action == "terminate":
                    terminate_instance(instance_id)
                print("\n")


def get_termination_attr(instance):
    termination_attr = None
    stopped_reason   = instance['StateTransitionReason']
    try:
        stopped_date_re  = re.findall(date_regex, stopped_reason)[0]
        stopped_date     = datetime.strptime(stopped_date_re, date_format).date()
        termination_attr = stopped_date + days_delta
    except:
        pass
    return termination_attr


def get_termination_tag(instance):
    termination_date_tag = None
    for tag in instance['Tags']:
        if tag['Key'] == "TerminationDate":
            try:
                termination_date_tag = datetime.strptime(tag['Value'], date_format).date()
            except:
                pass
    return termination_date_tag


def get_tag_action(instance_state, termination_tag, termination_attr):
    tag_action = None
    if instance_state == "stopped":
        if not termination_tag:
            tag_action = "add"
        elif termination_attr and termination_attr >= termination_tag:
            tag_action = "update"
    elif termination_tag:
        tag_action = "delete"
    return tag_action


def get_termination_date(tag_action, termination_tag):
    if tag_action == "add" or tag_action == "update":
        termination_date = current_date + days_delta
    else:
        termination_date = termination_tag
    return termination_date


def get_days_left(termination_date):
    days_left = None
    if termination_date:
        days_left = termination_date - current_date
        days_left = days_left.days
    return days_left


def get_instance_action(days_left):
    instance_action = None
    if days_left == 1 or days_left == 2 or days_left == 7:
        instance_action = "email"
    elif days_left == 0:
        instance_action = "terminate"
    return instance_action


def add_tag(instance_id, termination_date):
    ec2.create_tags(
        Resources = [
            instance_id
        ],
        Tags = [
            {
                'Key'  : 'TerminationDate',
                'Value': termination_date.isoformat()
            }
        ]
    )
    print("TerminationDate=" + termination_date.isoformat() + " tag for instance " + instance_id + " was added")
    

def delete_tag(instance_id):
    ec2.delete_tags(
        Resources = [
            instance_id
        ],
        Tags = [
            {
                'Key': 'TerminationDate'
            }
        ]
    )
    print("TerminationDate tag for instance " + instance_id + " was removed")


def send_email(days_left, termination_date, instance_id):
    result = sns_client.publish(
        TopicArn = sns_topic_arn,
        Subject = "WARNING!!! Instance " + instance_id + " will be terminated after " + str(days_left) + " day(s)",
        Message = "Instance " + instance_id + " will be terminated after " + str(days_left) + " day(s)\n" +
                  "Termination date: " + termination_date.isoformat()
    )
    if int(result['ResponseMetadata']['HTTPStatusCode']) == 200:
        print("Instance " + instance_id + " will be terminated on " + termination_date.isoformat())
        print("Warning message for instance " + instance_id + " is sent")
    else:
        print("Warning message for instance " + instance_id + " is not sent")


def terminate_instance(instance_id):
    result = ec2.terminate_instances(
        InstanceIds = [
            instance_id
        ]
    )
    if int(result['ResponseMetadata']['HTTPStatusCode']) == 200:
        print("Instance " + instance_id + " is terminated")
    else:
        print("Instance " + instance_id + " is not terminated")
