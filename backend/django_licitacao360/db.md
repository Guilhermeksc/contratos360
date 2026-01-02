bizu deletar tabelas

docker compose down
rm -rf postgres_data
docker compose up -d --build

docker exec -it postgres_cemos psql -U postgres -d appdb

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

docker compose restart backend
