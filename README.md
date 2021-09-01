# Выпускной проект Яндекс.Практикум
![](https://github.com/wildd1994/foodgram-project-react/actions/workflows/main.yml/badge.svg)<br/>

Проект Foodgram - сервис для публикации кулинарных рецептов.

Основные возможности:

  1. Регистрация пользователей.
  2. Создание, Изменение, Удаление рецептов.
  3. Добавление рецептов в избранное и простмотр всех избранных рецептов.
  4. Фильтрация рецептов по тегам.
  5. Подписка на авторов и просмотр рецептов определенного автора.
  6. Добавление рецептов и формирование списка покупок для их приготовления.

### Установка Для работы с проектом необходимо установить Docker: https://docs.docker.com/engine/install/

Клонируйте репозиторий к себе на сервер командой:

> git clone https://github.com/wildd1994/foodgram-project-react .

Перейдите в каталог проекта:

> cd foodgram-project-react/foodgram

Создайте файл окружений

> touch .env

И заполните его:

> POSTGRES_NAME=postgres  # имя базы postgres<br/>
> POSTGRES_USER=postgres # имя пользователя postgres<br/>
> POSTGRES_PASSWORD=postgres # пароль для базы postgres<br/>
> DB_HOST=postgresql   #имя хоста базы данных<br/>
> DB_PORT=5432  #порт<br/>

Перейдите в каталог infra и запустите создание контейнеров:

> docker-compose up -d --build

Первоначальная настройка проекта:

> docker-compose exec web foodgram/python manage.py migrate --noinput<br/>
> docker-compose exec web foodgram/python manage.py collectstatic --no-input

Создание суперпользователя:

> docker-compose exec backend python manage.py createsuperuser

Загрузка фикстур

> docker exec -it infra_web_1 foodgram/python manage.py loaddata fixtures.json

После сборки, проект будет доступен по имени хоста вашей машины, на которой был развернут проект.

