.ONESHELL: ## MAKE IT
.PHONY: build, run, stop

IMAGE_NAME = delichecki.ru/coco-telegram
DOCKERFILE = Dockerfile

tag = 1.0.0
IMAGE = $(IMAGE_NAME):$(tag)

build:
    @docker build -f $(DOCKERFILE) -t $(IMAGE) .

run:
    @docker-compose up -d

stop:
    @docker-compose down