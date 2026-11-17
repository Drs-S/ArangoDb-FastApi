# Démo ArangoDB en ligne de commande

Jeu de données : 4 clients (`users`), 5 produits (`products`), 8 achats (`bought`, collection d'arêtes).
Toutes les commandes ont été testées avec ArangoDB 3.12.

## 0. Démarrer

```bash
cp .env.example .env            # mot de passe root : ARANGO_ROOT_PASSWORD
docker compose up -d            # attend que le conteneur soit "healthy"
docker compose ps
```

Interface web : http://localhost:8529 (utilisateur `root`, base `demo`).

## 1. Créer la base, les collections et importer les données

Tout d'un coup :

```bash
./scripts/init.sh
```

Ou pas à pas, pour le montrer en direct :

```bash
# a) base "demo" (shell système)
docker compose exec arangodb sh -c 'arangosh --server.password "$ARANGO_ROOT_PASSWORD" --javascript.execute-string "db._createDatabase(\"demo\")"'

# b) collections, dans arangosh
./scripts/arangosh.sh
```

```js
db._create("users")
db._create("products")
db._createEdgeCollection("bought")
```

```bash
# c) import des fichiers de data/ (montés dans /import dans le conteneur)
for c in users products bought; do
  docker compose exec arangodb sh -c "arangoimport --server.password \"\$ARANGO_ROOT_PASSWORD\" --server.database demo --file /import/$c.json --type json --collection $c"
done
```

## 2. CRUD (dans arangosh : `./scripts/arangosh.sh`)

```js
// Lire
db.users.count()
db._query('FOR u IN users RETURN u').toArray()
db._query('FOR u IN users FILTER u.age > 25 SORT u.age RETURN u.name').toArray()
db.users.document("alice")

// Créer
db._query('INSERT { _key: "eve", name: "Eve", age: 22 } INTO users')
db.users.count()                                   // 5

// Modifier
db._query('UPDATE "eve" WITH { age: 23 } IN users')
db.users.document("eve").age                       // 23

// Supprimer
db._query('REMOVE "eve" IN users')
db.users.count()                                   // 4
```

## 3. Requêtes de graphe

```js
// Tout ce qui est relié à Alice, jusqu'à 3 liens, dans les deux sens
db._query('FOR v IN 1..3 ANY "users/alice" bought RETURN DISTINCT v').toArray()

// Produits à recommander à Alice : ceux des autres acheteurs, qu'elle n'a pas déjà
db._query(`
  FOR v IN 1..3 ANY "users/alice" bought
    FILTER IS_SAME_COLLECTION("products", v)
    FILTER v._key NOT IN ["clavier", "souris"]
    RETURN DISTINCT v.name
`).toArray()                                       // ["Écran 27 pouces", "Casque audio"]
```

## 4. Arrêter

```bash
docker compose down        # garde les données (volume)
docker compose down -v     # supprime aussi les données
```

## 5. API FastAPI (optionnel)

```bash
docker compose --profile api up -d --build
curl localhost:8000/users
```

Documentation interactive : http://localhost:8000/docs
