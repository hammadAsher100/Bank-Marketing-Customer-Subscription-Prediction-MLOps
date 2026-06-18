#!/bin/bash
# Script to run ON EC2 instance to build and deploy the application
# Usage: bash build-on-ec2.sh

set -e

echo "=========================================="
echo "MLOps Saylani - EC2 Build & Deploy"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "✗ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "==> Step 1: Cloning repository..."
if [ -d "MLOps-Saylani" ]; then
    echo "Repository already exists. Pulling latest changes..."
    cd MLOps-Saylani
    git pull
else
    git clone https://github.com/hammadAsher100/MLOps-Saylani.git
    cd MLOps-Saylani
fi

echo ""
echo "==> Step 2: Building Docker images..."
echo "This will take 5-10 minutes..."

# Build API image
echo "Building API image..."
docker build -f Dockerfile.api -t hammadasher/mlops-saylani-api:latest . || {
    echo "✗ API build failed"
    exit 1
}

# Build Frontend image
echo "Building Frontend image..."
docker build -f Dockerfile.frontend -t hammadasher/mlops-saylani-frontend:latest . || {
    echo "✗ Frontend build failed"
    exit 1
}

echo ""
echo "==> Step 3: Starting services..."
docker compose up -d

echo ""
echo "==> Step 4: Checking service status..."
sleep 5
docker compose ps

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Access your application:"
echo "  API:      http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000/docs"
echo "  Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose logs -f"
echo "  Stop:         docker compose down"
echo "  Restart:      docker compose restart"
echo "=========================================="
