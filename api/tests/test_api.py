from fastapi.testclient import TestClient

from app.main import app, get_db


class FakeCollection:
    def __init__(self):
        self.docs = {}

    def get(self, key):
        return self.docs.get(key)

    def all(self):
        return list(self.docs.values())

    def insert(self, doc):
        self.docs[doc["_key"]] = doc

    def update(self, doc):
        self.docs[doc["_key"]].update(doc)

    def delete(self, key, ignore_missing=False):
        return self.docs.pop(key, None) is not None


class FakeDb:
    def __init__(self):
        self.users = FakeCollection()

    def collection(self, name):
        return self.users


client = TestClient(app)


def test_crud():
    fake = FakeDb()
    app.dependency_overrides[get_db] = lambda: fake
    try:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.post("/users/eve", json={"name": "Eve", "age": 22}).status_code == 201
        assert client.post("/users/eve", json={"name": "Eve", "age": 22}).status_code == 409
        assert client.put("/users/eve", json={"name": "Eve", "age": 23}).json()["age"] == 23
        assert client.get("/users").json() == [{"key": "eve", "name": "Eve", "age": 23}]
        assert client.delete("/users/eve").status_code == 204
        assert client.get("/users/eve").status_code == 404
    finally:
        app.dependency_overrides.clear()
