"""
SQL Alchemy models declaration.
https://docs.sqlalchemy.org/en/14/orm/declarative_styles.html#example-two-dataclasses-with-declarative-table
Dataclass style for powerful autocompletion support.

https://alembic.sqlalchemy.org/en/latest/tutorial.html
Note, it is used by alembic migrations logic, see `alembic/env.py`

Alembic shortcuts:
# create migration
alembic revision --autogenerate -m "migration_name"

# apply all migrations
alembic upgrade head

Example for more complex constraint:
(https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html#declarative-table-configuration)
(https://docs.sqlalchemy.org/en/14/core/constraints.html#schema-unique-constraint)
class MyClass(Base):
    __tablename__ = "sometable"
    __table_args__ = (
        ForeignKeyConstraint(["id"], ["remote_table.id"]),
        UniqueConstraint("col2", "col3", name="uniq_col23"),
        {"autoload": True},
    )
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Union, List

from sqlalchemy import func
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import (
    String,
    SmallInteger,
    Integer,
    BigInteger,
    DateTime,
    Date,
    Enum,
    Text,
)
from sqlalchemy.orm import registry, relationship

Base = registry()


@Base.mapped
@dataclass
class Ingredient:
    __tablename__ = "ingredient"
    __sa_dataclass_metadata_key__ = "sa"

    ingredient_id: int = field(
        init=False,
        metadata={"sa": Column(Integer, primary_key=True)},
    )
    name: str = field(metadata={"sa": Column(Text, nullable=False, unique=True)})
    created_at: datetime = field(
        init=False,
        metadata={"sa": Column(DateTime, nullable=False, server_default=func.now())},
    )
    last_seen: datetime = field(
        init=False,
        metadata={
            "sa": Column(
                DateTime, nullable=False, onupdate=func.now(), server_default=func.now()
            )
        },
    )

    recipes_ingredient: List[RecipeIngredient] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "RecipeIngredient",
                back_populates="ingredient",
                lazy="joined",
            )
        },
    )

    __mapper_args__ = {"eager_defaults": True}


@Base.mapped
@dataclass
class RecipeIngredient:
    __tablename__ = "recipe_ingredient"
    __sa_dataclass_metadata_key__ = "sa"

    recipe_ingredient_id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )
    recipe_id: int = field(
        init=False,
        metadata={
            "sa": Column(Integer, ForeignKey("recipe.recipe_id", ondelete="CASCADE"))
        },
    )
    ingredient_id: int = field(
        init=False,
        metadata={
            "sa": Column(
                Integer, ForeignKey("ingredient.ingredient_id", ondelete="CASCADE")
            )
        },
    )
    quantity: int = field(metadata={"sa": Column(Integer, nullable=False)})

    ingredient: Ingredient = field(
        init=False,
        metadata={
            "sa": relationship("Ingredient", back_populates="recipes_ingredient")
        },
    )

    __mapper_args__ = {"eager_defaults": True}


@Base.mapped
@dataclass
class Recipe:
    __tablename__ = "recipe"
    __sa_dataclass_metadata_key__ = "sa"

    recipe_id: int = field(
        init=False,
        metadata={"sa": Column(Integer, primary_key=True)},
    )
    cake_id: int = field(
        init=False,
        metadata={
            "sa": Column(Integer, ForeignKey("cake.cake_id", ondelete="CASCADE"))
        },
    )
    name: str = field(metadata={"sa": Column(String, nullable=False)})
    date: datetime = field(
        init=False,
        metadata={"sa": Column(DateTime, nullable=False, server_default=func.now())},
    )

    recipe_ingredients: List[RecipeIngredient] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "RecipeIngredient",
                lazy="joined",
            )
        },
    )

    __mapper_args__ = {"eager_defaults": True}


@Base.mapped
@dataclass
class Cake:
    __tablename__ = "cake"
    __sa_dataclass_metadata_key__ = "sa"

    cake_id: int = field(
        init=False,
        metadata={"sa": Column(Integer, primary_key=True)},
    )
    name: str = field(metadata={"sa": Column(String(255), unique=True, nullable=False)})
    created_at: datetime = field(
        init=False,
        metadata={"sa": Column(DateTime, nullable=False, server_default=func.now())},
    )

    recipes: List[Recipe] = field(
        default_factory=list,
        metadata={
            "sa": relationship(
                "Recipe",
                lazy="joined",
            )
        },
    )

    __mapper_args__ = {"eager_defaults": True}
