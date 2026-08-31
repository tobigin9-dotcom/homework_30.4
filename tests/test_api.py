import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_and_list_recipes(client: AsyncClient):
    response = await client.post(
        "/recipes/",
        json={
            "title": "Борщ",
            "cooking_time": 90,
            "ingredients": ["свёкла — 2 шт", "капуста — 300 г"],
            "description": "Сварить бульон, добавить овощи.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Борщ"
    assert data["views"] == 0
    assert data["ingredients"] == ["свёкла — 2 шт", "капуста — 300 г"]

    response = await client.get("/recipes/")
    assert response.status_code == 200
    recipes = response.json()
    assert len(recipes) == 1
    assert recipes[0]["title"] == "Борщ"


@pytest.mark.asyncio
async def test_recipe_detail_increments_views(client: AsyncClient):
    create_resp = await client.post(
        "/recipes/",
        json={
            "title": "Омлет",
            "cooking_time": 10,
            "ingredients": ["яйца — 3 шт"],
            "description": "Взбить яйца, обжарить.",
        },
    )
    recipe_id = create_resp.json()["id"]

    resp1 = await client.get(f"/recipes/{recipe_id}")
    assert resp1.status_code == 200
    assert resp1.json()["views"] == 1

    resp2 = await client.get(f"/recipes/{recipe_id}")
    assert resp2.json()["views"] == 2


@pytest.mark.asyncio
async def test_sorting_by_views_then_cooking_time(client: AsyncClient):
    await client.post("/recipes/", json={
        "title": "A", "cooking_time": 30, "ingredients": ["x"], "description": "..."
    })
    await client.post("/recipes/", json={
        "title": "B", "cooking_time": 10, "ingredients": ["x"], "description": "..."
    })
    await client.post("/recipes/", json={
        "title": "C", "cooking_time": 20, "ingredients": ["x"], "description": "..."
    })

    recipes = (await client.get("/recipes/")).json()
    ids = {r["title"]: r["id"] for r in recipes}

    await client.get(f"/recipes/{ids['B']}")
    await client.get(f"/recipes/{ids['B']}")
    await client.get(f"/recipes/{ids['A']}")

    recipes = (await client.get("/recipes/")).json()
    titles = [r["title"] for r in recipes]
    assert titles == ["B", "A", "C"]


@pytest.mark.asyncio
async def test_recipe_not_found(client: AsyncClient):
    response = await client.get("/recipes/9999")
    assert response.status_code == 404
