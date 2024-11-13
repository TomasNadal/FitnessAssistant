import pytest
from models.models import TrainingSession,User,Set


@pytest.fixture
def sample_user():
    return User(id = 1, phone_number='+3467854323')

def test_basic_create_user():
    id = 1
    phone_number = '+3467854323'

    new_user = User(id = id , phone_number=phone_number)
    print(new_user.id)
    assert new_user.id == id
    assert new_user.phone_number == phone_number
    assert new_user.training_session == []