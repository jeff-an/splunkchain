SPLUNK_RUN_ARGS = -d -p 8000:8000 -e 'SPLUNK_START_ARGS=--accept-license' -e 'SPLUNK_PASSWORD=Chang3d!'
BASE_IMAGE = splunk/splunk
IMAGE_NAME = splunkchain:latest
REMOTE_IMAGE_NAME = repo.splunk.com/jan/splunkchain:latest
CONTAINER_NAME=$(shell echo $${name:-SPLUNKCHAIN_$$RANDOM})
DEPLOY_ID:=$(shell echo $${name:-$$RANDOM})

image:
	docker build -f "Dockerfile" -t $(IMAGE_NAME) .
	docker tag $(IMAGE_NAME) $(REMOTE_IMAGE_NAME)
	docker push $(REMOTE_IMAGE_NAME)

run: image
	docker run --name $(CONTAINER_NAME) $(SPLUNK_RUN_ARGS) $(IMAGE_NAME)

stop:
	docker stop $(shell docker ps -q --filter ancestor=$(BASE_IMAGE))

logs:
	docker logs $(shell docker ps -q --filter ancestor=$(BASE_IMAGE))

restart: image stop run logs

client:
	sed "s/DEPLOY_ID/$(DEPLOY_ID)/g" client.yml > client-$(DEPLOY_ID).yml
	kubectl create -f client-$(DEPLOY_ID).yml --save-config

krestart:
	kubectl delete -f .
	kubectl create -f . --save-config

kstop:
	-echo client-* | xargs -n1 kubectl delete -f
	rm client-*.yml

refresh:
	kubectl apply -f client-*

krebuild: image kstop client

clean:
	rm client-*.yml