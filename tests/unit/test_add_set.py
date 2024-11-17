from datetime import datetime, date, timedelta
import pytest
from src.training_sessions.domain.models import add_set, User, TrainingSession, Set

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


def test_add_set_returns_training_session_id(sample_user, list_of_training_sessions, sample_set):
    now_time = datetime.now()
    sample_user.add_training_session(TrainingSession(started_at=now_time))
    assert sample_user.training_sessions[-1].started_at == now_time
    assert sample_user.training_sessions[-1].status == "In progress"

    session_id = add_set(sample_set,sample_user.training_sessions)

    assert session_id == sorted(sample_user.training_sessions, reverse=True)[0].id