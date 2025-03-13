docker exec -it bomchefe-db psql -U admin -l

docker exec -it nome_do_container_db bash

Connect to DB: 
docker exec -it bomchefe-db psql -h db -U admin -d bomchefe_db -p 5432

Command to API: 
docker-compose exec -it bomchefe-api alembic upgrade head

admin / bomchefe