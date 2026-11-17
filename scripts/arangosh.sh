#!/usr/bin/env bash
# Ouvre arangosh (shell interactif) sur la base "demo".
cd "$(dirname "$0")/.."
exec docker compose exec arangodb sh -c 'arangosh --server.password "$ARANGO_ROOT_PASSWORD" --server.database demo'
