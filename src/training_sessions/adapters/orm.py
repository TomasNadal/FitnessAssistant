from sqlalchemy import Table, MetaData, Column, Integer, String, Date, ForeignKey, Float, DateTime, Boolean, Text
from sqlalchemy.orm import registry,  relationship, attribute_keyed_dict

import src.training_sessions.domain.models as model

# This mapping style is the classical ("imperative") way

'''
Metadata contains information of the database schema
'''
mapper_registry = registry()

user = Table('users',
              mapper_registry.metadata,
              Column('id', Integer, primary_key=True, autoincrement=True),
              Column('phone_number', String(15)),
              Column('gender', String(10)),   
              Column('name', String(255), nullable=True),
              Column('surname', String(255), nullable=True),
              Column('email', String(255), nullable=True),
              Column('password_hash', String(255), nullable=True),
              Column('date_of_birth', Date, nullable=True),
              Column('height', Float, nullable=True),
              Column('weight', Float, nullable= True)
              )


workout_sessions = Table('workout_sessions',
                        mapper_registry.metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('user_id', Integer, ForeignKey('users.id')),
                        Column('start_time', DateTime),
                        Column('updated_at', DateTime),
                        Column('end_time', DateTime),
                        Column('notes', String),
                        Column('rating', Integer),
                        Column('created_at', DateTime)
                        )

exercise = Table('exercises',
                mapper_registry.metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('name', String(100)),
                Column('description', String(255)),
                Column('primary_muscle_group', String(100)),
                Column('secondary_muscle_group', String(100)),
                Column('equipment_needed', String(100)),
                Column('is_compound', Boolean)
                )


exercise_sets = Table('exercise_sets',
                    mapper_registry.metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('exercise_id', Integer, ForeignKey('exercises.id')),
                    Column('workout_session_id', Integer, ForeignKey('workout_sessions.id')),
                    Column('set_number', Integer),
                    Column('weight_kg', Float),
                    Column('reps', Integer),
                    Column('rir', Integer, nullable=True),
                    Column('notes', String, nullable=True),
                    Column('video_url', String(255), nullable=True),
                    Column('created_at', DateTime),
                    Column('updated_at', DateTime)
                    )

exercise_repetitions = Table('exercise_repetitions',
                            mapper_registry.metadata,
                            Column('id', Integer, primary_key=True, autoincrement=True),
                            Column('exercise_set_id', Integer, ForeignKey('exercise_sets.id')),
                            Column('rep_number', Integer),
                            Column('distance', Float),
                            Column('mean_velocity', Float),
                            Column('peak_velocity', Float),
                            Column('power', Float),
                            Column('created_at', DateTime)
                            )   

# New tables for food models
food_items = Table('food_items',
                  mapper_registry.metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('name', String(100)),
                  Column('brand', String(100), nullable=True),
                  Column('serving_size_grams', Float),
                  Column('calories_per_100g', Float),
                  Column('protein_per_100g', Float),
                  Column('carbs_per_100g', Float),
                  Column('fat_per_100g', Float),
                  Column('fiber_per_100g', Float),
                  Column('source', String(50)),
                  Column('verified', Boolean),
                  Column('created_at', DateTime),
                  Column('updated_at', DateTime)
                  )

eating_days = Table('eating_days',
                   mapper_registry.metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('user_id', Integer, ForeignKey('users.id')),
                   Column('date', DateTime),
                   Column('created_at', DateTime),
                   Column('updated_at', DateTime)
                   )

meals = Table('meals',
             mapper_registry.metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('eating_day_id', Integer, ForeignKey('eating_days.id')),
             Column('user_id', Integer, ForeignKey('users.id')),
             Column('date', DateTime),
             Column('meal_type', String(20)),
             Column('created_at', DateTime),
             Column('updated_at', DateTime)
             )

