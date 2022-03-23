from app.utils.random_data_utils import *

def test_random_name():
    first, last = random_name()
    assert first in first_list
    assert last in last_list


def test_random_email():
    username = "username"
    email = random_email(username)
    assert username in email



def test_random_username():
    first, last = random_name()
    username = random_username(first, last)
    assert first in username
    assert last in username


def test_random_user_id():
    user_id = random_user_id(1)
    assert user_id 