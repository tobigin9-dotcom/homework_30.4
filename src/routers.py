import json

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Recipe
from schemas import RecipeCreate, RecipeDetail, RecipeListItem

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


@router.get(
    "/",
    response_model=list[RecipeListItem],
    summary="Получить список рецептов",
    description=(
        "Возвращает все рецепты. "
        "Рецепты сортируются по количеству просмотров "
        "по убыванию. Если количество просмотров одинаковое, "
        "сначала возвращается рецепт с меньшим временем приготовления."
    ),
)
async def get_recipes(
    db: AsyncSession = Depends(get_db),
) -> list[RecipeListItem]:
    """
    Получить список всех рецептов.

    Сортировка:
    1. количество просмотров — по убыванию;
    2. время приготовления — по возрастанию.

    Args:
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        Список рецептов для таблицы фронтенда.
    """

    query = select(Recipe).order_by(
        Recipe.views.desc(),
        Recipe.cooking_time.asc(),
    )

    result = await db.execute(query)
    recipes = result.scalars().all()

    return [RecipeListItem.model_validate(recipe) for recipe in recipes]


@router.get(
    "/{recipe_id}",
    response_model=RecipeDetail,
    summary="Получить рецепт",
    description=(
        "Возвращает подробную информацию о конкретном рецепте. "
        "При каждом успешном открытии рецепта его количество "
        "просмотров увеличивается на единицу."
    ),
    responses={
        404: {
            "description": "Рецепт не найден",
        },
    },
)
async def get_recipe(
    recipe_id: int = Path(
        ...,
        gt=0,
        description="ID рецепта.",
        examples=[1],
    ),
    db: AsyncSession = Depends(get_db),
) -> RecipeDetail:
    """
    Получить подробную информацию о рецепте.

    При открытии рецепта увеличивается его счётчик просмотров.

    Args:
        recipe_id: ID рецепта.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        Полная информация о рецепте.

    Raises:
        HTTPException: Если рецепт отсутствует.
    """

    result = await db.execute(select(Recipe).where(Recipe.id == recipe_id))

    recipe = result.scalar_one_or_none()

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    recipe.views += 1

    await db.commit()
    await db.refresh(recipe)

    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        ingredients=json.loads(recipe.ingredients),
        description=recipe.description,
        views=recipe.views,
    )


@router.post(
    "/",
    response_model=RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецепт",
    description=("Создаёт новый рецепт. " "Новый рецепт получает 0 просмотров."),
    responses={
        201: {
            "description": "Рецепт успешно создан",
        },
    },
)
async def create_recipe(
    recipe_data: RecipeCreate,
    db: AsyncSession = Depends(get_db),
) -> RecipeDetail:
    """
    Создать новый рецепт.

    Args:
        recipe_data: Данные нового рецепта.
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        Созданный рецепт.
    """

    recipe = Recipe(
        title=recipe_data.title,
        cooking_time=recipe_data.cooking_time,
        ingredients=json.dumps(
            recipe_data.ingredients,
            ensure_ascii=False,
        ),
        description=recipe_data.description,
        views=0,
    )

    db.add(recipe)

    await db.commit()
    await db.refresh(recipe)

    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        cooking_time=recipe.cooking_time,
        ingredients=recipe_data.ingredients,
        description=recipe.description,
        views=recipe.views,
    )
