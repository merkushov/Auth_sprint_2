ifndef VERBOSE
.SILENT:
endif

.DEFAULT_GOAL := help

help:	## список доступных команд
	@grep -E '^[a-zA-Z0-9_\-\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "(Other less used targets are available, open Makefile for details)"
.PHONY: help

# вызываем make находящийся в подкаталоге с настройками окружения
SUBMAKE_DEVOPS=$(MAKE) --silent -C devops/docker

## Production target с сервером Nginx и распределённой трассировкой
prod/setup: export STAGE := prod
prod/setup:
	$(SUBMAKE_DEVOPS) env_prod_setup
	@make base/setup

## настроить инфраструктуру для разработки в Докере
dev/setup:
	$(SUBMAKE_DEVOPS) env_dev_setup
	@make base/setup

base/setup:
	$(SUBMAKE_DEVOPS) docker/destroy
	$(SUBMAKE_DEVOPS) docker/build
	$(SUBMAKE_DEVOPS) docker/up
	$(SUBMAKE_DEVOPS) redis/redis_waiting_for_readiness
	$(SUBMAKE_DEVOPS) db/waiting_for_readiness
	$(SUBMAKE_DEVOPS) auth_api/migrate
.PHONY: base/setup


dev/up:	## поднять всю инфраструктуру для разработки в Докере
	$(SUBMAKE_DEVOPS) docker/up	
.PHONY: dev/up


dev/code:	## перейти внуть Докер-контейнера с API и начать кодить
	$(SUBMAKE_DEVOPS) docker/up
	$(SUBMAKE_DEVOPS) auth_api/bash
.PHONY: dev/code

dev/log:	## подсмотреть логи контейнера на хостовой машине
	$(SUBMAKE_DEVOPS) auth_api/log
.PHONY: dev/log

dev/stop:	## опустить инфраструктуру разработки
	$(SUBMAKE_DEVOPS) docker/stop
.PHONY: dev/stop

#
# Функциональные тесты
#

test/setup: 	## настройка окружения функциональных тестов
	$(SUBMAKE_DEVOPS) env_test_setup
	$(SUBMAKE_DEVOPS) auth_api_test/destroy
	$(SUBMAKE_DEVOPS) auth_api_test/build
	$(SUBMAKE_DEVOPS) auth_api_test/up
	$(SUBMAKE_DEVOPS) auth_api_test/db_waiting_for_readiness
	$(SUBMAKE_DEVOPS) auth_api_test/redis_waiting_for_readiness
.PHONY: test/setup

test/run_functional: 	## запустить функциональные тесты
	$(SUBMAKE_DEVOPS) auth_api_test/run
.PHONY: test/run_functional

test/down: 	## остановить тесты и удалить тестовую инфраструктуру
	$(SUBMAKE_DEVOPS) auth_api_test/destroy
.PHONY: test/run_functional

#
# Интеграционные тесты
#

test/run_integration:	## запустить интеграционные тесты
	$(SUBMAKE_DEVOPS) auth_api_test/run_integration
.PHONY: test/run_integration