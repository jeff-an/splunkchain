SPLUNK_RUN_ARGS = -d -p 8000:8000 -e 'SPLUNK_START_ARGS=--accept-license' -e 'SPLUNK_PASSWORD=Chang3d!'
BASE_IMAGE = splunk/splunk
IMAGE_NAME = splunkchain:latest
CONTAINER_NAME=$(shell echo $${name:-SPLUNKCHAIN_$$RANDOM})

image:
	docker build -f "Dockerfile" -t $(IMAGE_NAME) .

run: image
	docker run --name $(CONTAINER_NAME) $(SPLUNK_RUN_ARGS) $(IMAGE_NAME)

stop:
	docker stop $(shell docker ps -q --filter ancestor=$(BASE_IMAGE))

restart: image stop run

make logs:
	docker logs $(shell docker ps -q --filter ancestor=$(BASE_IMAGE))