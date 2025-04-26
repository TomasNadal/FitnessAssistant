from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import uuid
import logging


#WorkoutSession
class AlreadyActiveSession(Exception):
    pass

class AlreadyEndedSession(Exception):
    pass

class InvalidWorkoutSession(Exception):
    pass

class InvalidSeriesOrder(Exception):
    pass

#ExerciseSet
class InvalidNumberOfRepetitions(Exception):
    pass

class AlreadyHasRepetitions(Exception):
    pass

class InvalidSeries(Exception):
    pass

class InvalidRepetitionOrder(Exception):
    pass

class WorkoutSessionCompletedException(Exception):
    pass


# Pending here:
# - Add the different muscle groups
# - Add the different equipment
# - Add the different types of exercise
# - Add the different types of series
# - Add the different types of repetitions
# - Add the different types of workout sessions
# - Add the possible genders



'''
Food Models
'''

class EatingDay:
    def __init__(self, date: datetime):
        self.date = date
        self.meals = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_meal(self, meal: Meal):
        if meal not in self.meals:
            self.meals.append(meal)
            self.updated_at = datetime.now()
        
    def get_total_calories(self):
        return sum(meal.get_total_calories() for meal in self.meals)
    
    def get_total_macros(self):
        """Returns total protein, carbs, and fat for the day"""
        protein = sum(meal.get_total_protein() for meal in self.meals)
        carbs = sum(meal.get_total_carbs() for meal in self.meals)
        fat = sum(meal.get_total_fat() for meal in self.meals)
        return protein, carbs, fat
    
    def __eq__(self, other):
        if not isinstance(other, EatingDay):
            return False
        return self.date.date() == other.date.date()
    
    def __hash__(self):
        return hash(self.date.date())
        
    def __str__(self):
        return f'{self.date.date()} - {len(self.meals)} meals'


@dataclass
class FoodItem:
    name: str
    brand: Optional[str]
    serving_size_grams: float
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float
    source: str  # API, user-created, scraped
    verified: bool
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other):
        if not isinstance(other, FoodItem):
            return False
        return (self.name.lower() == other.name.lower() and 
                self.brand == other.brand)

    def __hash__(self):
        return hash((self.name.lower(), self.brand))


class Meal:
    def __init__(self, date: datetime, meal_type: str, user=None):
        self.date = date
        self.meal_type = meal_type  # breakfast, lunch, dinner, snack
        self._user = user
        self.foods = []  # Will contain MealFood objects
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_food(self, food_item: FoodItem, amount_grams: float):
        meal_food = MealFood(meal=self, food_item=food_item, amount_grams=amount_grams)
        self.foods.append(meal_food)
        self.updated_at = datetime.now()
        return meal_food
    
    def get_total_calories(self):
        return sum(food.get_calories() for food in self.foods)
    
    def get_total_protein(self):
        return sum(food.get_protein() for food in self.foods)
    
    def get_total_carbs(self):
        return sum(food.get_carbs() for food in self.foods)
    
    def get_total_fat(self):
        return sum(food.get_fat() for food in self.foods)
    
    def __eq__(self, other):
        if not isinstance(other, Meal):
            return False
        return (self.date == other.date and 
                self.meal_type == other.meal_type and
                self._user == other._user)
    
    def __hash__(self):
        return hash((self.date, self.meal_type, self._user))
    
    def __str__(self):
        return f'{self.meal_type} on {self.date.date()} - {len(self.foods)} items'


class MealFood:
    def __init__(self, meal: Meal, food_item: FoodItem, amount_grams: float):
        self.meal = meal
        self.food_item = food_item
        self.amount_grams = amount_grams
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_calories(self):
        return (self.food_item.calories_per_100g * self.amount_grams) / 100
    
    def get_protein(self):
        return (self.food_item.protein_per_100g * self.amount_grams) / 100
    
    def get_carbs(self):
        return (self.food_item.carbs_per_100g * self.amount_grams) / 100
    
    def get_fat(self):
        return (self.food_item.fat_per_100g * self.amount_grams) / 100
    
    def get_fiber(self):
        return (self.food_item.fiber_per_100g * self.amount_grams) / 100
    
    def __eq__(self, other):
        if not isinstance(other, MealFood):
            return False
        return (self.meal == other.meal and 
                self.food_item == other.food_item)
    
    def __hash__(self):
        return hash((self.meal, self.food_item))


