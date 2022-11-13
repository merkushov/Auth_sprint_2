## Разворачивание приложения для разработки

```
git clone git@github.com:merkushov/Auth_sprint_2.git

cd Auth_sprint_2

export ENV=dev
make dev/setup

# запуск интеграционных тестов
make test/run_integration

# доступные опции
make help
```

## Ручное тестирование интеграции AsyncAPI и AuthAPI

Два сервиса подняты в докер-контейнерах. Общаемся с ними через сервис Nginx

```shell
# создать нового пользователя и залогиниться
curl -XPOST -H "Content-Type: application/json" http://localhost/auth_api/v1/user -d '{"username": "test_user","email": "test@gmail.com","password": "12345"}'
curl -XPOST -H "Content-Type: application/json" http://localhost/auth_api/v1/login -d '{"username": "test_user", "password": "12345"}'

export AUTH_API_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI3YTZlMmExYy1kNDA0LTQ4ZTAtYjk1Yi0xMzBhNzc4ZmFhYTkiLCJ0eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6IjA5ODZlNDc2LTYwYzQtNGQzOS1iNTllLTQ5MjdkZDVmMThjMSIsInVzZXJfcm9sZXMiOltdLCJleHBpcmVkIjoiMjAyMi0xMS0xM1QxNTo1OTo1NCJ9.rN9mLZK_bG-zWic6WX-OKTaHh0c5qUXIAPTu64xmzx8

# создать роли и привязать роль subscriber к пользователю
curl -XPOST -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_API_ACCESS_TOKEN" http://localhost/auth_api/v1/role -d '{"name": "user"}'
curl -XPOST -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_API_ACCESS_TOKEN" http://localhost/auth_api/v1/role -d '{"name": "subscriber"}'
curl -XPOST -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_API_ACCESS_TOKEN" http://localhost/auth_api/v1/user/0986e476-60c4-4d39-b59e-4927dd5f18c1/role/d71820c9-a053-4e1b-ad33-4b69c3f9d32e

# убедиться, что роль пользователю выдана
curl -XGET -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_API_ACCESS_TOKEN" http://localhost/auth_api/v1/me/roles

# запросить список фильмов
#   Ограничения: 
#    - неавторизованному пользователю будет доступны только первые 10 фильмов из списка
#    - авторизованный пользователь с ролью subscriber будет иметь доступ к полному списку
curl -XGET -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_API_ACCESS_TOKEN" http://localhost/async_api/v1/film/
```