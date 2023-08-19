# twitter-clone
## Стек 
- Python
- FastAPI
- Alembic
- async PostgreSQL + async SQLAlchemy
- nginx
- pytest
- Docker
- Swagger
- docker-compose
- GitHub Workflow
Корпоративная копия Twitter с возможностью выкладывать посты, лайкать их, подписываться на других пользователей

## Для развертки проекта:

```
git clone <this repo>
```

Активировать venv

```
docker-compose up --build
```

База данных и миграции создаются автоматически

Сайт находиться на http://127.0.0.1:1337 </br>
Запросы к апи на [8000](http://127.0.0.1:8000) порту </br>
Документация Swagger по пути [/docs](http://127.0.0.1:8000/docs)
