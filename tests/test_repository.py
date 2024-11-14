import pytest
import models.models as model
import orm.repository as repository
from datetime import datetime
from sqlalchemy import text
import uuid

def test_repository_can_save_user(session):

    # Prepare
    new_user = model.User('+34545222123','Jose')
    user_repo = repository.SqlAlchemyRepository(session)

    # Function to assess
    user_repo.add(new_user)
    session.commit() # Remember we leave commit responsibility to the caller

    # SQL to get info
    rows = session.execute(text("SELECT id, phone_number, name FROM user"))

    assert list(rows) == [(new_user.id,'+34545222123','Jose')]


def insert_user(session):
    user_id = str(uuid.uuid4())
    session.execute(
        text("INSERT INTO user (id, phone_number, name) VALUES (:id, :phone, :name)"),
        {"id": user_id, "phone": "+34635805355", "name": "Jose"}
    )
    return user_id

def insert_training_session(session, user_id):
    training_session_id = str(uuid.uuid4())

    session.execute(
    text(
        "INSERT INTO training_session (id, user_id, status, started_at, modified_at) "
        "VALUES (:id, :user_id, :status, :started_at, :modified_at)"
    ),
    {
        "id": training_session_id,
        "user_id": user_id,
        "status": "In progress",
        "started_at": datetime.now(),
        "modified_at": datetime.now()
    }
)

    
    return training_session_id


def insert_set(session, training_session_id):
    # Add set:
    session.execute(text("INSERT INTO sets (session_id, exercise, series, repetition, kg, distance, mean_velocity, peak_velocity, power, rir)"
                         "VALUES (:session_id, :exercise, :series, :repetition, :kg, :distance, :mean_velocity, :peak_velocity, :power, :rir)"
                         ),
                         {'session_id' : training_session_id,
                           'exercise': 'Press Banca',
                          'series': 1,
                          'repetition': 1,
                          'kg': 214.3,
                          'distance': 1.03,
                          'mean_velocity': 0.24,
                          'peak_velocity': 1.3,
                          'power': 100,
                          'rir': 1
                          } 
                    )
    
    [[set_id]] = session.execute(text("SELECT id FROM sets WHERE session_id = :training_session_id"), {"training_session_id":training_session_id})

    return set_id


def test_repository_can_retrieve_user_with_training_sessions(session):

    user_id = insert_user(session)
    training_session_id = insert_training_session(session, user_id)
    set_id = insert_set(session, training_session_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get