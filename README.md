### Description
Backend service with **RESTful API** architecture. With implemented PostgreDatabase
using SQLAlchemy ORM, Redis database with RQ workers, Gunicorn workers, 
JWT authentication. The web service containerized using Docker and Doker Compose.

### How to setup

- clone git repository ```git clone https://github.com/remuneration/remuneration.git```
or use **SSH** instead of https.
- you should have **Docker Desktop** to be able to run the Docker compose.
- build and start your containers ```docker compose -p ship up --build```, **ship** is
just a name tag **ship-** for our containers.
- once containers are built and service started (approximately 10sec) we can send requests
to the routes.
- to get full info of implemented API routes check swagger-documentation ```http://127.0.0.1:8000/swagger-ui```

### Deletion

- we have previously marked our containers with the tag **ship** so 
to delete everything use ````docker compose -p ship down -v --rmi all````
(you will delete volumes, images, and containers)


:bangbang: All information that are in .env file is fake, it were loaded for demonstrative purposes only.
 Databases are creating locally, Postgres with volume and Redis in memory.