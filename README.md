# Foodgram project
 
![Django workflow](https://github.com/lazy-stuff/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

##### Дипломная работа по программе Python-разработчик (Я.Практикум).

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
$ git clone https://github.com/lazy-stuff/foodgram-project-react
$ cd foodgram-project-react/backend

```
Cоздать и активировать виртуальное окружение:

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
$ python3 -m pip install --upgrade pip
$ pip install -r requirements.txt
```

Перейти в папку foodgram/:

```
$ cd foodgram/
```

Выполнить миграции:

```
$ python3 manage.py migrate
```

Заполнить базу теестовыми данными:

```
$ python3 manage.py load_data
```

Запустить проект:

```
$ python3 manage.py runserver
```

#### Технологии
  
* [Python](https://www.python.org)

* [Django REST framework](https://www.django-rest-framework.org)

#### Автор

**Настя Лунегова** - *GitHub* - *[lazy-stuff](https://github.com/lazy-stuff)*
