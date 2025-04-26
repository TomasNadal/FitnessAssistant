import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine
import requests
from requests.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, clear_mappers
from src.training_sessions.domain.models import User, WorkoutSession, Exercise, ExerciseSet, ExerciseRepetition
from datetime import datetime, timedelta

from src.training_sessions.adapters.orm import mapper_registry, start_mappers, registry
import src.training_sessions.config as config


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
def sample_json_payload():
    return {'from':'+34645353526', 'set':[{'exercise':'Press Banca',
        'series':1,
        'repetition': 1,
        'kg': 123}]}


@pytest.fixture
def test_data_folder():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_user():
    return User(phone_number='+3467854323', name="Test User", gender="Male")


@pytest.fixture
def sample_workout_session(sample_user):
    workout_session = WorkoutSession(
        started_at=datetime.now()
    )

    # Add the session directly to the user's workout_sessions list
    # since we can't use add_workout_session without ending the previous session
    sample_user.workout_sessions.append(workout_session)

    return workout_session


@pytest.fixture
def list_of_workout_sessions(sample_user):
    list_of_workouts = [WorkoutSession(
        started_at=datetime.now() - timedelta(days=i)
    ) for i in range(1,4,1)]

    # Add the first session directly
    sample_user.workout_sessions.append(list_of_workouts[0])
    
    # End the first session so we can add more
    list_of_workouts[0].end_time = list_of_workouts[0].start_time + timedelta(hours=1)
    
    # Add the remaining sessions, ending each one after adding
    for session in list_of_workouts[1:]:
        sample_user.add_workout_session(session)
        session.end_time = session.start_time + timedelta(hours=1)

    return list_of_workouts


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)

    pytest.fail("Postgres never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def postgres_db():
    db_uri = config.get_postgres_uri()
    print(db_uri)
    engine = create_engine(db_uri)

    wait_for_postgres_to_come_up(engine)
    mapper_registry.metadata.create_all(engine)
    return engine
    

@pytest.fixture
def session_factory_in_memory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind = in_memory_db)
    clear_mappers()


@pytest.fixture
def session_factory(postgres_db):
    start_mappers()
    yield sessionmaker(bind = postgres_db)
    clear_mappers()

@pytest.fixture
def session_factory_non_persistent(postgres_db):
    start_mappers()
    yield sessionmaker(bind = postgres_db)
    # Clean up the database after the test
    with postgres_db.begin() as conn:
        # Delete all data from tables in reverse order of dependencies
        conn.execute(mapper_registry.metadata.tables['exercise_sets'].delete())
        conn.execute(mapper_registry.metadata.tables['exercises'].delete())
        conn.execute(mapper_registry.metadata.tables['workout_sessions'].delete())
        conn.execute(mapper_registry.metadata.tables['users'].delete())
    clear_mappers()


@pytest.fixture
def restart_api():
    (Path(__file__).parent.parent / "src/training_sessions/entrypoints/flask_app.py").touch()

    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture
def valid_csv_adrencoder_path():
    adr_path = Path(__file__).parent / "fixtures" / "adrencoder.csv"
    return adr_path

@pytest.fixture
def valid_csv_adrencoder_ejercicios_variados():
    adr_path = Path(__file__).parent / "fixtures" / "adrejercicios.csv"
    return adr_path

@pytest.fixture
def invalid_csv_adrencoder_path():
    adr_path = Path(__file__).parent / "fixtures" / "adrencoder_invalid.csv"
    return adr_path
 
from tests.fixtures.payloads import (
    VALID_STATUS_UPDATE_PAYLOAD,
    VALID_TEXT_MESSAGE_PAYLOAD,
    VALID_DOCUMENT_MESSAGE_PAYLOAD,
    INVALID_MESSAGE_PAYLOAD,
    INTERACTIVE_LIST_SEND_PAYLOAD,
    VALID_LIST_REPLY,
    DOCUMENT_MESSAGE,
    DOCUMENT_MESSAGE_2  
)

# Define Test Payloads
@pytest.fixture
def valid_list_reply_payload():
    return VALID_LIST_REPLY

@pytest.fixture
def interactive_send_payload():
    return INTERACTIVE_LIST_SEND_PAYLOAD

@pytest.fixture
def valid_status_update_payload():
    return VALID_STATUS_UPDATE_PAYLOAD

@pytest.fixture
def valid_text_message_payload():
    return VALID_TEXT_MESSAGE_PAYLOAD

@pytest.fixture
def valid_document_message_payload():
    return VALID_DOCUMENT_MESSAGE_PAYLOAD

@pytest.fixture
def invalid_message_payload():
    return INVALID_MESSAGE_PAYLOAD

@pytest.fixture
def document_message_part():
    return DOCUMENT_MESSAGE

@pytest.fixture
def document_message_part_2():
    return DOCUMENT_MESSAGE_2