import pytest
from src.training_sessions.domain.models import TrainingSession, User, Exercise, Series, Repetition
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


def test_user_can_add_exercises():
    new_user = User(phone_number='34658493846')
    training_session = TrainingSession(started_at=datetime.now())
    new_user.add_training_session(training_session)

    exercise = Exercise(name = "Press Banca")
    training_session.add_exercise(exercise)

    assert training_session.exercises["press banca"] == exercise



def test_user_can_add_series_to_exercise():
    #Add user
    new_user = User(phone_number='34658493846')
    training_session = TrainingSession(started_at=datetime.now())
    # Add training session
    new_user.add_training_session(training_session)
    # Add exercise
    exercise = Exercise(name = "Press Banca")
    training_session.add_exercise(exercise)
    # Add series

    exercise.add_series()

    assert exercise.series[-1].number == 1


def test_series_autoincrement_number():
    #Add user
    new_user = User(phone_number='34658493846')
    training_session = TrainingSession(started_at=datetime.now())
    # Add training session
    new_user.add_training_session(training_session)
    # Add exercise
    exercise = Exercise(name = "Press Banca")
    training_session.add_exercise(exercise)
    # Add series
    number_of_series = 4
    series_output = [exercise.add_series() for i in range(number_of_series)]

    assert list(range(1,number_of_series+1)) == [series.number for series in series_output]



def test_user_can_add_repetitions_to_series():
    #Add user
    new_user = User(phone_number='34658493846')
    training_session = TrainingSession(started_at=datetime.now())
    # Add training session
    new_user.add_training_session(training_session)
    # Add exercise
    exercise = Exercise(name = "Press Banca")
    training_session.add_exercise(exercise)
    # Add series
    serie = exercise.add_series()
    

    # Add repetition
    repetition = Repetition(number = 1, kg = 100)
    serie.add_repetition(repetition)

    assert serie.repetitions[-1] == repetition




