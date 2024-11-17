import pytest
from src.training_sessions.domain.models import TrainingSession,User,Set
from datetime import datetime, timedelta



def test_basic_create_user():

    phone_number = '+3467854323'

    new_user = User(phone_number=phone_number)
    print(new_user.id)

    assert new_user.phone_number == phone_number
    assert new_user.training_sessions == []


def test_training_sessions_are_ended_when_new_added():
    new_user = User(phone_number='+34675647392')

    new_user.add_training_session(TrainingSession(started_at=datetime(2020,2,1)))

    training_sessions = [TrainingSession(started_at= datetime.now() - timedelta(days=i)) for i in range(1,3)]

    for training_session in training_sessions:
        assert new_user.training_sessions[-1].status == 'In progress'
        previous_session_id = new_user.training_sessions[-1].id
        new_user.add_training_session(training_session)
        assert new_user.training_sessions[-2].status == 'Completed'
        assert previous_session_id ==new_user.training_sessions[-2].id
        assert new_user.training_sessions[-1].status == 'In progress'