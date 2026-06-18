#!/bin/bash
# Usage: ./deploy.sh YOUR_EC2_IP
# Run this locally whenever you push a new image to DockerHub

EC2_IP=$1
KEY="mlops-saylani-key.pem"

if [ -z "$EC2_IP" ]; then
  echo "Usage: ./deploy.sh YOUR_EC2_IP"
  exit 1
fi

echo "==> Pushing latest images to DockerHub..."
docker push hammadasher/mlops-saylani-api:latest
docker push hammadasher/mlops-saylani-frontend:latest

echo "==> SSHing into EC2 and pulling latest images..."
ssh -i $KEY ec2-user@$EC2_IP << 'REMOTE'
  cd mlops-saylani
  docker compose pull
  docker compose up -d --remove-orphans
  docker compose ps
REMOTE

echo "==> Deployment complete!"
echo "API:      http://$EC2_IP:8000/docs"
echo "Frontend: http://$EC2_IP:8501"
