import pytest
import models.models as model
import orm.repository as repository
from datetime import datetime
from sqlalchemy import text

def test_user_repository_can_save_user(session):

    # Prepare
    new_user = model.User(1,'+34545222123','Jose')
    user_repo = repository.UserSqlAlchemyRepository(session)

    # Function to assess
    user_repo.add(new_user)
    session.commit() # Remember we leave commit responsibility to the caller

    # SQL to get info
    rows = session.execute(text("SELECT id, phone_number, name FROM user"))

    assert list(rows) == [(1,'+34545222123','Jose')]


def insert_user(session):
    session.execute(text("INSERT INTO user (phone_number, name) "
                         "VALUES ('+34635805355', 'Jose')"))
    [[user_id]] = session.execute(text("SELECT id FROM user WHERE phone_number=:phone_number AND name=:name"), {"phone_number": "+34635805355", "name":"Jose"})

    print(user_id)
    return user_id


def insert_training_session(session, user_id):
    session.execute(
    text(
        "INSERT INTO training_session (user_id,reference,status,started_at,modified_at) "
        "VALUES (:user_id, :reference, :status, :started_at, :modified_at)"
    ),
    {
        "user_id": user_id,
        "reference": "referencia",
        "status": "In progress",
        "started_at": datetime.now(),
        "modified_at": datetime.now()
    }
        )
    
    [[training_session_id]] = session.execute(text("SELECT id FROM trianing_session WHERE user_id = :user_id AND reference =:reference AND status = :status"), 
                                             {
                                                "user_id": user_id,
                                                "reference": "referencia",
                                                "status": "In progress"
                                            } )
    
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


def test_training_repository_can_save_training_session(session):

    user_id = insert_user(session)

    training_session = model.TrainingSession