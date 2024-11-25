import pytest
import src.training_sessions.domain.models as model
from sqlalchemy import text, event
from datetime import datetime


def test_mapper_can_load_user(session):

    expected = [model.User(phone_number="+34600000000"),
                model.User(phone_number="+34600000001"),
                model.User(phone_number="+34600000002")]
    
    [id1,id2,id3] = [user.id for user in expected]
    session.execute(text("INSERT INTO user (id, phone_number) VALUES "
                    '(:id1,"+34600000000"),'
                    '(:id2, "+34600000001"),'
                    '(:id3, "+34600000002")'
                ), dict(id1 = id1, id2 = id2, id3 = id3))
    

    

    assert session.query(model.User).all() == expected

def test_mapper_can_save_user(session):

    new_user = model.User(phone_number="+34600000000")
    id = new_user.id
    session.add(new_user)

    session.commit()

    rows = list(session.execute(text('SELECT id, phone_number FROM "user"')))

    assert rows == [(id, "+34600000000")]


def test_mapper_can_load_training_session(session):

    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()

    # 
    expected = [model.TrainingSession(current_time)]
    
    session_id = expected[0].id
    
    session.execute(
    text(
        "INSERT INTO training_session (id, user_id, status, started_at, modified_at) "
        "VALUES (:id, :user_id, :status, :started_at, :modified_at)"
    ),
    {
        "id": session_id,
        "user_id": new_user.id,
        "status": "In progress",
        "started_at": current_time,
        "modified_at": current_time
    }
)


    
    assert session.query(model.TrainingSession).all() == expected


def test_mapper_can_save_training_sessions(session):
    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    user_id = new_user.id
    session.commit()

    current_time = datetime.now()

    new_training_session = model.TrainingSession(current_time)
    new_user.add_training_session(new_training_session)
    id = new_training_session.id
    session.commit()

    rows = list(session.execute(text("SELECT id, user_id, started_at FROM 'training_session'")))

    assert rows == [(id,user_id,str(current_time))]


def test_mapper_can_load_exercises(session):

    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    user_id = new_user.id
    session.commit()

    # Create new training_session:
    current_time = datetime.now()
    new_training_session = model.TrainingSession(current_time)
    training_session_id = new_training_session.id
    new_user.add_training_session(new_training_session)
    session.commit()

    session.execute(text("INSERT INTO exercises (session_id, name) VALUES"
                         '(:session_id, :name)'),
                         dict(session_id = training_session_id, name = "press banca"))
    

    expected = model.Exercise(name = "press banca")
    result = session.query(model.Exercise).filter_by(name = "press banca")[0]

    assert expected == result


def test_mapper_can_save_exercises(session):
    
    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    user_id = new_user.id
    session.commit()

    # Create new training_session:
    current_time = datetime.now()
    new_training_session = model.TrainingSession(current_time)
    training_session_id = new_training_session.id
    new_user.add_training_session(new_training_session)
    session.commit()

    # Test mapper can save exercises
    exercise = model.Exercise(name = "sentadilla voladora")
    new_training_session._add_exercise(exercise)
    session.commit()

    obtain_session_id, obtained_name = session.execute(text("SELECT session_id, name FROM exercises WHERE name = :name"
                                  ),
                                  dict(name = "sentadilla voladora")).first()
    
    assert obtain_session_id == training_session_id
    assert obtained_name == 'sentadilla voladora'



def test_mapper_can_load_series(session):
    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    user_id = new_user.id
    session.commit()

    # Create new training_session:
    current_time = datetime.now()
    new_training_session = model.TrainingSession(current_time)
    training_session_id = new_training_session.id
    new_user.add_training_session(new_training_session)
    session.commit()

    # Create exercises
    exercise = model.Exercise(name = "sentadilla voladora")
    new_training_session._add_exercise(exercise)
    session.commit()

    # Get exercise ID
    exercise_id = session.execute(text("SELECT id FROM exercises WHERE name = 'sentadilla voladora'")).first()[0]

    # Test mapper can load series
    session.execute(text("INSERT INTO series (exercise_id, number)  VALUES "
                         '(:exercise_id, :number)'), 
                         dict(exercise_id = 1, number = 1)
                         )
    expected = [model.Series(number = 1)]
    result = session.query(model.Series).filter_by(exercise_id = exercise_id).all()

    assert result[0].number == expected[0].number



'''


def test_mapper_can_load_sets(session):
    
    # Create new user
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    user_id = new_user.id
    session.commit()

    # Create new training_session:
    current_time = datetime.now()
    new_training_session = model.TrainingSession(current_time)
    training_session_id = new_training_session.id
    new_user.add_training_session(new_training_session)
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
    new_user = model.User(phone_number="+34600000000")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()
    new_training_session = model.TrainingSession(current_time)
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

    assert rows == [(new_training_session.id,'Press Banca', 1, 1,  214.3, 1.03, 0.24, 1.3, 100, 1)]


'''