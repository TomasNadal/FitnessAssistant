import pytest
from datetime import datetime
from models.models import TrainingSession, Set, User

def test_create_training_session(sample_user):
    id = 1244
    started_at = datetime.now()
    status = 'In progress'

    training_session = TrainingSession(id = id, started_at = started_at)
    sample_user.add_training_session(training_session)
    
    # Then
    assert training_session in sample_user.training_sessions
    assert len(sample_user.training_sessions) == 1
    assert training_session.id == id
    assert training_session.started_at == started_at
    assert training_session._status == "In progress"
    assert training_session.sets == set()


def test_create_series():
    exercise = "Press Banca"
    series = 1
    repetition = 1
    kg = 104
    distance = 0.41
    mean_velocity = 0.21
    peak_velocity = 0.8
    power = 213
    rir = 0

    set = Set(exercise = exercise,
                                     series = series,
                                     repetition = repetition,
                                     kg = kg,
                                     distance = distance,
                                     mean_velocity = mean_velocity,
                                     peak_velocity = peak_velocity,
                                     power = power)
    
    assert set.exercise == exercise
    assert set.series == series
    assert set.repetition == repetition
    assert set.kg == kg
    assert set.distance == distance
    assert set.mean_velocity == mean_velocity
    assert set.peak_velocity == peak_velocity
    assert set.power == power


def test_create_and_add_training_session_(sample_user):
    id = 1244
    started_at = datetime.now()
    status = 'In progress'

    training_session = TrainingSession(id = id, started_at = started_at)

    sample_user.add_training_session(training_session)

    assert sample_user.training_sessions == [training_session]
    added_session = sample_user.training_sessions[0]
    assert training_session.id == id
    assert training_session.started_at == started_at
    assert training_session._status == "In progress"
    assert training_session.sets == set()


def test_add_set_to_session(sample_user, sample_set,sample_training_session):
    sample_training_session.add_set(sample_set)

    assert sample_training_session.sets == {sample_set}


def test_is_session_active(sample_training_session):

    assert sample_training_session.is_active() == True

def test_end_training_session(sample_training_session):

    sample_training_session.end()
    assert sample_training_session._status == 'Completed'


