# Kittygram — практическая работа 4

Проект запускается в четырёх контейнерах: PostgreSQL 13, Django/Gunicorn,
сборка React и Nginx. Адрес приложения: http://localhost:9000/kittygram/.
API и админка доступны по `/kittygram/api/` и `/kittygram/admin/`.

## Локальный запуск

1. Запустите Docker Desktop с Linux containers и Docker Compose v2.
2. Скопируйте `.env.example` в `.env` (PowerShell: `Copy-Item .env.example .env`).
   Если `.env` уже существует, сохраните его значения и добавьте недостающие
   переменные из примера. Задайте случайный `SECRET_KEY` и пароль БД.
3. Выполните:

```sh
docker compose up -d --build
docker compose ps -a
docker compose exec backend python manage.py createsuperuser
```

Backend ждёт готовности PostgreSQL, применяет миграции, собирает статику
и запускает Gunicorn. Frontend копирует сборку в общий том и завершает работу
с кодом 0 — это ожидаемо. Gateway запускается после подготовки обоих сервисов.

Тома `pg_data`, `static`, `media` сохраняют БД, статику и фотографии.
Статика Django и React размещена в разных каталогах общего тома.
Остановка без удаления данных: `docker compose down`.
Команда `down -v` удаляет данные, не используйте её для обычного обновления.

## GitHub Actions и Docker Hub

Workflow `.github/workflows/main.yml` проверяет backend через Ruff и Django
tests, инфраструктурные файлы через pytest, frontend через Jest и сборку React.
После успешного прохождения тестов и проверки контейнеров при push в `main` собираются образы:

- `<DOCKER_USERNAME>/kittygram_backend`;
- `<DOCKER_USERNAME>/kittygram_frontend`;
- `<DOCKER_USERNAME>/kittygram_gateway`.

Каждый образ получает теги `latest` и SHA коммита. После публикации всех трёх
образов отправляется уведомление Telegram. Для pull request выполняются
только проверки. Ручной запуск публикации доступен для ветки `main`.

В GitHub → Settings → Secrets and variables → Actions добавьте secrets:

| Secret | Значение |
| --- | --- |
| `DOCKER_USERNAME` | Логин Docker Hub в нижнем регистре |
| `DOCKER_PASSWORD` | Токен Docker Hub с правом публикации |
| `TELEGRAM_TOKEN` | Токен Telegram-бота |
| `TELEGRAM_TO` | ID чата, в котором бот может отправлять сообщения |

Создайте публичные репозитории образов на Docker Hub. Код можно отправить
в существующий origin после проверки локальных изменений через `git diff`.
`kittygram_workflow.yml` — копия workflow для сдачи; при изменении workflow
обновляйте оба файла. CI проверяет их совпадение.

## Запуск опубликованных образов на localhost

Отдельный сервер не нужен. `docker-compose.production.yml` — конфигурация
запуска готовых образов из Docker Hub на этом же компьютере, без сборки кода.
После успешного workflow укажите `DOCKER_USERNAME=jlykabblu` в `.env`.
`IMAGE_TAG=latest` использует последний выпуск; SHA коммита выбирает конкретный.

```sh
docker compose down
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d --force-recreate
```

Выполняйте команды из того же каталога проекта: БД и фотографии сохранятся
в тех же томах. Адрес приложения остаётся http://localhost:9000/kittygram/.

## Проверки

```sh
docker compose config --quiet
docker compose exec backend python manage.py check
docker compose exec backend python manage.py test cats
```

Без Docker для backend используйте Python 3.10, зависимости из
`backend/requirements.txt`, PostgreSQL и переменные окружения из `.env`.
Django сам файл `.env` не читает. Для frontend используйте Node 18:

```sh
cd frontend
npm ci
npm test -- --watchAll=false --runInBand
npm run build
```

Для отдельной сборки frontend задайте `PUBLIC_URL=/kittygram`; Dockerfile
и CI уже задают эту переменную. Dev-сервер React не проксирует API автоматически;
полный проект проверяйте через gateway.

`tests.yml` содержит логины GitHub/Docker Hub и локальный адрес Kittygram.
Проверки разделены по моменту запуска:

```sh
# Структура проекта и конфигурация — без HTTP-запросов
python -m pytest
# Работа приложения — сначала запустите docker compose up -d
python -m pytest -m integration
# Публичные образы — после успешной публикации workflow
python -m pytest -m dockerhub
```

Переменная `KITTYGRAM_URL` может переопределить адрес для HTTP-проверок.
CI выполняет Ruff, Django-тесты, pytest, Jest, сборку React, затем собирает
и запускает весь проект в Docker на временном localhost GitHub runner.
Только после успешных HTTP-проверок публикуются три образа. Отдельный шаг
проверяет публичную доступность образов с тегом SHA, затем отправляет Telegram.
Домен, HTTPS и второй проект для этих проверок не требуются.

Перед сдачей проверьте регистрацию, вход, создание котика с фотографией,
повторное открытие карточки после перезагрузки страницы и статику админки.
Наличие workflow в репозитории само по себе не подтверждает успешный запуск
GitHub Actions или наличие образов: это проверяется после push и настройки secrets.
