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

def test_uow_can_get_user_and_add_sets(session_factory_in_memory):
    session = session_factory_in_memory()
    insert_user(session, '346578493123')
    insert_training_session(session, '346578493123')
    
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory_in_memory)

    with uow:
        user = uow.user.get('346578493123')
        training_set = model.Set(exercise = 'Press banca', series = 10, repetition = 5, kg = 12)
        training_session = user.training_sessions[-1]
        training_session.add_set(training_set)
        
        uow.commit()

    training_session_ref = get_training_session_id(session, '346578493123')
    assert training_session_ref == "testsession3213"


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
        