import pytest
import requests
import src.training_sessions.config as config
from random import randint


def random_set(phone_number, series_number):
    exercise = 'Banco volador'
    kg = 200

    number_of_reps = randint(1,10)

    return [{
        'from': phone_number, 'set':{
        'exercise':exercise,
        'series':series_number,
        'repetition': i,
        'kg': kg
    }} for i in range(number_of_reps)]
    


# First instinct is to test here if data is commited to database, etc. But what we really
# are trying to test is if the API does what it is expected. I.e parse data correctly,
# return correct error codes and info

# When selecting start_training in whatsapp, a call is made to this endpoint and a new
# session is created
def post_to_create_training_session(phone_number):
    url = config.get_api_url()
    r = requests.post(f'{url}/new_training_session', json={'phone_number':phone_number})

    assert r.status_code == 201
    assert r.json()["session_id"] is not None

    return r.json()["session_id"]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_set():
    url = config.get_api_url()

    phone_number = '+34678383282'
    sets = random_set(phone_number, 1)
    session_id = post_to_create_training_session(phone_number)

    for set in sets:
        r = requests.post(f'{url}/add_set', json=set)
        assert r.status_code == 201
        assert r.json()["session_id"] == session_id



# Add here the unhappy path
