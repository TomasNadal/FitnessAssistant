import pytest
from src.training_sessions.domain.models import TrainingSession,User,Set



def test_basic_create_user():

    phone_number = '+3467854323'

    new_user = User(phone_number=phone_number)
    print(new_user.id)

    assert new_user.phone_number == phone_number
    assert new_user.training_sessions == []