import pytest
import src.training_sessions.domain.models as model
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from src.training_sessions import config
import src.training_sessions.service_layer.unit_of_work as unit_of_work
from datetime import datetime

'''
Need to test that the unit of work is able to get user by phone number and access its training sessions

Retrieve a user and add set to it

Commits/Unrolls etc


'''


def insert_user(session: Session , phone_number: str) -> None:

    session.execute(text('INSERT INTO "user" (id, phone_number) VALUES '
                         '(:id, :phone_number) '),
                         dict(id = phone_number[2:4], phone_number=phone_number))
    

def insert_training_session(session: Session , phone_number: str) -> None:

    result = session.execute(
                        text('SELECT id FROM "user" WHERE phone_number = :phone'),
                        {'phone': phone_number}
                    ).first()[0]

    print(result)
    started_at = datetime.now()

    session.execute(text("INSERT INTO training_session (id, user_id, status, started_at) VALUES"
                         '(:id, :user_id, :status, :started_at)'), dict(id = "testsession3213", user_id = result, started_at = started_at, status = "In progress"))
    

def get_training_session_id(session: Session , phone_number: str):
    result = session.execute(
                        text('SELECT id FROM "user" WHERE phone_number = :phone'),
                        {'phone': phone_number}
                    ).first()[0]
    
    training_id = session.execute(text("SELECT id FROM training_session WHERE user_id = :user_id"), dict(user_id = result)).first()[0]

    return training_id


def get_exercises_from_training_session(session: Session, training_session_id: str):
    [result] = session.execute(text('SELECT name FROM exercises WHERE session_id = :training_session_id'), dict(training_session_id=training_session_id))

    return result

def test_uow_can_get_user_and_add_exercises(session_factory_in_memory):
    session = session_factory_in_memory()
    insert_user(session, '346578493123')
    insert_training_session(session, '346578493123')
    
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory_in_memory)

    with uow:
        user = uow.users.get('346578493123')
        exercise = model.Exercise(name = 'Press banca')
        series = exercise.add_series()
        repetition = model.Repetition(number = 1, kg = 12)
        series.add_repetition(repetition)
        training_session = user.training_sessions[-1]
        training_session._add_exercise(exercise)
        
        uow.commit()

    training_session_ref = get_training_session_id(session, '346578493123')
    exercises = get_exercises_from_training_session(session, training_session_ref)
    assert training_session_ref == "testsession3213"
    assert 'press banca' in exercises


def test_rolls_back_uncommited_work_by_default(session_factory_in_memory):
    # UoW should not commit anything if not explicitly commited

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory_in_memory)

    with uow:
        insert_user(uow.session, "34657849314")

    new_session = session_factory_in_memory()
    rows = list(new_session.execute(text('SELECT * FROM "user"')))

    assert rows == []


def test_rolls_back_on_error(session_factory_in_memory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory_in_memory)

    with pytest.raises(MyException):
        with uow:
            insert_user(uow.session, '34657849315')
            raise MyException()
    
    new_session = session_factory_in_memory()
    rows = list(new_session.execute(text('SELECT * FROM "user"')))

    assert rows == []
        