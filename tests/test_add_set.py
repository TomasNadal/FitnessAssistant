from datetime import datetime, date, timedelta
import pytest
from models.models import add_set, User, TrainingSession, Set

now = datetime.now()
yesterday = now - timedelta(days=1)
last_week = now - timedelta(days=7)
times = [now,yesterday,last_week]


def test_add_set_to_most_recent_session(sample_user, sample_set):
    training_sessions = [TrainingSession(
        started_at=times[i]
    ) for i in range(3)]
    
    session_id = add_set(sample_set,training_sessions)

    assert {sample_set} == sorted(training_sessions, reverse=True)[0].sets
    assert now == sorted(training_sessions, reverse=True)[0].started_at


def test_add_set_returns_training_session_id(list_of_training_sessions, sample_set):
    session_id = add_set(sample_set,list_of_training_sessions)

    assert session_id == sorted(list_of_training_sessions, reverse=True)[0].id