import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import asyncio
from unittest.mock import AsyncMock

from app.main import app
from app.db.session import get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Avoid actual DB connections
async def override_get_db():
    mock_session = AsyncMock()
    
    class MockResult:
        def scalar_one_or_none(self):
            class MockModel:
                id = "mock_id"
                title = "Mock Title"
                candidate_name = "Mock Name"
                raw_text = "Mock Text"
                description_text = "Mock Desc"
            return MockModel()
            
        def __iter__(self):
            # For iteration in matching function
            yield ("mock_id", "Title", "Company", 0.9, 0.8, 0.7)
            
    mock_session.execute.return_value = MockResult()
    yield mock_session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    class MockEmbeddingResponse:
        @property
        def data(self):
            class Item:
                embedding = [0.1] * 1536
            return [Item()]
            
    class MockChatResponse:
        @property
        def choices(self):
            class Msg:
                class Parsed:
                    match_score = 85
                    strengths = ["Python"]
                    gaps = ["Docker"]
                    missing_keywords = ["K8s"]
                    recommended_cv_bullets = ["Built API"]
                    learning_plan = [{"topic": "Docker", "reason": "needed"}]
                parsed = Parsed()
            class Choice:
                message = Msg()
            return [Choice()]

    async def mock_embed_create(*args, **kwargs):
        return MockEmbeddingResponse()
        
    async def mock_chat_parse(*args, **kwargs):
        return MockChatResponse()

    monkeypatch.setattr("app.services.openai_client.client.embeddings.create", mock_embed_create)
    monkeypatch.setattr("app.services.openai_client.client.beta.chat.completions.parse", mock_chat_parse)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