class Recipe:
    def __init__(self, name: str, servings: int, user=None):
        self.name = name
        self.servings = servings
        self._user = user
        self.ingredients = []  # Will contain RecipeIngredient objects
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_ingredient(self, food_item: FoodItem, amount_grams: float):
        ingredient = RecipeIngredient(recipe=self, food_item=food_item, amount_grams=amount_grams)
        self.ingredients.append(ingredient)
        self.updated_at = datetime.now()
        return ingredient
    
    def get_total_calories(self):
        return sum(ingredient.get_calories() for ingredient in self.ingredients)
    
    def get_calories_per_serving(self):
        return self.get_total_calories() / self.servings if self.servings > 0 else 0
    
    def __eq__(self, other):
        if not isinstance(other, Recipe):
            return False
        return self.name.lower() == other.name.lower() and self._user == other._user
    
    def __hash__(self):
        return hash((self.name.lower(), self._user))


class RecipeIngredient:
    def __init__(self, recipe: Recipe, food_item: FoodItem, amount_grams: float):
        self.recipe = recipe
        self.food_item = food_item
        self.amount_grams = amount_grams
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_calories(self):
        return (self.food_item.calories_per_100g * self.amount_grams) / 100
    
    def get_protein(self):
        return (self.food_item.protein_per_100g * self.amount_grams) / 100
    
    def get_carbs(self):
        return (self.food_item.carbs_per_100g * self.amount_grams) / 100
    
    def get_fat(self):
        return (self.food_item.fat_per_100g * self.amount_grams) / 100
    
    def __eq__(self, other):
        if not isinstance(other, RecipeIngredient):
            return False
        return (self.recipe == other.recipe and 
                self.food_item == other.food_item)
    
    def __hash__(self):
        return hash((self.recipe, self.food_item))

'''
 Training Models
'''
class WorkoutSession:
    def __init__(self, started_at: datetime):
        self.start_time = started_at
        self.end_time = None
        self.exercise_sets = []
        self.notes = None
        self.rating = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def is_completed(self):
        return self.end_time is not None

    def __str__(self):
        return f'{self.start_time}-{self.end_time}-{self.exercise_sets}'

    def add_exercise_set(self, exercise_set: ExerciseSet):
        if exercise_set.workout_session != self:
            raise InvalidWorkoutSession

        previous_set = [exercise_set for exercise_set in self.exercise_sets if exercise_set.exercise == exercise_set.exercise]
        if exercise_set.set_number != previous_set.set_number + 1:
            raise InvalidSeriesOrder

        self.exercise_sets.append(exercise_set)


    def __eq__(self, other):
        if not isinstance(other, WorkoutSession):
            return False
        else:
            return self.start_time == other.start_time  

    def __hash__(self):
        return hash(self.start_time)



class ExerciseSet:
    def __init__(self, workout_session: WorkoutSession,
                    exercise: Exercise,
                    set_number: int,
                    weight_kg: float,
                    reps: int,
                    rir: Optional[int] = None,
                    notes: Optional[str] = None,
                    video_url: Optional[str] = None):

        if not workout_session.is_completed:
            raise WorkoutSessionCompletedException("Cannot add exercise sets to a completed workout session")

        self.workout_session = workout_session
        self.exercise = exercise
        self.set_number = set_number
        self.weight_kg = weight_kg
        self.reps = reps
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.rir = rir
        self.notes = notes
        self.video_url = video_url
        self.repetitions = []

    


    def add_repetitions(self, repetitions: List[ExerciseRepetition]):
        if len(self.repetitions) != 0:
            raise AlreadyHasRepetitions

        if len(repetitions) != self.reps:
            raise InvalidNumberOfRepetitions
        
        if sorted([repetition.number for repetition in repetitions]) != list(range(1, self.reps + 1)):
            raise InvalidRepetitionOrder

        for repetition in repetitions:
            self._add_repetition(repetition)

    def _add_repetition(self, repetition: ExerciseRepetition):
        self.repetitions.append(repetition)

    def __str__(self):
        return f'{self.exercise.name} - {self.set_number} - {self.weight} - {self.reps}'


@dataclass    
class ExerciseRepetition:
    number: int
    kg: float
    distance: float
    mean_velocity: float
    peak_velocity: float
    power: float
    

@dataclass
class Exercise:
    name: str
    description: str
    primary_muscle_group: str
    secondary_muscle_group: str
    equipment_needed: Optional[str] = None
    is_compound: Optional[bool] = False



    def __eq__(self, other):
        if not isinstance(other, Exercise):
            return False
        else:
            return self.name.lower() == other.name.lower()

    def __hash__(self):
        return hash(self.name)
    
    



### Things I will need to query easily:
'''

- User by telephone
- Session by day
- Exercise by name
- Series by number


Functions I will need to define in models:

- user.get_training_session: gets or creates training session 
- user.add_series(exercise_name: ... , series(list_of_dicts))
    - I receive series info, no rep by rep. Makes sense to add the complete series
    - The add_series function manages creating a new series object.
    - It adds the repetitions
    - Returns the data added. 


'''

