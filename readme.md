# To plug and play
> docker compose build --no-cache && docker compose up

# Issues I faced
1. **Django applications were unable to connect to the database**: the issue was solved by adding a health check and conditions in the docker-compose file. Now the application perform the internal configuration only after checking if db-service is healthy and ready.
2. **http://auth_service:8000** is not a valid domain: well it has nothing to do with docker. It was a silly mistake, so removed the _ from the name and renamed everything like authservice, userservice.
3. **Services were not startring up**: this was due to sequence of commands like runserver, migrate, etc. The issue was solved by adding the **ENTRYPOINT** but later I faced that the migrate command was not running from the **docker-compose** file. It happend because one command overwrites another so **ENTRYPOINT** overwrote the commands in **docker-compose**.