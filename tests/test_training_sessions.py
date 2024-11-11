import pytest
from datetime import datetime
from models.models import TrainingSession, Set



def create_training_session(user, timestamp: datetime):
    return TrainingSession(user = user, timestamp = timestamp)

def test_create_training_session():
    user = 'user1'
    timestamp = datetime.now()
    reference = f'{user}-{timestamp}'
    status = 'In progress'

    training_session = create_training_session(user = user, timestamp = timestamp)

    assert training_session.user == user
    assert training_session.timestamp == timestamp
    assert training_session.reference == reference
    assert training_session._status == "In progress"
    assert training_session.sets == []


def test_create_series():
    exercise = "Press Banca"
    set_num = "S1"
    repetition = "R1"
    kg = 104
    distance = 0.41
    mean_velocity = 0.21
    peak_velocity = 0.8
    power = 213

    set = Set(exercise = exercise,
                                     set = set_num,
                                     repetition = repetition,
                                     kg = kg,
                                     distance = distance,
                                     mean_velocity = mean_velocity,
                                     peak_velocity = peak_velocity,
                                     power = power)
    
    assert set.exercise == exercise
    assert set.set == set_num
    assert set.repetition == repetition
    assert set.kg == kg
    assert set.distance == distance
    assert set.mean_velocity == mean_velocity
    assert set.peak_velocity == peak_velocity
    assert set.power == power

def test_add_set_to_session():
    user = 'user1'
    timestamp = datetime.now()
    reference = f'{user}{timestamp}'

    training_session = create_training_session(user = user, timestamp = timestamp)

    exercise = "Press Banca"
    set_num = "S1"
    repetition = "R1"
    kg = 104
    distance = 0.41
    mean_velocity = 0.21
    peak_velocity = 0.8
    power = 213

    set = Set(exercise = exercise,
                                     set = set_num,
                                     repetition = repetition,
                                     kg = kg,
                                     distance = distance,
                                     mean_velocity = mean_velocity,
                                     peak_velocity = peak_velocity,
                                     power = power)
    

    training_session.add_set(set)

    assert training_session.sets == [set]