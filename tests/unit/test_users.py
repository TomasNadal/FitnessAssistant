import pytest
from src.training_sessions.domain.models import WorkoutSession, User, Exercise, ExerciseSet, ExerciseRepetition, Meal, EatingDay, FoodItem, Recipe, RecipeIngredient 
from datetime import datetime, timedelta, date


def test_basic_create_user():
    phone_number = '+3467854323'
    name = "John"
    gender = "Male"

    new_user = User(phone_number=phone_number, name=name, gender=gender)

    assert new_user.phone_number == phone_number
    assert new_user.name == name
    assert new_user.gender == gender
    assert new_user.workout_sessions == []


def test_workout_sessions_are_ended_when_new_added():
    new_user = User(phone_number='+34675647392', name="Jane", gender="Female")
    
    # First session
    first_session = WorkoutSession(started_at=datetime(2020,2,1))
    new_user.add_workout_session(first_session)
    
    # End the first session so we can add more
    new_user.end_workout_session()
    
    # Add more sessions
    for i in range(1, 3):
        session = WorkoutSession(started_at=datetime.now() - timedelta(days=i))
        
        # Make sure previous session is completed
        assert new_user.workout_sessions[-1].is_completed()
        
        # Store previous session ID for comparison
        previous_session = new_user.workout_sessions[-1]
        
        # Add new session
        new_user.add_workout_session(session)
        
        # Verify previous session is still completed
        assert previous_session.is_completed()
        
        # End the current session so we can add another
        session.end_time = session.start_time + timedelta(hours=1)


def test_user_can_add_exercises():
    new_user = User(phone_number='34658493846', name="Alex", gender="Male")
    workout_session = WorkoutSession(started_at=datetime.now())
    new_user.workout_sessions.append(workout_session)

    exercise = Exercise(
        name="Press Banca",
        description="Chest press exercise",
        primary_muscle_group="Chest",
        secondary_muscle_group="Triceps"
    )
    
    # Create an exercise set
    exercise_set = ExerciseSet(
        workout_session=workout_session,
        exercise=exercise,
        set_number=1,
        weight=100.0,
        reps=10
    )
    
    # Add the exercise set to the workout session
    workout_session.exercise_sets.append(exercise_set)

    assert any(es.exercise.name == "Press Banca" for es in workout_session.exercise_sets)


def test_user_can_add_repetitions_to_exercise_set():
    new_user = User(phone_number='34658493846', name="Sam", gender="Female")
    workout_session = WorkoutSession(started_at=datetime.now())
    new_user.workout_sessions.append(workout_session)
    
    exercise = Exercise(
        name="Press Banca",
        description="Chest press exercise",
        primary_muscle_group="Chest",
        secondary_muscle_group="Triceps"
    )
    
    # Create an exercise set with 1 rep
    exercise_set = ExerciseSet(
        workout_session=workout_session,
        exercise=exercise,
        set_number=1,
        weight=100.0,
        reps=1
    )
    
    workout_session.exercise_sets.append(exercise_set)
    
    # Create a repetition
    repetition = ExerciseRepetition(
        number=1,
        kg=100.0,
        distance=0.5,
        mean_velocity=0.8,
        peak_velocity=1.2,
        power=120.0
    )
    
    # Add the repetition to the exercise set
    exercise_set._add_repetition(repetition)

    assert exercise_set.repetitions[-1] == repetition




def test_user_can_add_meals():
    new_user = User(phone_number='34658493846', name="Alex", gender="Male")
    meal = Meal(date=datetime.now(), meal_type="Breakfast")
    new_user.meals.append(meal)

    assert any(m.date == datetime.now() for m in new_user.meals)


def test_user_can_add_meals_given_date():
    new_user = User(phone_number='34658493846', name="Alex", gender="Male")
    meal = Meal(date=datetime.now(), meal_type="Breakfast")
    new_user.add_meal_given_date(meal, datetime.now())

    assert any(m.date == datetime.now() for m in new_user.meals)        