class User:
    def __init__(self,
    phone_number: str,
    gender: str,
    name: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    surname: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    password_hash: Optional[str] = None):

        self.username = username
        self.email = email
        self.surname = surname
        self.date_of_birth = date_of_birth
        self.height = height
        self.weight = weight
        self.password_hash = password_hash
        self.phone_number = phone_number
        self.name = name
        self.gender = gender
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.workout_sessions = []
        self.eating_days = []
        self.messages = []

    def __eq__(self, other):
        if not isinstance(other,User):
            return False
        return (other.name == self.name) and (other.phone_number == self.phone_number)

    def __hash__(self):
        return hash(self.name, self.phone_number)


    def add_workout_session(self, workout_session: WorkoutSession):

        if len(self.workout_sessions) != 0 and self.workout_sessions[-1].end_time is None:
            raise AlreadyActiveSession

        self.workout_sessions.append(workout_session)


    def end_workout_session(self):
        time_now = datetime.now()
        if not self.workout_sessions[-1].is_completed:
            raise AlreadyEndedSession

        self.workout_sessions[-1].end_time = time_now

    def add_eating_day(self, eating_day: EatingDay):
        self.eating_days.append(eating_day)


    def get_eating_day_today(self):
        if self.eating_days == []:
            self.add_eating_day(EatingDay(datetime.now()))

        if self.eating_days[-1].date != datetime.now().date():
            self.add_eating_day(EatingDay(datetime.now()))
        
        return self.eating_days[-1]

    def get_eating_day_given_date(self, date: datetime):
        for eating_day in self.eating_days:
            if eating_day.date == date.date():
                return eating_day
        return None


    def add_meal(self, meal: Meal):
        eating_day = self.get_eating_day_today()
        eating_day.add_meal(meal)
        
    def add_meal_given_date(self, meal: Meal, date: datetime):
        eating_day = self.get_eating_day_given_date(date)
        if eating_day is None:
            self.add_eating_day(EatingDay(date))
            eating_day = self.get_eating_day_given_date(date)
        eating_day.add_meal(meal)   

    def __str__(self):
        return f'{self.name} - {self.phone_number}'

    def start_conversation(self, topic=None):
        conversation = Conversation(self, topic)
        return conversation

    def get_active_conversation(self):
        for msg in reversed(self.messages):
            if hasattr(msg, 'conversation') and msg.conversation.is_active():
                return msg.conversation
        return None


'''
Whatsapp Models
'''

class Message:
    def __init__(self, 
                 user: User,
                 content: str,
                 direction: str,  # 'inbound' or 'outbound'
                 message_type: str,  # 'text', 'audio', 'image', 'video', 'document'
                 timestamp: datetime = None,
                 media_url: Optional[str] = None,
                 media_id: Optional[str] = None,
                 model_used: Optional[str] = None,
                 tokens_used: Optional[int] = None,
                 context_id: Optional[str] = None,
                 intent_detected: Optional[str] = None,
                 processing_time: Optional[float] = None,
                 error: Optional[str] = None):
        
        self.user = user
        self.content = content
        self.direction = direction
        self.message_type = message_type
        self.timestamp = timestamp or datetime.now()
        self.media_url = media_url
        self.media_id = media_id
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.context_id = context_id
        self.intent_detected = intent_detected
        self.processing_time = processing_time
        self.error = error
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Add the message to the user's messages list
        if user and self not in user.messages:
            user.messages.append(self)
    
    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return (self.user == other.user and 
                self.timestamp == other.timestamp and
                self.content == other.content and
                self.direction == other.direction)
    
    def __hash__(self):
        return hash((self.user, self.timestamp, self.content, self.direction))
    
    def __str__(self):
        direction_str = "→" if self.direction == "outbound" else "←"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} {direction_str} {self.message_type}: {self.content[:30]}{'...' if len(self.content) > 30 else ''}"


#   TODO: Add logic to decide when to create new conversation
class Conversation:
    def __init__(self, user: User, topic: Optional[str] = None):
        self.user = user
        self.topic = topic
        self.messages = []
        self.started_at = datetime.now()
        self.ended_at = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_message(self, message: Message):
        if message.user != self.user:
            raise ValueError("Message user does not match conversation user")
        
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def end_conversation(self):
        self.ended_at = datetime.now()
        self.updated_at = datetime.now()
    
    def is_active(self):
        return self.ended_at is None
    
    def get_last_message(self):
        if not self.messages:
            return None
        return self.messages[-1]
    
    def get_messages_by_direction(self, direction):
        return [msg for msg in self.messages if msg.direction == direction]
    
    def get_total_tokens_used(self):
        return sum(msg.tokens_used or 0 for msg in self.messages)
    
    def __eq__(self, other):
        if not isinstance(other, Conversation):
            return False
        return (self.user == other.user and 
                self.started_at == other.started_at)
    
    def __hash__(self):
        return hash((self.user, self.started_at))
    
    def __str__(self):
        return f"Conversation with {self.user} started at {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"