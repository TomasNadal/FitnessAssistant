import pytest
from src.training_sessions.domain.models import User, Meal, EatingDay, FoodItem, Recipe, RecipeIngredient, MealFood
from datetime import datetime, timedelta, date


@pytest.fixture
def sample_user():
    return User(phone_number='+34612345678', name="Test User", gender="Male")


@pytest.fixture
def sample_food_items():
    return [
        FoodItem(
            name="Chicken Breast",
            brand=None,
            serving_size_grams=100.0,
            calories_per_100g=165.0,
            protein_per_100g=31.0,
            carbs_per_100g=0.0,
            fat_per_100g=3.6,
            fiber_per_100g=0.0,
            source="user-created",
            verified=True
        ),
        FoodItem(
            name="Brown Rice",
            brand=None,
            serving_size_grams=100.0,
            calories_per_100g=112.0,
            protein_per_100g=2.6,
            carbs_per_100g=23.5,
            fat_per_100g=0.9,
            fiber_per_100g=1.8,
            source="user-created",
            verified=True
        ),
        FoodItem(
            name="Protein Bar",
            brand="FitBrand",
            serving_size_grams=60.0,
            calories_per_100g=333.0,
            protein_per_100g=25.0,
            carbs_per_100g=30.0,
            fat_per_100g=10.0,
            fiber_per_100g=5.0,
            source="API",
            verified=True
        )
    ]


def test_food_item_creation():
    food = FoodItem(
        name="Apple",
        brand=None,
        serving_size_grams=100.0,
        calories_per_100g=52.0,
        protein_per_100g=0.3,
        carbs_per_100g=14.0,
        fat_per_100g=0.2,
        fiber_per_100g=2.4,
        source="user-created",
        verified=True
    )
    
    assert food.name == "Apple"
    assert food.brand is None
    assert food.serving_size_grams == 100.0
    assert food.calories_per_100g == 52.0
    assert food.protein_per_100g == 0.3
    assert food.carbs_per_100g == 14.0
    assert food.fat_per_100g == 0.2
    assert food.fiber_per_100g == 2.4
    assert food.source == "user-created"
    assert food.verified is True


def test_food_item_equality():
    food1 = FoodItem(
        name="Apple",
        brand=None,
        serving_size_grams=100.0,
        calories_per_100g=52.0,
        protein_per_100g=0.3,
        carbs_per_100g=14.0,
        fat_per_100g=0.2,
        fiber_per_100g=2.4,
        source="user-created",
        verified=True
    )
    
    food2 = FoodItem(
        name="Apple",
        brand=None,
        serving_size_grams=150.0,  # Different serving size
        calories_per_100g=55.0,    # Different calories
        protein_per_100g=0.4,      # Different protein
        carbs_per_100g=15.0,       # Different carbs
        fat_per_100g=0.3,          # Different fat
        fiber_per_100g=2.5,        # Different fiber
        source="API",              # Different source
        verified=False             # Different verification
    )
    
    food3 = FoodItem(
        name="APPLE",  # Same name but different case
        brand=None,
        serving_size_grams=100.0,
        calories_per_100g=52.0,
        protein_per_100g=0.3,
        carbs_per_100g=14.0,
        fat_per_100g=0.2,
        fiber_per_100g=2.4,
        source="user-created",
        verified=True
    )
    
    food4 = FoodItem(
        name="Apple",
        brand="OrganicFarms",  # Different brand
        serving_size_grams=100.0,
        calories_per_100g=52.0,
        protein_per_100g=0.3,
        carbs_per_100g=14.0,
        fat_per_100g=0.2,
        fiber_per_100g=2.4,
        source="user-created",
        verified=True
    )
    
    # Same name, no brand should be equal despite other differences
    assert food1 == food2
    
    # Case insensitive name comparison
    assert food1 == food3
    
    # Different brand should make them not equal
    assert food1 != food4


def test_meal_creation(sample_user, sample_food_items):
    now = datetime.now()
    meal = Meal(date=now, meal_type="Lunch", user=sample_user)
    
    assert meal.date == now
    assert meal.meal_type == "Lunch"
    assert meal._user == sample_user
    assert meal.foods == []


