from app.utils import random_data_utils


def test_random_name():
    first, last = random_data_utils.random_name()
    assert first in random_data_utils.first_list
    assert last in random_data_utils.last_list


def test_random_email():
    username = "username"
    email = random_data_utils.random_email(username)
    assert username in email


def test_random_username():
    first, last = random_data_utils.random_name()
    username = random_data_utils.random_username(first, last)
    assert first in username
    assert last in username
