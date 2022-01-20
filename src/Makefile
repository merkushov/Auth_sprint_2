ifndef VERBOSE
.SILENT:
endif

.DEFAULT_GOAL := help

help:	## список доступных команд
	@grep -E '^[a-zA-Z0-9_\-\/]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "(Other less used targets are available, open Makefile for details)"
.PHONY: help

#
# Работа с кодом
#

code/format: 	## принудительное форматирование кода по принятым стандартам
	black ./
.PHONY: code/format

code/docstringformat: 	## принудительное форматирование кода по принятым стандартам
	docformatter --in-place -r ./
.PHONY: code/docstringformat

code/format_check: 	## проверка форматирования кода по принятым стандартам
	black --check ./
.PHONY: code/format_check

code/isort:		## сортировка строк импорта
	isort ./
.PHONY: code/isort

code/isort_check:		## проверка сортировок строк импорта
	isort --check ./
.PHONY: code/isort_check

code/style:		## проверка стиля кода
	flake8 ./
.PHONY: code/style

code/docstyle:		## проверка стиля кода
	pydocstyle ./
.PHONY: code/docstyle

code/check_all: code/format_check code/isort_check code/style	## статический анализ кода (без авто-исправлений) по принятым в проекте стандартам
.PHONY: code/check_all

code: code/format code/docstringformat code/isort code/style	## статический анализ кода и авто-исправления по принятым в проекте стандартам
.PHONY: code