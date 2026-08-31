from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    """Данные для создания нового рецепта."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название блюда.",
        examples=["Курица с картофелем"],
    )

    cooking_time: int = Field(
        ...,
        gt=0,
        description="Время приготовления в минутах.",
        examples=[60],
    )

    ingredients: list[str] = Field(
        ...,
        min_length=1,
        description="Список ингредиентов.",
        examples=[
            [
                "курица — 500 г",
                "картофель — 400 г",
                "соль — 1 ч. л.",
            ]
        ],
    )

    description: str = Field(
        ...,
        min_length=1,
        description="Текстовое описание рецепта.",
        examples=["Нарезать картофель, добавить курицу и запекать 60 минут."],
    )


class RecipeListItem(BaseModel):
    """Рецепт для отображения в списке."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Уникальный идентификатор рецепта.",
        examples=[1],
    )

    title: str = Field(
        description="Название блюда.",
        examples=["Курица с картофелем"],
    )

    views: int = Field(
        description="Количество просмотров рецепта.",
        examples=[25],
    )

    cooking_time: int = Field(
        description="Время приготовления в минутах.",
        examples=[60],
    )


class RecipeDetail(BaseModel):
    """Полная информация о рецепте."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        description="Уникальный идентификатор рецепта.",
        examples=[1],
    )

    title: str = Field(
        description="Название блюда.",
        examples=["Курица с картофелем"],
    )

    cooking_time: int = Field(
        description="Время приготовления в минутах.",
        examples=[60],
    )

    ingredients: list[str] = Field(
        description="Список ингредиентов.",
        examples=[
            [
                "курица — 500 г",
                "картофель — 400 г",
                "соль — 1 ч. л.",
            ]
        ],
    )

    description: str = Field(
        description="Описание приготовления блюда.",
        examples=["Нарезать картофель, добавить курицу и запекать 60 минут."],
    )

    views: int = Field(
        description="Количество просмотров рецепта.",
        examples=[25],
    )
