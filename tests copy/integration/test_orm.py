import pytest
import src.training_sessions.domain.models as model
from sqlalchemy import text, event
from datetime import datetime


def test_mapper_can_load_user(session):
    expected = [
        model.User(phone_number="+34600000000", name="Test User", gender="Male"),
        model.User(phone_number="+34600000001", name="Test User2", gender="Female"),
        model.User(phone_number="+34600000002", name="Test User3", gender="Male")
    ]
    
    session.execute(
        text("INSERT INTO users (phone_number, name, gender) VALUES "
             "(:phone1, :name1, :gender1),"
             "(:phone2, :name2, :gender2),"
             "(:phone3, :name3, :gender3)"
        ), {
            "phone1": "+34600000000", "name1": "Test User", "gender1": "Male",
            "phone2": "+34600000001", "name2": "Test User2", "gender2": "Female",
            "phone3": "+34600000002", "name3": "Test User3", "gender3": "Male"
        }
    )
    
    users = session.query(model.User).all()
    
    # Compare only phone numbers since other attributes might have default values
    assert [u.phone_number for u in users] == [u.phone_number for u in expected]


def test_mapper_can_save_user(session):
    new_user = model.User(phone_number="+34600000000", name="Test User", gender="Male")
    session.add(new_user)
    session.commit()

    rows = list(session.execute(text('SELECT phone_number, name, gender FROM users')))
    assert rows == [("+34600000000", "Test User", "Male")]


def test_mapper_can_load_workout_session(session):
    # Create new user
    new_user = model.User(phone_number="+34600000000", name="Test User", gender="Male")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()
    
    # Insert workout session
    session.execute(
        text(
            "INSERT INTO workout_sessions (user_id, start_time, created_at, updated_at) "
            "VALUES (:user_id, :start_time, :created_at, :updated_at)"
        ),
        {
            "user_id": 1,  # Assuming user ID is 1
            "start_time": current_time,
            "created_at": current_time,
            "updated_at": current_time
        }
    )
    
    # Query the workout session
    workout_session = session.query(model.WorkoutSession).first()
    
    assert workout_session is not None
    assert workout_session.start_time == current_time


def test_mapper_can_save_workout_sessions(session):
    # Create new user
    new_user = model.User(phone_number="+34600000000", name="Test User", gender="Male")
    session.add(new_user)
    session.commit()

    current_time = datetime.now()

    # Create new workout session
    new_workout_session = model.WorkoutSession(started_at=current_time)
    new_user.add_workout_session(new_workout_session)
    session.commit()

    rows = list(session.execute(text("SELECT user_id, start_time FROM workout_sessions")))
    
    # Check that the user_id is 1 and start_time matches
    assert len(rows) == 1
    assert rows[0][0] == 1  # user_id
    assert datetime.strptime(rows[0][1], '%Y-%m-%d %H:%M:%S.%f') == current_time  # start_time


def test_mapper_can_load_exercises(session):
    current_time = datetime.now()
    
    # Insert exercise
    session.execute(
        text(
            "INSERT INTO exercises (name, description, primary_muscle_group, secondary_muscle_group, is_compound) "
            "VALUES (:name, :description, :primary, :secondary, :is_compound)"
        ),
        {
            "name": "Bench Press",
            "description": "Chest exercise",
            "primary": "Chest",
            "secondary": "Triceps",
            "is_compound": True
        }
    )
    
    # Query the exercise
    exercise = session.query(model.Exercise).first()
    
    assert exercise is not None
    assert exercise.name == "Bench Press"
    assert exercise.primary_muscle_group == "Chest"


def test_mapper_can_save_exercises(session):
    current_time = datetime.now()
    
    # Create new exercise
    new_exercise = model.Exercise(
        name="Squat",
        description="Leg exercise",
        primary_muscle_group="Quadriceps",
        secondary_muscle_group="Glutes",
        is_compound=True
    )
    
    session.add(new_exercise)
    session.commit()

    rows = list(session.execute(text("SELECT name, primary_muscle_group FROM exercises")))
    
    assert rows == [("Squat", "Quadriceps")]


def test_exercise_set_relationships(session):
    # Create user
    user = model.User(phone_number="+34600000000", name="Test User", gender="Male")
    session.add(user)
    session.commit()
    
    # Create workout session
    current_time = datetime.now()
    workout = model.WorkoutSession(started_at=current_time)
    user.add_workout_session(workout)
    
    # Create exercise
    exercise = model.Exercise(
        name="Deadlift",
        description="Back exercise",
        primary_muscle_group="Back",
        secondary_muscle_group="Hamstrings",
        is_compound=True
    )
    session.add(exercise)
    
    # Create exercise set
    exercise_set = model.ExerciseSet(
        set_number=1,
        weight_kg=100.0,
        reps=5,
        workout_session=workout,
        exercise=exercise
    )
    session.add(exercise_set)
    
    session.commit()
    
    # Query the exercise set
    loaded_set = session.query(model.ExerciseSet).first()
    
    assert loaded_set is not None
    assert loaded_set.set_number == 1
    assert loaded_set.weight_kg == 100.0
    assert loaded_set.reps == 5
    assert loaded_set.exercise.name == "Deadlift"
    assert loaded_set.workout_session.start_time == current_time


def test_exercise_set_relationships_in_postgres(session_factory_non_persistent):
    # Create user
    session = session_factory_non_persistent()
    user = model.User(phone_number="+34600000000", name="Test User", gender="Male")
    session.add(user)
    session.commit()
    
    # Create workout session
    current_time = datetime.now()
    workout = model.WorkoutSession(started_at=current_time)
    user.add_workout_session(workout)
    
    # Create exercise
    exercise = model.Exercise(
        name="Deadlift",
        description="Back exercise",
        primary_muscle_group="Back",
        secondary_muscle_group="Hamstrings",
        is_compound=True
    )
    session.add(exercise)
    
    # Create exercise set
    exercise_set = model.ExerciseSet(
        set_number=1,
        weight_kg=100.0,
        reps=5,
        workout_session=workout,
        exercise=exercise
    )
    session.add(exercise_set)
    
    session.commit()
    
    # Query the exercise set
    loaded_set = session.query(model.ExerciseSet).first()
    
    assert loaded_set is not None
    assert loaded_set.set_number == 1
    assert loaded_set.weight_kg == 100.0
    assert loaded_set.reps == 5
    assert loaded_set.exercise.name == "Deadlift"
    assert loaded_set.workout_session.start_time == current_time