import pytest
import models.models as model
from sqlalchemy import text, event
from datetime import datetime


def test_mapper_can_load_user(session):

    session.execute(text("INSERT INTO user (phone_number) VALUES "
                    '("+34600000000"),'
                    '("+34600000001"),'
                    '("+34600000002")'
                ))
    
    expected = [model.User(1,phone_number="+34600000000"),
                model.User(2,phone_number="+34600000001"),
                model.User(3,phone_number="+34600000002")]
    

    assert session.query(model.User).all() == expected

def test_mapper_can_save_user(session):

    new_user = model.User(1,phone_number="+34600000000")
    session.add(new_user)

    session.commit()

    rows = list(session.execute(text('SELECT id, phone_number FROM "user"')))

    assert rows == [(1, "+34600000000")]


def test_mapper_can_load_training_session(session):

    # Create new user
    new_user = model.User(1 , phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()

    # 
    session.execute(
    text(
        "INSERT INTO training_session (id, user_id, status, started_at, modified_at) "
        "VALUES (:id, :user_id, :status, :started_at, :modified_at)"
    ),
    {
        "id": 1,
        "user_id": new_user.id,
        "status": "In progress",
        "started_at": current_time,
        "modified_at": current_time
    }
)

    expected = [model.TrainingSession(1,current_time)]
    
    assert session.query(model.TrainingSession).all() == expected


def test_mapper_can_save_training_sessions(session):
    # Create new user
    new_user = model.User(1 , phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()

    new_training_session = model.TrainingSession(1, current_time)
    new_user.add_training_session(new_training_session)
    session.commit()

    rows = list(session.execute(text("SELECT id, user_id, started_at FROM 'training_session'")))

    assert rows == [(1,1,str(current_time))]



def test_mapper_can_load_sets(session):
    
    # Create new user
    new_user = model.User(1 , phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    # Create new training_session:
    current_time = datetime.now()
    new_training_session = model.TrainingSession(1, current_time)
    session.add(new_training_session)
    session.commit()


    # Add set:
    session.execute(text("INSERT INTO sets (session_id, exercise, series, repetition, kg, distance, mean_velocity, peak_velocity, power, rir)"
                         "VALUES (:session_id, :exercise, :series, :repetition, :kg, :distance, :mean_velocity, :peak_velocity, :power, :rir)"
                         ),
                         {'session_id' : new_training_session.id,
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
    
    expected =            [model.Set(
                                exercise = 'Press Banca',
                                    series = 1,
                                    repetition = 1,
                                    kg =  214.3,
                                    distance =  1.03,
                                    mean_velocity = 0.24,
                                    peak_velocity =1.3,
                                    power = 100 ,
                                    rir = 1)]
    

    assert session.query(model.Set).all() == expected



def test_mapper_can_save_sets(session):

     # Add SQL logging
    def on_sql(statement, *_):
        print(f'Statement: {statement}')
    
    event.listen(session.bind, 'before_cursor_execute', on_sql)

    # Your existing test code
    new_user = model.User(1 , phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()
    new_training_session = model.TrainingSession(1,  current_time)
    new_user.add_training_session(new_training_session)
    session.commit()

    new_training_set = model.Set(exercise = 'Press Banca',
                                    series = 1,
                                    repetition = 1,
                                    kg =  214.3,
                                    distance =  1.03,
                                    mean_velocity = 0.24,
                                    peak_velocity =1.3,
                                    power = 100 ,
                                    rir = 1)
    
    new_training_session.add_set(new_training_set)
    session.commit()

    rows = list(session.execute(text("SELECT session_id, exercise, series, repetition, kg, distance, mean_velocity, peak_velocity, power, rir FROM sets")))

    assert rows == [(1,'Press Banca', 1, 1,  214.3, 1.03, 0.24, 1.3, 100, 1)]