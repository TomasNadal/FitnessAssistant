import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from models.models import User, TrainingSession, Set
from datetime import datetime, timedelta

from orm.orm import mapper_registry, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()



@pytest.fixture
def sample_user():
    return User(phone_number='+3467854323')



@pytest.fixture
def sample_training_session(sample_user):
    training_session = TrainingSession(
        started_at=datetime.now()
    )

    sample_user.add_training_session(training_session)

    return training_session



@pytest.fixture
def list_of_training_sessions(sample_user):
    list_of_training = [TrainingSession(
        started_at=datetime.now() - timedelta(days=i)
    ) for i in range(1,4,1)]

    for session in list_of_training:
        sample_user.add_training_session(session)

    return list_of_training



@pytest.fixture
def sample_set(sample_training_session):
    sample_training_session.add_set(Set(
        exercise="Press Banca",
        series=1,
        repetition=1,
        kg=104,
        distance=0.41,
        mean_velocity=0.21,
        peak_velocity=0.8,
        power=213
    ))

    return next(iter(sample_training_session.sets))
    