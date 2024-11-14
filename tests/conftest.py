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
    return User(id = 1, phone_number='+3467854323')



@pytest.fixture
def sample_training_session(sample_user):
    return TrainingSession(
        id = 1,
        user_id = sample_user.id,
        started_at=datetime.now()
    )


@pytest.fixture
def list_of_training_sessions(sample_user):
    return [TrainingSession(
        id = i,
        user_id = sample_user.id,
        started_at=datetime.now() - timedelta(days=i)
    ) for i in range(1,4,1)]


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
    