def test_meal_add_food(sample_user, sample_food_items):
    now = datetime.now()
    meal = Meal(date=now, meal_type="Dinner", user=sample_user)
    
    # Add chicken breast (100g)
    meal_food = meal.add_food(sample_food_items[0], 100.0)
    
    assert len(meal.foods) == 1
    assert meal.foods[0] == meal_food
    assert meal.foods[0].food_item == sample_food_items[0]
    assert meal.foods[0].amount_grams == 100.0


def test_meal_nutrition_calculations(sample_user, sample_food_items):
    now = datetime.now()
    meal = Meal(date=now, meal_type="Lunch", user=sample_user)
    
    # Add 150g of chicken breast
    meal.add_food(sample_food_items[0], 150.0)
    
    # Add 200g of brown rice
    meal.add_food(sample_food_items[1], 200.0)
    
    # Expected calculations:
    # Chicken: 150g * (165 cal / 100g) = 247.5 cal
    # Rice: 200g * (112 cal / 100g) = 224 cal
    # Total: 471.5 cal
    assert meal.get_total_calories() == pytest.approx(471.5)
    
    # Protein: (150g * 31/100g) + (200g * 2.6/100g) = 46.5 + 5.2 = 51.7g
    assert meal.get_total_protein() == pytest.approx(51.7)
    
    # Carbs: (150g * 0/100g) + (200g * 23.5/100g) = 0 + 47 = 47g
    assert meal.get_total_carbs() == pytest.approx(47.0)
    
    # Fat: (150g * 3.6/100g) + (200g * 0.9/100g) = 5.4 + 1.8 = 7.2g
    assert meal.get_total_fat() == pytest.approx(7.2)


def test_meal_equality(sample_user):
    now = datetime.now()
    
    meal1 = Meal(date=now, meal_type="Breakfast", user=sample_user)
    meal2 = Meal(date=now, meal_type="Breakfast", user=sample_user)
    meal3 = Meal(date=now, meal_type="Lunch", user=sample_user)
    
    another_user = User(phone_number='+34687654321', name="Another User", gender="Female")
    meal4 = Meal(date=now, meal_type="Breakfast", user=another_user)
    
    # Same date, type, and user should be equal
    assert meal1 == meal2
    
    # Different meal type should not be equal
    assert meal1 != meal3
    
    # Different user should not be equal
    assert meal1 != meal4


def test_meal_food_calculations(sample_food_items):
    now = datetime.now()
    meal = Meal(date=now, meal_type="Snack")
    
    # Create a MealFood with 75g of protein bar
    meal_food = MealFood(meal=meal, food_item=sample_food_items[2], amount_grams=75.0)
    
    # Expected calculations for 75g of protein bar:
    # Calories: 75g * (333 cal / 100g) = 249.75 cal
    assert meal_food.get_calories() == pytest.approx(249.75)
    
    # Protein: 75g * (25g / 100g) = 18.75g
    assert meal_food.get_protein() == pytest.approx(18.75)
    
    # Carbs: 75g * (30g / 100g) = 22.5g
    assert meal_food.get_carbs() == pytest.approx(22.5)
    
    # Fat: 75g * (10g / 100g) = 7.5g
    assert meal_food.get_fat() == pytest.approx(7.5)
    
    # Fiber: 75g * (5g / 100g) = 3.75g
    assert meal_food.get_fiber() == pytest.approx(3.75)


def test_recipe_creation(sample_user):
    recipe = Recipe(name="Chicken Rice Bowl", servings=2, user=sample_user)
    
    assert recipe.name == "Chicken Rice Bowl"
    assert recipe.servings == 2
    assert recipe._user == sample_user
    assert recipe.ingredients == []


def test_recipe_add_ingredients(sample_user, sample_food_items):
    recipe = Recipe(name="Protein Meal", servings=1, user=sample_user)
    
    # Add 200g chicken
    ingredient1 = recipe.add_ingredient(sample_food_items[0], 200.0)
    
    # Add 150g rice
    ingredient2 = recipe.add_ingredient(sample_food_items[1], 150.0)
    
    assert len(recipe.ingredients) == 2
    assert recipe.ingredients[0] == ingredient1
    assert recipe.ingredients[1] == ingredient2
    assert recipe.ingredients[0].food_item == sample_food_items[0]
    assert recipe.ingredients[0].amount_grams == 200.0
    assert recipe.ingredients[1].food_item == sample_food_items[1]
    assert recipe.ingredients[1].amount_grams == 150.0


