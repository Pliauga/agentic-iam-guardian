#!/usr/bin/env bash
set -e

echo "================================================================="
echo "  Agentic IAM Guardian: Local Lab Orchestrator"
echo "================================================================="

echo "[1/4] Starting Docker containers (LocalStack + Guardian)..."
docker-compose down -v --remove-orphans || true
docker-compose up -d --build

echo "[2/4] Waiting for LocalStack to be fully ready..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"iam": "available"\|"iam": "running"'; do
  echo "Waiting for LocalStack services..."
  sleep 3
done
echo " LocalStack is online!"

echo "[3/4] Initializing and applying Terraform baseline infrastructure..."
cd terraform
terraform init -upgrade
terraform apply -auto-approve
cd ..
echo " Terraform state deployed successfully to LocalStack!"

echo "[4/4] Executing Red-Team Simulation Suite..."
python3 -m pip install -q -r test-harness/requirements.txt
python3 test-harness/run_simulations.py

echo ""
echo "================================================================="
echo " System running! Visit http://localhost:8000/docs for Swagger UI"
echo " Audit Ledger endpoint: http://localhost:8000/audit"
echo "================================================================="
