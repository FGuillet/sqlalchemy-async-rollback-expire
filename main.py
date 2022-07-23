import random
from datetime import datetime, timezone
import asyncio
from typing import List
import copy

from faker import Faker
import sqlalchemy
from sqlalchemy import select, update, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import models

async_engine = create_async_engine(
    "sqlite+aiosqlite:///./cakes.db", pool_pre_ping=True, echo=True
)
async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore


async def create_cakes(session: AsyncSession, nbr: int = 10) -> List[models.Cake]:
    cakes = []
    for _ in range(0, nbr):
        fake = Faker()
        cake = models.Cake(
            name=fake.name(),
        )
        cake.created_at = fake.date_time_between_dates(
            datetime_start=datetime(2022, 6, 1, 0, 0, 0).replace(tzinfo=timezone.utc),
            datetime_end=datetime(2022, 6, 30, 23, 59, 59).replace(tzinfo=timezone.utc),
        )

        session.add(cake)
        await session.commit()
        await session.refresh(cake)

        cakes.append(cake)

    return cakes


async def get_recipe_ingredients(
    session: AsyncSession,
    cake: models.Cake,
    ingredients: List[models.Ingredient],
    nbr: int = 10,
):
    recipe_ingredients = []
    for _ in range(0, nbr):
        # We want some ingredient shared by recipe
        ingredient: models.Ingredient = random.choice(ingredients)
        print(ingredient.name)

        # Upsert
        try:
            session.add(ingredient)
            await session.commit()
            await session.refresh(ingredient)
        except sqlalchemy.exc.IntegrityError:
            await session.rollback()
            await session.execute(
                update(models.Ingredient)
                .where(models.Ingredient.name == ingredient.name)
                .values(
                    name=ingredient.name,
                )
            )

        recipe_ingredient = models.RecipeIngredient(quantity=random.randint(10, 500))

        recipe_ingredient.ingredient_id = ingredient.ingredient_id

        recipe_ingredients.append(recipe_ingredient)

        # For a complete arbitrary reason, I want to use cake object sometimes
        print(f"Cake id: {cake.cake_id}")

    return recipe_ingredients


async def create_recipe(
    session: AsyncSession,
    cakes: List[models.Cake],
    ingredients: List[models.Ingredient],
    by_cake: int = 2,
) -> List[models.Recipe]:
    for cake in cakes:
        for _ in range(0, by_cake):
            fake = Faker()
            recipe = models.Recipe(name=fake.name())

            recipe_ingredients = await get_recipe_ingredients(
                session, cake, ingredients
            )

            recipe.recipe_ingredients = recipe_ingredients

            session.add(recipe)
            await session.commit()


def get_ingredients(nbr: int = 10) -> List[models.Ingredient]:
    ingredients = []
    for _ in range(0, nbr):
        fake = Faker()

        ingredient = models.Ingredient(name=fake.name())

        ingredients.append(ingredient)
        ingredients.append(copy.deepcopy(ingredient))

    return ingredients


async def main():
    async with async_session() as session:
        cakes = await create_cakes(session, 2)
        ingredients = get_ingredients(2)
        random.shuffle(ingredients)

        await create_recipe(session, cakes, ingredients, 2)


if __name__ == "__main__":
    asyncio.run(main())
