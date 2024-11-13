import pytest
from datetime import datetime
from models.models import TrainingSession, Set, User


@pytest.fixture
def sample_user():
    return User(id = 1, phone_number='+3467854323')


@pytest.fixture
def sample_set():
    return Set(
        exercise="Press Banca",
        series=1,
        repetition=1,
        kg=104,
        distance=0.41,
        mean_velocity=0.21,
        peak_velocity=0.8,
        power=213
    )

@pytest.fixture
def sample_training_session(sample_user):
    return TrainingSession(
        id = 1,
        user = sample_user,
        started_at=datetime.now()
    )


def create_training_session(id, user, started_at: datetime):
    return TrainingSession(id = id, user = user, started_at = started_at)

def test_create_training_session(sample_user):
    id = 1244
    started_at = datetime.now()
    reference = f'{sample_user.id}-{started_at}'
    status = 'In progress'

    training_session = create_training_session(id = id, user = sample_user, started_at = started_at)

    assert training_session.id == id
    assert training_session.user == sample_user
    assert training_session.started_at == started_at
    assert training_session.reference == reference
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

def test_add_set_to_session(sample_user, sample_set,sample_training_session):
    sample_training_session.add_set(sample_set)

    assert sample_training_session.sets == {sample_set}


def test_is_session_active(sample_training_session):

    assert sample_training_session.is_active() == True

def test_end_training_session(sample_training_session):

    sample_training_session.end()
    assert sample_training_session._status == 'Completed'