def test_recipe_nutrition_calculations(sample_user, sample_food_items):
    recipe = Recipe(name="Protein Meal", servings=2, user=sample_user)
    
    # Add 200g chicken
    recipe.add_ingredient(sample_food_items[0], 200.0)
    
    # Add 150g rice
    recipe.add_ingredient(sample_food_items[1], 150.0)
    
    # Expected calculations:
    # Chicken: 200g * (165 cal / 100g) = 330 cal
    # Rice: 150g * (112 cal / 100g) = 168 cal
    # Total: 498 cal
    # Per serving (2 servings): 249 cal
    
    assert recipe.get_total_calories() == pytest.approx(498.0)
    assert recipe.get_calories_per_serving() == pytest.approx(249.0)


def test_recipe_equality(sample_user):
    user2 = User(phone_number='+34698765432', name="Another User", gender="Female")
    
    recipe1 = Recipe(name="Protein Bowl", servings=1, user=sample_user)
    recipe2 = Recipe(name="Protein Bowl", servings=2, user=sample_user)  # Different servings
    recipe3 = Recipe(name="PROTEIN BOWL", servings=1, user=sample_user)  # Different case
    recipe4 = Recipe(name="Protein Bowl", servings=1, user=user2)  # Different user
    
    # Same name and user should be equal despite different servings
    assert recipe1 == recipe2
    
    # Case insensitive name comparison
    assert recipe1 == recipe3
    
    # Different user should make them not equal
    assert recipe1 != recipe4


def test_eating_day_creation():
    today = datetime.now()
    eating_day = EatingDay(date=today)
    
    assert eating_day.date == today
    assert eating_day.meals == []


def test_eating_day_add_meal(sample_user):
    today = datetime.now()
    eating_day = EatingDay(date=today)
    
    breakfast = Meal(date=today, meal_type="Breakfast", user=sample_user)
    lunch = Meal(date=today, meal_type="Lunch", user=sample_user)
    
    eating_day.add_meal(breakfast)
    eating_day.add_meal(lunch)
    
    assert len(eating_day.meals) == 2
    assert eating_day.meals[0] == breakfast
    assert eating_day.meals[1] == lunch


def test_eating_day_nutrition_calculations(sample_user, sample_food_items):
    today = datetime.now()
    eating_day = EatingDay(date=today)
    
    # Create breakfast with protein bar
    breakfast = Meal(date=today, meal_type="Breakfast", user=sample_user)
    breakfast.add_food(sample_food_items[2], 60.0)  # One protein bar
    
    # Create lunch with chicken and rice
    lunch = Meal(date=today, meal_type="Lunch", user=sample_user)
    lunch.add_food(sample_food_items[0], 150.0)  # 150g chicken
    lunch.add_food(sample_food_items[1], 200.0)  # 200g rice
    
    eating_day.add_meal(breakfast)
    eating_day.add_meal(lunch)
    
    # Expected calculations:
    # Breakfast: 60g * (333 cal / 100g) = 199.8 cal
    # Lunch: (150g * 165/100g) + (200g * 112/100g) = 247.5 + 224 = 471.5 cal
    # Total: 199.8 + 471.5 = 671.3 cal
    
    assert eating_day.get_total_calories() == pytest.approx(671.3)
    
    # Protein: (60g * 25/100g) + (150g * 31/100g) + (200g * 2.6/100g) = 15 + 46.5 + 5.2 = 66.7g
    # Carbs: (60g * 30/100g) + (150g * 0/100g) + (200g * 23.5/100g) = 18 + 0 + 47 = 65g
    # Fat: (60g * 10/100g) + (150g * 3.6/100g) + (200g * 0.9/100g) = 6 + 5.4 + 1.8 = 13.2g
    
    protein, carbs, fat = eating_day.get_total_macros()
    assert protein == pytest.approx(66.7)
    assert carbs == pytest.approx(65.0)
    assert fat == pytest.approx(13.2)


def test_eating_day_equality():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    eating_day1 = EatingDay(date=today)
    eating_day2 = EatingDay(date=today)
    eating_day3 = EatingDay(date=tomorrow)
    
    # Same date should be equal
    assert eating_day1 == eating_day2
    
    # Different date should not be equal
    assert eating_day1 != eating_day3


