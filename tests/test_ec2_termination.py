import pytest
import json
from module.ec2_termination import *

with open('tests/json/test_instance.json') as json_file:
    instance = json.load(json_file)

with open('tests/json/test_instance_wrong.json') as json_file:
    instance_wrong = json.load(json_file)

with open('tests/json/test_instance_wrong.json') as json_file:
    instance_empty = json.load(json_file)


@pytest.fixture
def mock_env_days_delta(monkeypatch):
    monkeypatch.setenv('DAYS_DELTA', '30')


@pytest.fixture
def mock_env_topic_arn(monkeypatch):
    monkeypatch.setenv('SNS_TOPIC_ARN', 'arn')


def test_get_days_delta(mock_env_days_delta):
    response = get_days_delta()
    assert response == timedelta(days = 30)


def test_get_days_delta_empty():
    with pytest.raises(TypeError):
        get_days_delta()


def test_get_topic_arn(mock_env_topic_arn):
    response = get_topic_arn()
    assert response


def test_get_topic_arn_empty():
    with pytest.raises(ValueError):
        get_topic_arn()


def test_get_termination_attr():
    response = get_termination_attr(instance = instance,
                                    days_delta = timedelta(days = 30))
    assert response == date(2021, 4, 7)


def test_get_wrong_termination_attr():
    response = get_termination_attr(instance = instance_wrong,
                                    days_delta = timedelta(days = 30))
    assert not response


def test_get_empty_termination_attr():
    response = get_termination_attr(instance = instance_empty,
                                    days_delta = timedelta(days = 30))
    assert not response


def test_get_termination_tag():
    response = get_termination_tag(instance = instance)
    assert response == date(2021, 4, 7)


def test_get_wrong_termination_tag():
    response = get_termination_tag(instance = instance_wrong)
    assert not response


def test_get_empty_termination_tag():
    response = get_termination_tag(instance = instance_empty)
    assert not response


def test_get_tag_action_stopped_1():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = date(2021, 4, 7))
    assert not response


def test_get_tag_action_stopped_2():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = date(2021, 4, 8))
    assert response == "update"


def test_get_tag_action_stopped_3():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = date(2021, 4, 8),
                              termination_attr = date(2021, 4, 7))
    assert not response


def test_get_tag_action_stopped_4():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = None,
                              termination_attr = date(2021, 4, 7))
    assert response == "add"


def test_get_tag_action_stopped_5():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = None,
                              termination_attr = None)
    assert response == "add"


def test_get_tag_action_stopped_6():
    response = get_tag_action(instance_state   = "stopped",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = None)
    assert not response


def test_get_tag_action_other_1():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = date(2021, 4, 7))
    assert response == "delete"


def test_get_tag_action_other_2():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = date(2021, 4, 8))
    assert response == "delete"


def test_get_tag_action_other_3():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = date(2021, 4, 8),
                              termination_attr = date(2021, 4, 7))
    assert response == "delete"


def test_get_tag_action_other_4():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = None,
                              termination_attr = date(2021, 4, 7))
    assert not response


def test_get_tag_action_other_5():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = None,
                              termination_attr = None)
    assert not response


def test_get_tag_action_other_6():
    response = get_tag_action(instance_state   = "other",
                              termination_tag  = date(2021, 4, 7),
                              termination_attr = None)
    assert response == "delete"


def test_get_termination_date_none():
    response = get_termination_date(tag_action      = None,
                                    current_date    = date(2021, 4, 6),
                                    days_delta      = timedelta(days = 30),
                                    termination_tag = date(2021, 4, 7))
    assert response == date(2021, 4, 7)


def test_get_termination_date_update():
    response = get_termination_date(tag_action      = "update",
                                    current_date    = date(2021, 4, 6),
                                    days_delta      = timedelta(days = 30),
                                    termination_tag = date(2021, 4, 7))
    assert response == date(2021, 5, 6)


def test_get_termination_date_add():
    response = get_termination_date(tag_action      = "add",
                                    current_date    = date(2021, 4, 6),
                                    days_delta      = timedelta(days = 30),
                                    termination_tag = date(2021, 4, 7))
    assert response == date(2021, 5, 6)


def test_get_days_left():
    response = get_days_left(current_date = date(2021, 3, 8), termination_date = date(2021, 3, 10))
    assert response == 2


def test_get_instance_action_1day():
    response = get_instance_action(days_left = 1)
    assert response == "email"


def test_get_instance_action_2days():
    response = get_instance_action(days_left = 2)
    assert response == "email"


def test_get_instance_action_7days():
    response = get_instance_action(days_left = 7)
    assert response == "email"


def test_get_instance_action_0days():
    response = get_instance_action(days_left = 0)
    assert response == "terminate"


def test_get_instance_action_negative_days():
    response = get_instance_action(days_left = -1)
    assert response == "terminate"
