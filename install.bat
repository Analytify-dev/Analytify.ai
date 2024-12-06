@echo off
set /p ADMIN_EMAIL="Enter admin email: "
set /p ADMIN_PASSWORD="Enter admin password: "

docker-compose build --build-arg ADMIN_EMAIL=%ADMIN_EMAIL% --build-arg ADMIN_PASSWORD=%ADMIN_PASSWORD%
docker-compose up
