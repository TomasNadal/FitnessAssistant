-- Create database (if not using an existing one)
-- CREATE DATABASE fitness_tracker;
-- USE fitness_tracker;

-- Enable UUID extension (for PostgreSQL)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(50),
    surname VARCHAR(50),
    date_of_birth DATE,
    gender VARCHAR(10),
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Exercise library
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    primary_muscle_group VARCHAR(50),
    secondary_muscle_group VARCHAR(50),
    equipment_needed VARCHAR(50),
    is_compound BOOLEAN DEFAULT FALSE
    CONSTRAINT unique_exercise_name UNIQUE (name)
);

-- Workout sessions
CREATE TABLE workout_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    notes TEXT,
    rating SMALLINT CHECK (rating >= 1 AND rating <= 10),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Exercise sets
CREATE TABLE exercise_sets (
    id SERIAL PRIMARY KEY,
    workout_session_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    set_number SMALLINT NOT NULL,
    weight_kg DECIMAL(6,2),
    reps INTEGER,
    rir SMALLINT, -- Reps In Reserve
    notes TEXT,
    video_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_session_id) REFERENCES workout_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
    CONSTRAINT unique_set_in_workout UNIQUE (workout_session_id, exercise_id, set_number)
);

-- Optional: Exercise repetitions (for detailed tracking with linear encoder)
CREATE TABLE exercise_repetitions (
    id SERIAL PRIMARY KEY,
    set_id INTEGER NOT NULL,
    rep_number SMALLINT NOT NULL,
    mean_velocity DECIMAL(5,2),
    peak_velocity DECIMAL(5,2),
    mean_power DECIMAL(7,2),
    peak_power DECIMAL(7,2),
    distance_mm DECIMAL(6,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (set_id) REFERENCES exercise_sets(id) ON DELETE CASCADE,
    CONSTRAINT unique_rep_in_set UNIQUE (set_id, rep_number)
);

-- Food items
CREATE TABLE food_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    serving_size DECIMAL(6,2),
    serving_unit VARCHAR(20),
    calories INTEGER,
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fat_g DECIMAL(6,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_food_item UNIQUE (name, brand)
);

-- Meals
CREATE TABLE meals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL, -- breakfast, lunch, dinner, snack
    time TIME,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Meal foods (junction table)
CREATE TABLE meal_foods (
    id SERIAL PRIMARY KEY,
    meal_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity DECIMAL(6,2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(id)
);

-- User measurements
CREATE TABLE user_measurements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(4,1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_user_measurement_date UNIQUE (user_id, date)
);

-- Create indexes for performance
CREATE INDEX idx_workout_sessions_user_id ON workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_start_time ON workout_sessions(start_time);
CREATE INDEX idx_exercise_sets_workout_session_id ON exercise_sets(workout_session_id);
CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_date ON meals(date);
CREATE INDEX idx_meal_foods_meal_id ON meal_foods(meal_id);
CREATE INDEX idx_user_measurements_user_id ON user_measurements(user_id);
CREATE INDEX idx_user_measurements_date ON user_measurements(date);