.PHONY: up down tf-apply test clean logs

up:
	docker-compose up -d --build

down:
	docker-compose down -v

tf-init:
	cd terraform && terraform init

tf-apply:
	cd terraform && terraform apply -auto-approve

test:
	python3 -m pip install -q -r test-harness/requirements.txt
	python3 test-harness/run_simulations.py

audit:
	curl -s http://localhost:8000/audit | jq .

run-all:
	./run.sh

logs:
	docker-compose logs -f
