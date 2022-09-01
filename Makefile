# Unless otherwise specified we will for safety reasons always assume a dev deployment.
ifndef environment
override environment = dev
endif

include scraper_api/secrets/.makerc

IMAGE=scraper_api:${environment}
CLUSTER_NAME =scraper-api

.PHONY: info
info:
	@echo "Environment: " ${environment}
	@echo "Image: " ${IMAGE}
	@echo "Repo: " ${REPO}/${IMAGE}

.PHONY: freeze
freeze: pyproject.toml poetry.lock
	poetry export -f requirements.txt --output requirements.txt --without-hashes


# -----------------------------------
# Local
# -----------------------------------
.PHONY: local/run_scraper
local/run_scraper:
	environment=dev poetry run python scraper_api/scraper/run.py \
		--scraper_name="growatt" \
		--user_login="" \
		--password="" \
		--start="2022-08-20"  \
		--debug

.PHONY: local/run_api
local/run_api:
	environment=dev poetry run uvicorn scraper_api.api.main:app --reload

.PHONY: local/jupyter
local/jupyter:
	environment=dev poetry run jupyter notebook

# -----------------------------------
# Docker
# -----------------------------------
.PHONY: docker/build
docker/build: freeze
	docker image build --pull --tag ${IMAGE} .

docker/run:
	docker run --rm -ti \
		-p 8000:8000 \
		-v ${PWD}/scraper_api/secrets:/app/scraper_api/secrets:ro \
		scraper_api:dev
		

.PHONY: docker/run_compose
docker/run_compose:
	docker-compose -f docker-compose-dev.yml up -V --force-recreate scraper_api

# -----------------------------------
# KUBERNETES
# -----------------------------------
.PHONY: k8s/minikubestart
k8s/minikubestart:
	minikube start -p minikube
	eval $(minikube -p minikube docker-env)

.PHONY: k8s/delete_all
k8s/delete_all:
	kubectl delete deployment --all --ignore-not-found=true
	kubectl delete pods --all --ignore-not-found=true
	kubectl delete secrets --all --ignore-not-found=true
	kubectl delete services --all --ignore-not-found=true
	kubectl delete pvc --all --ignore-not-found=true
	kubectl delete pv --all --ignore-not-found=true

.PHONY: k8s/secret_path
k8s/secret_path:
	kubectl delete secrets secret-scraper-api-path --ignore-not-found=true
	kubectl create secret generic secret-scraper-api-path --from-file ./scraper_api/secrets

.PHONY: k8s/delete_deploy
k8s/delete_deploy:
	kubectl delete deployment -l app=secret-scraper-api --ignore-not-found=true
	kubectl delete pods -l app=secret-scraper-api --ignore-not-found=true

.PHONY: k8s/run
k8s/run: secret_path delete_k8s_deploy
	kubectl apply -f kubernetes/deploy-scraper-api.yaml
	sleep 3; kubectl get pods
	kubectl logs -f -l app=scraper-api -c scraper-api

# -----------------------------------
# GCLOUD
# -----------------------------------
.PHONY: gcloud/init
gcloud/init:
	gcloud init
	gcloud components install kubectl
	gcloud auth login


.PHONY: gcloud/build_image
gcloud/push_image: info
	docker tag ${IMAGE} ${REPO}/${IMAGE}
	gcloud auth configure-docker ${REGION}-docker.pkg.dev
	docker push ${REPO}/${IMAGE}

.PHONY: gcloud/create_cluster
gcloud/create_cluster:
	gcloud container clusters create-auto ${CLUSTER_NAME} \
		--region ${REGION} \
		--project=${PROJECT_ID} 

.PHONY: gcloud/scraper_api_cluster
gcloud/scraper_api_cluster:
	gcloud container clusters get-credentials ${CLUSTER_NAME} \
		--project ${PROJECT_ID} \
		--region ${REGION}
	kubectl get nodes

.PHONY: gcloud/service_host
gcloud/service_host:
	 kubectl get svc scraper-api-svc --output jsonpath='{.spec.clusterIP}'