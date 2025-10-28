.PHONY: run build-container

IMAGE_NAME=forecaster
TAG=latest

run:
	streamlit run home.py --server.port=8080 --server.address=0.0.0.0

run-container:
	docker build . -t $(IMAGE_NAME):$(TAG) | docker run -p 8080:8080 $(IMAGE_NAME):$(TAG)


