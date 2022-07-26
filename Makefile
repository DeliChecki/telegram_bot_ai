.ONESHELL: ## Запуск всех команд в одной оболочке.
.PHONY: all, analysis, build, format, githooks, pull, push, requirements, tests

IMAGE_NAME = delichecki.ru/coco-telegram
DOCKERFILE = Dockerfile

tag = $(shell poetry version --short)

IMAGE = $(IMAGE_NAME):$(tag)

all: build

analysis: ## Анализирует исходный код.
	@poetry run black sources --check --diff
	@poetry run flake8 sources
	@poetry run isort sources --check

build: ## Собирает образ контейнера.
	@docker build -f $(DOCKERFILE) -t $(IMAGE) .

format: ## Форматирует исходный код.
	@poetry run autoflake --recursive --remove-unused-variables --remove-all-unused-imports sources
	@poetry run black sources
	@poetry run isort sources

githooks: ## Устанавливает хуки из конфигурации (.pre-commit-config.yaml).
	@poetry run pre-commit install --hook-type=pre-commit --hook-type=pre-push

requirements: ## Экспортирует зависимости в requirements.txt для обратной совместимости
	@poetry export -o requirements.txt --without-hashes
