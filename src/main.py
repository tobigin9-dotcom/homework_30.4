from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from models import Recipe
from routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Жизненный цикл приложения.

    При запуске создаются таблицы базы данных,
    если они ещё не существуют.
    """

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="CookBook API",
    description="""
# API кулинарной книги

Асинхронный REST API для работы с рецептами.

## Возможности

- получение списка рецептов;
- автоматическая сортировка рецептов по популярности;
- получение подробной информации о рецепте;
- автоматический подсчёт просмотров;
- создание новых рецептов.

## Сортировка

Список рецептов сортируется по двум параметрам:

1. `views` — количество просмотров по убыванию;
2. `cooking_time` — время приготовления по возрастанию,
   если количество просмотров одинаковое.

## Просмотры

Каждый успешный запрос `GET /recipes/{recipe_id}`
увеличивает количество просмотров рецепта на `1`.
""",
    version="1.0.0",
    contact={
        "name": "CookBook API",
    },
    lifespan=lifespan,
)

app.include_router(router)


@app.get(
    "/",
    tags=["Service"],
    summary="Проверка работы API",
)
async def root() -> dict[str, str]:
    """
    Проверяет доступность API.
    """

    return {
        "message": "CookBook API is running",
    }
