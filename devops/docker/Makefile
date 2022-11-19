ifndef VERBOSE
.SILENT:
endif

ifeq ($(STAGE), prod)
DOCKER_COMPOSE_FILE=-f docker-compose.prod.yml
else ifeq ($(STAGE), test)
DOCKER_COMPOSE_FILE=-f docker-compose.test.yml
else
DOCKER_COMPOSE_FILE=-f docker-compose.dev.yml
endif

DOCKER_COMPOSE=docker-compose -p "auth_api" -f docker-compose.yml $(DOCKER_COMPOSE_FILE) --env-file ../.env
DOCKER_COMPOSE_TEST=docker-compose -p "auth_api_test" -f docker-compose.test.yml --env-file ../.env

# имя контейнеров в docker-compose
DOCKER_AUTH_API=auth_api
DOCKER_AUTH_DB=auth_db
DOCKER_AUTH_REDIS=auth_redis
DOCKER_AUTH_NGINX=auth_nginx

DOCKER_AUTH_API_TEST=auth_test_api
DOCKER_AUTH_DB_TEST=auth_test_db
DOCKER_AUTH_REDIS_TEST=auth_test_redis

#[[ -z "${OS}" ]] && OS := (shell uname) || OS="${OS}"

ifeq ($(OS),)
OS := $(shell uname)
endif
.DEFAULT_GOAL := help

help:	## список доступных команд
	@grep -E '^[a-zA-Z0-9_\-\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "(Other less used targets are available, open Makefile for details)"
.PHONY: help

env_prod_setup:	## настроить переменные production окружения
	@cp ../auth_api/.env.prod.example ../auth_api/.env
	@make env_setup
.PHONY: env_prod_setup

env_dev_setup:	## настроить переменные development окружения
	@cp ../auth_api/.env.dev.example ../auth_api/.env
	@make env_setup
.PHONY: env_dev_setup

env_setup:
	@echo "$(OS)"
	@cp ../auth_db/.env.example 	../auth_db/.env
	@cp ../.env.example ../.env

	# сгенерировать рандомные пароли для PostgreSQL
	# `env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 42 | xargs -I '{}' sed -i '' -e 's/POSTGRES_PASSWORD=[a-zA-Z0-9]*/POSTGRES_PASSWORD={}/' -e 's/DB_PASSWORD=[a-zA-Z0-9]*/DB_PASSWORD={}/' ../auth_api/.env ../auth_db/.env`

	# сгенерировать рандомный SECRET_KEY и JWT_SECRET_KEY
	@if [[ $(OS) = 'Windows_NT' ]]; then \
		`env LC_CTYPE=C cat /dev/urandom | tr -dc "a-zA-Z0-9" | head -c 32 | xargs -I '{}' sed -i -e "s/SECRET_KEY=[a-zA-Z0-9_\-]*/SECRET_KEY={}/" ../auth_api/.env`; \
		`env LC_CTYPE=C cat /dev/urandom | tr -dc "a-zA-Z0-9" | head -c 32 | xargs -I '{}' sed -i -e "s/JWT_SECRET_KEY=[a-zA-Z0-9_\-]*/JWT_SECRET_KEY={}/" ../auth_api/.env`; \
	else \
		`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | xargs -I '{}' sed -i '' 's/SECRET_KEY=[a-zA-Z0-9\-]*/SECRET_KEY={}/' ../auth_api/.env`; \
		`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | xargs -I '{}' sed -i '' 's/JWT_SECRET_KEY=[a-zA-Z0-9\-]*/JWT_SECRET_KEY={}/' ../auth_api/.env`; \
	fi
	

	# установить HOST_UID = UID текущего пользователя. Это влияет на UID пользователя внутри контейнера.
	# Нужно для совместимости прав доступа к сгенерированным файлам у хостового пользователя

	# Хак! Я не знаю, как правильно сматчить GroupID между
	# 	   MacOS (host) и Linux (docker os)
	#	   На Windows host также необходимо переформатирование команд (кавычки и т.д.)
	@if [[ $(OS) = 'Darwin' ]]; then \
		`id -u | xargs -I '{}' sed -i '' 's/HOST_UID=.*/HOST_UID={}/' ../.env`; \
		`sed -i '' 's/HOST_GID=.*/HOST_GID=61/' ../.env`; \
	elif [[ $(OS) = 'Windows_NT' ]]; then \
		`id -u | xargs -I '{}' sed -i "s/HOST_UID=.*/HOST_UID={}/" ../.env`; \
		`id -g | xargs -I '{}' sed -i "s/HOST_GID=.*/HOST_GID={}/" ../.env`; \
	else \
		`id -u | xargs -I '{}' sed -i '' 's/HOST_UID=.*/HOST_UID={}/' ../.env`; \
		`id -g | xargs -I '{}' sed -i '' 's/HOST_GID=.*/HOST_GID={}/' ../.env`; \
	fi
.PHONY: env_setup

docker/build:	## build the environment
	$(DOCKER_COMPOSE) build
.PHONY: docker/build

docker/start:	## поднять Докер
	$(DOCKER_COMPOSE) up -d
.PHONY: docker/start

# alias for docker/start
docker/up: docker/start
.PHONY: docker/up

docker/stop:	## остановить все контейнеры Приложения
	$(DOCKER_COMPOSE) down
.PHONY: docker/stop

docker/down: 	## остановить и удалить все контейнеры Приложения
	$(DOCKER_COMPOSE) down --remove-orphans
.PHONY: docker/down

docker/destroy:	## остановить/удалить контейнеры и очистить данные Приложения
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
.PHONY: docker/destroy

