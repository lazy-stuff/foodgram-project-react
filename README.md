# Foodgram project
 
![Django workflow](https://github.com/lazy-stuff/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Дипломная работа по программе Python-разработчик (Я.Практикум).

Приложение «Продуктовый помощник» - это сайт, на котором пользователи могут размещать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям скачивать список продуктов, которые нужно купить для приготовления выбранных блюд.

#### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
$ git clone https://github.com/lazy-stuff/foodgram-project-react
```

Перейти в директорию infra/:

```
$ cd foodgram-project-react/infra/
```
Cоздать .env-файл для проекта.
Шаблон заполнения:

```
SECRET_KEY = 'p123456'

DB_ENGINE=django.db.backends.postgresql
DB_NAME=data_base
POSTGRES_USER=data_base
POSTGRES_PASSWORD=data_base
DB_HOST=db
DB_PORT=1234
```

Запустить контейнеры:

```
$ docker-compose up -d --build 
```

Выполнить миграции, создать суперпользователя и собрать статику:

```
$ docker-compose exec backend python manage.py migrate
$ docker-compose exec backend python manage.py createsuperuser
$ docker-compose exec backend python manage.py collectstatic --no-input 
```

Заполнить базу данных:

```
$ docker-compose exec backend python manage.py load_data 
```

#### Технологии
  
* [Python](https://www.python.org)

* [Django REST framework](https://www.django-rest-framework.org)

* [Docker](https://www.docker.com)

#### Авторы

**Настя Лунегова** - *GitHub* - *[lazy-stuff](https://github.com/lazy-stuff)*