meal_foods = Table('meal_foods',
                  mapper_registry.metadata,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('meal_id', Integer, ForeignKey('meals.id')),
                  Column('food_item_id', Integer, ForeignKey('food_items.id')),
                  Column('amount_grams', Float),
                  Column('created_at', DateTime),
                  Column('updated_at', DateTime)
                  )

recipes = Table('recipes',
               mapper_registry.metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('user_id', Integer, ForeignKey('users.id')),
               Column('name', String(100)),
               Column('servings', Integer),
               Column('created_at', DateTime),
               Column('updated_at', DateTime)
               )

recipe_ingredients = Table('recipe_ingredients',
                          mapper_registry.metadata,
                          Column('id', Integer, primary_key=True, autoincrement=True),
                          Column('recipe_id', Integer, ForeignKey('recipes.id')),
                          Column('food_item_id', Integer, ForeignKey('food_items.id')),
                          Column('amount_grams', Float),
                          Column('created_at', DateTime),
                          Column('updated_at', DateTime)
                          )

# Info about relationships goes in properties dict. The relationships refer to
# relationships defined in the domain class
def start_mappers():
    repetitions_mapper = mapper_registry.map_imperatively(
        model.ExerciseRepetition, 
        exercise_repetitions,
        properties={
            "_exercise_set": relationship("ExerciseSet", back_populates="exercise_repetitions")
        }
    )
    
    exercise_set_mapper = mapper_registry.map_imperatively(
        model.ExerciseSet,
        exercise_sets,
        properties={
            "exercise_repetitions": relationship(model.ExerciseRepetition, collection_class=list, back_populates="_exercise_set"),
            "exercise": relationship("Exercise", back_populates="exercise_sets"),
            "workout_session": relationship("WorkoutSession", back_populates="exercise_sets")
        }
    )

    exercise_mapper = mapper_registry.map_imperatively(
        model.Exercise,
        exercise,
        properties={
            "exercise_sets": relationship(model.ExerciseSet, collection_class=list, back_populates="exercise")
        }
    )

    workout_session_mapper = mapper_registry.map_imperatively(
        model.WorkoutSession,
        workout_sessions,
        properties={
            "exercise_sets": relationship(model.ExerciseSet, collection_class=list, back_populates="workout_session"),
            "_user": relationship("User", back_populates="workout_sessions")
        }
    )
    
    mapper_registry.map_imperatively(
        model.User,
        user,
        properties={
            "workout_sessions": relationship(model.WorkoutSession, collection_class=list, back_populates="_user"),
            "eating_days": relationship(model.EatingDay, collection_class=list, back_populates="_user")
        }
    )

    # New mappers for food models
    food_item_mapper = mapper_registry.map_imperatively(
        model.FoodItem,
        food_items
    )
    
    recipe_ingredient_mapper = mapper_registry.map_imperatively(
        model.RecipeIngredient,
        recipe_ingredients,
        properties={
            "recipe": relationship("Recipe", back_populates="ingredients"),
            "food_item": relationship("FoodItem")
        }
    )
    
    recipe_mapper = mapper_registry.map_imperatively(
        model.Recipe,
        recipes,
        properties={
            "ingredients": relationship(model.RecipeIngredient, collection_class=list, back_populates="recipe"),
            "_user": relationship("User")
        }
    )
    
    meal_food_mapper = mapper_registry.map_imperatively(
        model.MealFood,
        meal_foods,
        properties={
            "meal": relationship("Meal", back_populates="foods"),
            "food_item": relationship("FoodItem")
        }
    )
    
    meal_mapper = mapper_registry.map_imperatively(
        model.Meal,
        meals,
        properties={
            "foods": relationship(model.MealFood, collection_class=list, back_populates="meal"),
            "_user": relationship("User"),
            "eating_day": relationship("EatingDay", back_populates="meals")
        }
    )
    
    eating_day_mapper = mapper_registry.map_imperatively(
        model.EatingDay,
        eating_days,
        properties={
            "meals": relationship(model.Meal, collection_class=list, back_populates="eating_day"),
            "_user": relationship("User", back_populates="eating_days")
        }
    )