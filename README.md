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
- Prometheus
- Grafana
Корпоративная копия Twitter с возможностью выкладывать посты, лайкать их, подписываться на других пользователей

## Для развертки проекта:

```
git clone <this repo>
```

Активировать venv

```
docker-compose up --build
```

### [Просмотр метрик](http://127.0.0.1:3000)
```
admin admin
```
```
Prometheus
http://prometheus:9090
```
```angular2html
Можно импортировать готовый дешборд из директории grafana/dashboards/dashboard.json
```




База данных и миграции создаются автоматически

Сайт находиться на http://127.0.0.1:1337 </br>
Запросы к апи на [8000](http://127.0.0.1:8000) порту </br>
Документация Swagger по пути [/docs](http://127.0.0.1:8000/docs)
