#!/usr/bin/env bash
# Crée la base "demo", les collections et importe le jeu de données (data/*.json).
# Relançable : repart d'une base "demo" propre.
set -euo pipefail
cd "$(dirname "$0")/.."

run() { docker compose exec -T arangodb sh -c "$1"; }
AUTH='--server.password "$ARANGO_ROOT_PASSWORD"'

echo "# 1. Base et collections"
run "arangosh $AUTH --javascript.execute-string '
  if (db._databases().includes(\"demo\")) db._dropDatabase(\"demo\");
  db._createDatabase(\"demo\"); db._useDatabase(\"demo\");
  db._create(\"users\"); db._create(\"products\"); db._createEdgeCollection(\"bought\");
  print(\"collections : \" + db._collections().filter(c => !c.name().startsWith(\"_\")).map(c => c.name()));
'"

echo "# 2. Import du jeu de données"
for pair in users:users products:products bought:bought; do
  file=${pair%%:*}; coll=${pair##*:}
  run "arangoimport $AUTH --server.database demo --file /import/$file.json --type json --collection $coll"
done
