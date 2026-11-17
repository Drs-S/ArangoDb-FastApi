import os
from functools import lru_cache

from arango import ArangoClient
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ArangoDb-FastApi", description="CRUD et recommandations sur ArangoDB")


@lru_cache
def get_db():
    client = ArangoClient(hosts=os.getenv("ARANGO_HOST", "http://localhost:8529"))
    return client.db(
        os.getenv("ARANGO_DB", "demo"),
        username=os.getenv("ARANGO_USER", "root"),
        password=os.getenv("ARANGO_PASSWORD", ""),
    )


class UserIn(BaseModel):
    name: str
    age: int


class User(UserIn):
    key: str


def to_user(doc: dict) -> User:
    return User(key=doc["_key"], name=doc["name"], age=doc["age"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/users", response_model=list[User])
def list_users(db=Depends(get_db)):
    return [to_user(d) for d in db.collection("users").all()]


@app.get("/users/{key}", response_model=User)
def read_user(key: str, db=Depends(get_db)):
    doc = db.collection("users").get(key)
    if doc is None:
        raise HTTPException(404, "Utilisateur introuvable")
    return to_user(doc)


@app.post("/users/{key}", response_model=User, status_code=201)
def create_user(key: str, user: UserIn, db=Depends(get_db)):
    users = db.collection("users")
    if users.get(key) is not None:
        raise HTTPException(409, "Clé déjà utilisée")
    users.insert({"_key": key, **user.model_dump()})
    return User(key=key, **user.model_dump())


@app.put("/users/{key}", response_model=User)
def update_user(key: str, user: UserIn, db=Depends(get_db)):
    users = db.collection("users")
    if users.get(key) is None:
        raise HTTPException(404, "Utilisateur introuvable")
    users.update({"_key": key, **user.model_dump()})
    return User(key=key, **user.model_dump())


@app.delete("/users/{key}", status_code=204)
def delete_user(key: str, db=Depends(get_db)):
    if not db.collection("users").delete(key, ignore_missing=True):
        raise HTTPException(404, "Utilisateur introuvable")


@app.get("/users/{key}/recommendations", response_model=list[str])
def recommendations(key: str, db=Depends(get_db)):
    """Produits achetés par des clients proches (graphe), hors produits déjà achetés."""
    query = """
        LET mine = (FOR p IN OUTBOUND CONCAT("users/", @key) bought RETURN p._id)
        FOR v IN 1..3 ANY CONCAT("users/", @key) bought
            FILTER IS_SAME_COLLECTION("products", v) AND v._id NOT IN mine
            RETURN DISTINCT v.name
    """
    return list(db.aql.execute(query, bind_vars={"key": key}))