def test_user_eating_day_management(sample_user):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Test get_eating_day_today creates a new eating day if none exists
    eating_day = sample_user.get_eating_day_today()
    assert len(sample_user.eating_days) == 1
    assert eating_day.date.date() == today.date()
    
    # Test get_eating_day_today returns existing eating day
    same_eating_day = sample_user.get_eating_day_today()
    assert len(sample_user.eating_days) == 1  # No new eating day created
    assert same_eating_day == eating_day
    
    # Test get_eating_day_given_date with non-existent date
    assert sample_user.get_eating_day_given_date(yesterday) is None
    
    # Test add_eating_day
    yesterday_eating_day = EatingDay(date=yesterday)
    sample_user.add_eating_day(yesterday_eating_day)
    assert len(sample_user.eating_days) == 2
    
    # Test get_eating_day_given_date with existing date
    retrieved_day = sample_user.get_eating_day_given_date(yesterday)
    assert retrieved_day == yesterday_eating_day


def test_user_add_meal(sample_user, sample_food_items):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    
    # Create meals
    breakfast = Meal(date=today, meal_type="Breakfast", user=sample_user)
    lunch = Meal(date=today, meal_type="Lunch", user=sample_user)
    yesterday_dinner = Meal(date=yesterday, meal_type="Dinner", user=sample_user)
    
    # Add meals for today
    sample_user.add_meal(breakfast)
    sample_user.add_meal(lunch)
    
    # Add meal for yesterday
    sample_user.add_meal_given_date(yesterday_dinner, yesterday)
    
    # Check today's eating day
    today_eating_day = sample_user.get_eating_day_today()
    assert len(today_eating_day.meals) == 2
    assert breakfast in today_eating_day.meals
    assert lunch in today_eating_day.meals
    
    # Check yesterday's eating day
    yesterday_eating_day = sample_user.get_eating_day_given_date(yesterday)
    assert len(yesterday_eating_day.meals) == 1
    assert yesterday_dinner in yesterday_eating_day.meals


def test_recipe_ingredient_calculations(sample_food_items):
    """Test calculations for recipe ingredients"""
    recipe = Recipe(name="Test Recipe", servings=4)
    
    # Add 150g of chicken breast
    ingredient = RecipeIngredient(recipe=recipe, food_item=sample_food_items[0], amount_grams=150.0)
    
    # Expected calculations for 150g of chicken breast:
    # Calories: 150g * (165 cal / 100g) = 247.5 cal
    assert ingredient.get_calories() == pytest.approx(247.5)
    
    # Protein: 150g * (31g / 100g) = 46.5g
    assert ingredient.get_protein() == pytest.approx(46.5)
    
    # Carbs: 150g * (0g / 100g) = 0g
    assert ingredient.get_carbs() == pytest.approx(0.0)
    
    # Fat: 150g * (3.6g / 100g) = 5.4g
    assert ingredient.get_fat() == pytest.approx(5.4)


def test_recipe_macronutrient_calculations(sample_user, sample_food_items):
    """Test that recipes correctly calculate macronutrients"""
    recipe = Recipe(name="Balanced Meal", servings=2, user=sample_user)
    
    # Add 200g chicken
    recipe.add_ingredient(sample_food_items[0], 200.0)
    
    # Add 150g rice
    recipe.add_ingredient(sample_food_items[1], 150.0)
    
    # Expected protein: (200g * 31/100g) + (150g * 2.6/100g) = 62 + 3.9 = 65.9g
    # Expected carbs: (200g * 0/100g) + (150g * 23.5/100g) = 0 + 35.25 = 35.25g
    # Expected fat: (200g * 3.6/100g) + (150g * 0.9/100g) = 7.2 + 1.35 = 8.55g
    
    total_protein = sum(ingredient.get_protein() for ingredient in recipe.ingredients)
    total_carbs = sum(ingredient.get_carbs() for ingredient in recipe.ingredients)
    total_fat = sum(ingredient.get_fat() for ingredient in recipe.ingredients)
    
    assert total_protein == pytest.approx(65.9)
    assert total_carbs == pytest.approx(35.25)
    assert total_fat == pytest.approx(8.55)


def test_add_duplicate_meal_to_eating_day(sample_user):
    """Test that adding the same meal twice doesn't duplicate it"""
    today = datetime.now()
    eating_day = EatingDay(date=today)
    
    meal = Meal(date=today, meal_type="Breakfast", user=sample_user)
    
    # Add the meal twice
    eating_day.add_meal(meal)
    eating_day.add_meal(meal)
    
    # Should only be added once
    assert len(eating_day.meals) == 1 