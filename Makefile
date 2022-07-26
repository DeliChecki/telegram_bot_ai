.ONESHELL: ## MAKE IT
.PHONY: build, run, stop

IMAGE_NAME = delichecki.ru/coco-telegram
DOCKERFILE = Dockerfile

tag = 1.0.0
IMAGE = $(IMAGE_NAME):$(tag)

all: build

build:
    $(shell docker build -f $(DOCKERFILE) -t $(IMAGE) .)

run:
    $(shell docker-compose up -d)

stop:
    $(shell docker-compose down)