#
# Приложение
#

auth_api/bash:		## доступ в контейнер с Django
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_API) bash
.PHONY: auth_api/bash

auth_api/log:	## посмотреть логи контейнера Приложения
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_AUTH_API)
.PHONY: auth_api/log

auth_api/migrate:	## применить миграции
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_API) flask db upgrade
.PHONY: auth_api/migrate

#
# База данных
#

db/bash:		## доступ в контейнер с БД
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_DB) bash
.PHONY: db/bash

db/log:		## посмотреть логи контейнера БД
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_AUTH_DB)
.PHONY: db/log

db/psql:		## интерактивный терминал PostgreSQL
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_DB) bash -c 'psql -U $${POSTGRES_USER} $${POSTGRES_DB}'
.PHONY: db/psql

db/waiting_for_readiness:
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_DB) bash -c 'until pg_isready 2>/dev/null; do sleep 1 ; done; echo "Database ready."'
.PHONY: db/waiting_for_readiness

#
# Nginx
#

nginx/bash:		## доступ в контейнер с Nginx
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_NGINX) bash
.PHONY: nginx/bash

nginx/log:		## посмотреть логи контейнера Nginx
	$(DOCKER_COMPOSE) logs --follow $(DOCKER_AUTH_NGINX)
.PHONY: nginx/log

#
# Redis
#

redis/redis_waiting_for_readiness:	## ожидать готовности Redis
	$(DOCKER_COMPOSE) exec $(DOCKER_AUTH_REDIS) sh -c 'until redis-cli -u redis://localhost:6379 ping 1>/dev/null; do printf "."; sleep 1; done; echo "Redis ready."'
.PHONY: redis/redis_waiting_for_readiness

#
# Функкциональное тестирование
#

env_test_setup:		## настроить переменные окружения для тестового контура
	@cp ../auth_api/.env.test.example ../auth_api/.env
	@cp ../auth_db/.env.example 	../auth_db/.env
	@cp ../.env.example ../.env

	# сгенерировать рандомные пароли для PostgreSQL
	# `env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 42 | xargs -I '{}' sed -i '' -e 's/POSTGRES_PASSWORD=[a-zA-Z0-9]*/POSTGRES_PASSWORD={}/' -e 's/DB_PASSWORD=[a-zA-Z0-9]*/DB_PASSWORD={}/' ../auth_api/.env ../auth_db/.env`

	# сгенерировать рандомный SECRET_KEY и JWT_SECRET_KEY
	@if [[ $(OS) = 'Windows_NT' ]]; then \
		`env LC_CTYPE=C cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32 | xargs -I '{}' sed -i -e "s/SECRET_KEY=[a-zA-Z0-9_\-]*/SECRET_KEY={}/" ../auth_api/.env`; \
		`env LC_CTYPE=C cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c 32 | xargs -I '{}' sed -i -e "s/JWT_SECRET_KEY=[a-zA-Z0-9_\-]*/JWT_SECRET_KEY={}/" ../auth_api/.env`; \
	else \
		`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | xargs -I '{}' sed -i '' 's/SECRET_KEY=[a-zA-Z0-9\-]*/SECRET_KEY={}/' ../auth_api/.env`; \
		`env LC_CTYPE=C tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c 32 | xargs -I '{}' sed -i '' 's/JWT_SECRET_KEY=[a-zA-Z0-9\-]*/JWT_SECRET_KEY={}/' ../auth_api/.env`; \
	fi

.PHONY: env_test_setup

auth_api_test/destroy:		## остановить/удалить контейнеры для тестов и очистить тестовые данные
	$(DOCKER_COMPOSE_TEST) down --volumes --remove-orphans
.PHONY: auth_api_test/setup

auth_api_test/build: 	## собрать тестовые контейнеры
	$(DOCKER_COMPOSE_TEST) build
.PHONY: auth_api_test/build

auth_api_test/up: 	## поднять контейнеры для тестов
	$(DOCKER_COMPOSE_TEST) up -d
.PHONY: auth_api_test/up

auth_api_test/db_waiting_for_readiness:	## ожидать готовность тестовой БД
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_AUTH_DB_TEST) bash -c 'until pg_isready 2>/dev/null; do sleep 1 ; done; echo "Database ready."'
.PHONY: auth_api_test/db_waiting_for_readiness

auth_api_test/redis_waiting_for_readiness:	## ожидать готовности тестового Redis
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_AUTH_REDIS_TEST) sh -c 'until redis-cli -u redis://localhost:6379 ping 1>/dev/null; do printf "."; sleep 1; done; echo "Redis ready."'
.PHONY: auth_api_test/redis_waiting_for_readiness

auth_api_test/run:	## запустить функциональные тесты API
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_AUTH_API_TEST) bash -c 'cd /usr/src/auth_app_tests/functional && PYTHONPATH=. pytest .'
.PHONY: test/run

auth_api_test/bash: 	## доступ в контейнер с тестами
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_AUTH_API_TEST) bash
.PHONY: auth_api_test/bash

auth_api_test/log:	## посмотреть логи контейнера с тестами Приложения
	$(DOCKER_COMPOSE_TEST) logs --follow $(DOCKER_AUTH_API_TEST)
.PHONY: auth_api_test/log

#
# Интеграционные тесты
#

auth_api_test/run_integration: 	## запустить интеграционные авто-тесты
	$(DOCKER_COMPOSE_TEST) exec $(DOCKER_AUTH_API_TEST) bash -c 'cd /usr/src/auth_app_tests && PYTHONPATH=/usr/src/auth_app pytest integration/src'
.PHONY: test
