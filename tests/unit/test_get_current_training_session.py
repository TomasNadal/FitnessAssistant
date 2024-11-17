from datetime import datetime, date, timedelta
import pytest
from src.training_sessions.domain.models import get_current_training_session, User, TrainingSession, Set, NotActiveSessions


'''
Correct NotActiveSessions when training session there are no training sessions
Correct training session when there is one training session
Correct training session when there are more than one training session with In progress
Doesn't return session if only one session but it is not In Progress
'''

def test_get_current_training_training_session_raises_error_if_no_sessions_created():
    user = User(phone_number='+34656767676')

    with pytest.raises(NotActiveSessions) as e:
        get_current_training_session(user.training_sessions)


def test_correct_training_sessions_if_only_one_created():
    user = User(phone_number='+34656767676')
    
    user.add_training_session(TrainingSession(started_at=datetime.now()))
    training_session = user.training_sessions[0]

    training_session_obtained = get_current_training_session(user.training_sessions)

    assert training_session == training_session_obtained

def test_correct_training_sessions_if_many_sessions_created():
    user = User(phone_number='+34656767676')
    
    user.add_training_session(TrainingSession(started_at=datetime.now() - timedelta(days=3)))
    user.add_training_session(TrainingSession(started_at=datetime.now() - timedelta(days=1)))
    user.add_training_session(TrainingSession(started_at=datetime.now()))
    training_session_old,training_session_mid,training_session_new = user.training_sessions

    training_session_obtained = get_current_training_session(user.training_sessions)

    assert training_session_new == training_session_obtained


def test_raises_NotActiveSessions_if_one_session_created_but_not_active():
    user = User(phone_number='+34656767676')
    
    user.add_training_session(TrainingSession(started_at=datetime.now()))
    training_session = user.training_sessions[0]

    training_session.end()

    with pytest.raises(NotActiveSessions):

        training_session_obtained = get_current_training_session(user.training_sessions)
