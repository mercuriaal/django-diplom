## Дипломная работа по курсу Django: создание функциональных веб-приложений

Инструкция по установке и первому запуску:

1. Скачивание проекта 

`git clone https://github.com/mercuriaal/django-diplom`

2. Подключение к базе данных в `settings.py`

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': ваша база данных,
        'USER': ваш логин,
        'PASSWORD': ваш пароль,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

2. Установка библиотек

`pip install -r requirements.txt`

3. Создание таблиц в базе данных

`python manage.py migrate`

4. Наполнение тестовыми данными

`python manage.py loaddata fixtures.json`

5. Запуск проекта

`python manage.py runserver`