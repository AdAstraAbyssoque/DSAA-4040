$ docker compose ps
NAME                  IMAGE              SERVICE   STATUS                 PORTS
bookstore-backend-1   bookstore-backend  backend   Up 49 min              0.0.0.0:8000->8000/tcp
bookstore-frontend-1  bookstore-frontend frontend  Up 39 min              0.0.0.0:8080->80/tcp
bookstore-postgres-1  postgres:16-alpine postgres  Up 49 min  (healthy)   0.0.0.0:5432->5432/tcp
bookstore-redis-1     redis:7-alpine     redis     Up 49 min  (healthy)   0.0.0.0:6379->6379/tcp
