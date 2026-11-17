# ArangoDb-FastApi

ArangoDB (Docker) + API FastAPI + guide de démonstration en ligne de commande.

| Dossier / fichier | Rôle |
|---|---|
| `docker-compose.yml` | ArangoDB 3.12 (+ l'API avec `--profile api`) |
| `data/` | Jeu de données JSON : `users`, `products`, `bought` (arêtes) |
| `scripts/init.sh` | Crée la base `demo`, les collections et importe `data/` |
| `scripts/arangosh.sh` | Ouvre `arangosh` sur la base `demo` |
| `DEMO.md` | Script à suivre : CRUD et requêtes de graphe en CLI |
| `api/` | API FastAPI (CRUD `users` + recommandations par le graphe) |

## Démarrage

```bash
cp .env.example .env
docker compose up -d
./scripts/init.sh
```

Suivre ensuite [DEMO.md](DEMO.md).

## API

```bash
docker compose --profile api up -d --build
```

Docs interactives : http://localhost:8000/docs

| Méthode | Route | |
|---|---|---|
| GET | `/users`, `/users/{key}` | lire |
| POST | `/users/{key}` | créer (`{"name": "...", "age": 0}`) |
| PUT | `/users/{key}` | modifier |
| DELETE | `/users/{key}` | supprimer |
| GET | `/users/{key}/recommendations` | produits recommandés (graphe) |

Tests : `cd api && pip install -r requirements-dev.txt && pytest`
